from server.format import *
from server.property import *

# Packet type
RESERVED = 0
CONNECT = 1
CONNACK = 2 
PUBLISH = 3
SUBCRIBE = 8
PINGREQ = 12
PINGRESP = 13
DISCONNECT = 14

# Reason Code
SUCCESS = b'\x00'
NORMAL_DISCONNECT = b'\x00' 
UNSPECIFIED_ERROR = b'\x80'
MALFORMED_PACKET = b'\x81'
PROTOCOL_ERROR = b'\x82'
IMPLEMENT_SPECIFIC_ERROR = b'\x83'
UNSUPPORTED_PROTOCOL_VERSION = b'\x84'

# Packet type translator
PACKET_TRANS = {
    RESERVED: 'RESERVED',
    CONNECT: 'CONNECT',
    CONNACK: 'CONNACK',
    PUBLISH: 'PUBLISH',
    SUBCRIBE: 'SUBCRIBE',
    PINGREQ: 'PINGREQ',
    PINGRESP: 'PINGRESP',
    DISCONNECT: 'DISCONNECT',
    }
def connect_strategy(packet, buf):
  # Variable header
  name, buf = utf8_encoded_string(buf)
  packet.variable_header.update({'protocol_name': name})

  ver, buf = buf[0], buf[1:]
  packet.variable_header.update({'protocol_version': ver})

  flags, buf = '{0:08b}'.format(buf[0]), buf[1:]
  packet.variable_header.update({
    'username_flag': flags[0],
    'password_flag': flags[1],
    'will_retain': flags[2],
    'will_QoS': flags[3:5],
    'will_flag': flags[5],
    'clean_start': flags[6],
    'reserved': flags[7]
    })

  keep_alive, buf = buf[0:2], buf[2:]
  packet.variable_header.update({'keep_alive': int.from_bytes(keep_alive, 'big')})

  property_length, buf = variable_byte_integer(buf)
  packet.variable_header.update({'property_length': property_length})
  if property_length != 0:
    pass

  # Payload
  client_id, buf = utf8_encoded_string(buf)
  packet.payload.update({'client_id': client_id})

  if packet.will_flag == 1:
    property_length, buf = variable_byte_integer(buf)
    packet.payload.update({'property_length': property_length})

    properties = Properties(buf=buf, max_length=property_length)
    packet.payload.update(properties.will_properties)

    will_topic, buf = utf8_encoded_string(buf)
    packet.payload.update({'will_topic': will_topic})

    will_payload, buf = utf8_encoded_string(buf)
    packet.payload.update({'will_payload': will_payload})

  if packet.username_flag == '1':
    username, buf = utf8_encoded_string(buf)
    packet.payload.update({'username': username})
  if packet.password_flag == '1':
    password, buf = utf8_encoded_string(buf)
    packet.payload.update({'password': password})

def connack_strategy(packet):
  conn_ack_flags = RESERVED
  reason_code = SUCCESS

  property_length = variable_byte_integer(0)
  if packet.clean_start == 0 and reason_code == SUCCESS:
    conn_ack_flags |= 1

  buf = conn_ack_flags.to_bytes(1, 'big')
  buf += reason_code
  buf += property_length
  return buf

def publish_strategy(packet, buf):
  topic, buf = utf8_encoded_string(buf)
  packet.variable_header.update({'topic': topic})

  if packet.QoS_level == 0:
    packet_id, buf = buf[0:2], buf[2:]

  property_length, buf = variable_byte_integer(buf)
  packet.variable_header.update({'property_length': property_length})

  if property_length != 0:
    pass
  packet.payload.update({'application_message': buf})

  # process topic storage
  topic = Topic(packet.topic_storage)
  topic[packet.topic] = packet.p_application_message

class Topic():
  def __init__(self, topic):
    self.topic = topic

  def __setitem__(self, filters, app_msg):
    topic_filters = str(filters).split('/')
    topic = self.topic
    for topic_filter in topic_filters[:-1]:
      try:
        if not isinstance(topic[topic_filter], dict):
          raise KeyError
        topic = topic[topic_filter]
      except KeyError:
        topic.update({topic_filter: dict()})
        topic = topic[topic_filter]
    topic.update({topic_filters[-1]: app_msg})

def subcribe_strategy(packet, buf):
  pass

def disconnect_strategy(packet, buf):
  if len(buf) < 1:
    rc = NORMAL_DISCONNECT
    packet.variable_header.update({'reason_code': rc})
  elif len(buf) < 2:
    rc = buf[1]
    packet.variable_header.update({'reason_code': rc})
  else:
    properties, buf = buf[1], buf[2:]
    i = 0
    try:
      if property[i] == SESSION_EXPIRY_INTERVAL:
        i += 1
        self._session_expiry_interval = property[i:i+4]
        i += 4
        if self._session_expiry_interval.from_bytes('big') == 0:
          pass
        if property[i] == REASON_STRING:
          i += 1
        if property[i] == REASON_STRING:
          pass
        if property[i] == USER_PROPERTY:
          i += 1
          remain = property[i:]
          while remain[0] != SERVER_REFERENCE:
            name, remain = utf8_encoded_string(remain)
            i += 2 + len(name)
            value, remain = utf8_encoded_string(remain)
            i += 2 + len(value)

        if property[i] == SERVER_REFERENCE:
          i += 1
        if property[i] == SERVER_REFERENCE:
          pass
    except IndexError:
      pass
  packet.payload.update({'': None})

class Packet():
  def __init__(self, buf, topics=None):
    self.packet_type = buf[0] >> 4
    self.flags = buf[0] & 15
    self.remain_length = 0 
    self.variable_header = dict()
    self.payload = dict()
    self.topic_storage = topics

  def __str__(self):
    out = '\n-- [{0}]'.format(PACKET_TRANS[self.packet_type])
    out += '\n-- [Fixed Header]'
    out += '\n\tpacket type: {0} \tflags: {1:04b}'.format(
        self.packet_type , self.flags)
    out += '\n-- [Variable Header]'
    for key, val in self.variable_header.items():
      out += '\n\t{0}: \t{1}'.format(key.replace('_', ' '), val)    
    out += '\n-- [Payload]'
    for key, val in self.payload.items():
      out += '\n\t{0}: \t{1}'.format(key.replace('_', ' '), val)    
    return out

  def __getattr__(self, attr):
    try:
      if str(attr)[0:2] == 'p_':
        return self.payload[str(attr)[2:]]
      return self.variable_header[str(attr)]
    except KeyError:
      if self.packet_type == PUBLISH:
        flags = '{0:04b}'.format(self.flags)
        attr = str(attr)
        if attr == 'DUP_flag':
          return flags[0]
        if attr == 'QoS_level':
          return flags[1:3]
        if attr == 'retain':
          return flags[3]
      else:
        raise AttributeError('Packet does not have "{0}" attribute'.format(attr))

  @property
  def strategy(self):
    if CONNECT == self.packet_type:
      return connect_strategy
    elif PUBLISH == self.packet_type:
      return publish_strategy
    elif DISCONNECT == self.packet_type:
      return disconnect_strategy
    else:
      raise AttributeError('Packet type strategy not available')

  @property
  def response_strategy(self):
    if CONNECT == self.packet_type:
      return connack_strategy(self), CONNACK, RESERVED
    else:
      raise ValueError('Response action not available')

  @property
  def response_packet(self):
    try:
      response, packet_type, flags = self.response_strategy
    except ValueError:
      return None
    byte1 = (packet_type << 4 | flags).to_bytes(1, 'big')
    remain_length = len(response)
    byte2 = variable_byte_integer(remain_length)
    return byte1 + byte2 + response

  def __lshift__(self, conn):
    self.remain_length, buf = variable_byte_integer(conn)
    self.strategy(self, buf)
    return self.response_packet
