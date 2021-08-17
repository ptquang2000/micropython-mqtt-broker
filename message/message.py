import usocket
import _thread
import ujson
import btree

OFFSET = 2

class message():
  # Reason Code
  SUCCESS = 0
  UNSPECIFIED_ERROR = 128
  MALFORMED_PACKET = 129
  PROTOCOL_ERROR = 130
  IMPLEMENT_SPECIFIC_ERROR = 131
  UNSUPPORTED_PROTOCOL_VERSION = 132

  def __init__(self, conn) -> None:
    self._conn = conn
    self._header = None

  @property
  def type(self): 
    self._header = self._conn.recv(2)
    message_type = self._header[0] >> 4
    return message_type

  def reverse(self,s):
    return '' if not s else self.reverse(s[1:]) + s[0] 

  @staticmethod
  def process_utf8(payload):
    LSB = payload[0]
    MSB = payload[1]
    return payload[LSB+OFFSET:MSB+OFFSET], payload[MSB+OFFSET:] 

  def process_utf8(self):
    LSB = self._conn.recv(1)[0]
    MSB = self._conn.recv(1)[0]
    return self._conn.recv(MSB + LSB)


LOCK = _thread.allocate_lock()


class connect(message):
  NAME = 6
  VERSION = 1
  FLAGS = 1
  ALIVE = 2
  PROPERTY = 1

  CONNACK = 2 
  RESERVED = 0 
  SESSION_EXPIRY_VALUE = 3600 # MAX 0xFFFFFFFF
  SESSION_EXPIRY_ID = 17

  def __init__(self, msg):
    super().__init__(msg._conn)

  def handle(self):
    print()
    print('Packet type:', self._header[0] >> 4, 'Reserved:', self._header[0] & 15)
    # VARIABLE HEADER
    # Protocol
    protocol = self._conn.recv(connect.NAME)
    payload = self._header[1] - connect.NAME
    name, _ = self.process_utf8(protocol)
    version = self._conn.recv(connect.VERSION)[0]
    payload -= connect.VERSION
    print('Protocol:', name, 'Version:', version)

    # Connect Flags 
    flags = '{0:08b}'.format(self._conn.recv(connect.FLAGS)[0])
    payload -= connect.FLAGS
    print('Connection Flags:', flags)

    # Keep Alive
    start, end = self._conn.recv(connect.ALIVE)
    payload -= connect.ALIVE
    print('Interval:', start,'-', end)

    # Properties
    properties = self._conn.recv(connect.PROPERTY)[0]
    if properties != 0:
      payload -= connect.PROPERTY + properties
      properties = self._conn.recv(properties)
      indentifier = properties[0]
      interval = properties[1:]
      print('Identifier:', indentifier, 'Interval:', interval)

    # Payload
    flags = self.reverse(flags)
    # Client identifier
    id, _payload = self.process_utf8(self._conn.recv(payload))
    print('Client ID', id)

    # Will Properties
    if flags[2] == '1':
      pass

      # Will Topic
      if flags[3] == '1':
        pass

      # Will Payload
      if flags[4] == '1':
        pass

      # Will retain
      if flags[5] == '1':
        pass

    # User Name
    if flags[6] == '1':
      username, _payload = self.process_utf8(_payload)
      print('User Name:', username)

    # Password
    if flags[7] == '1':
      password, _payload = self.process_utf8(_payload)
      print('Password:', password)

    session = {
      'id': id.decode('utf-8'),
    }

    # Clean Start
    LOCK.acquire()
    state = self.save_session(session, flags[1] == '1')
    LOCK.release()

    print('---------- Sending CONNACK ----------')
    buf = self.connack(clean_start=flags[1] == '1', session_state=state)
    self._conn.write(buf)
    print('-------------------------------------')
    print()

  def save_session(self, session, clean_start):
    state = False
    try:
      f = open("session", "r+b")
    except OSError:
      f = open("session", "w+b")
    db = btree.open(f)
    key = session['id'].encode()
    value =  ujson.dumps(session).encode()
    if clean_start:
      if key in db:
        del db[key]
      db[key] = value
    else:
      if key not in db:
        db[key] = value
      else:
        state = True
    print('Session:',db[key])
    db.flush()
    db.close()
    f.close()
    return state

  def connack(self, clean_start, session_state=None, session_expiry_interval=None):
    # FIXED HEADER
    self._header = connect.CONNACK * 16 + connect.RESERVED

    # VARIABLE HEADER

    # ACKNOWLEDGE FLAG
    # Byte 1
    ackflag = connect.RESERVED * 1

    # Session Present
    present_flag = 0
    if not clean_start and session_state:
      present_flag = 1

    # Byte 2
    reason_code = message.SUCCESS

    # PROPERTIES
    # Property Length
    property_len = 0

    # Session Expiry Interval
    ssn_expiry_interval = 0
    if session_expiry_interval != None:
      ssn_expiry_interval += session_expiry_interval
    else:
      ssn_expiry_interval += connect.SESSION_EXPIRY_VALUE

    property_len += 5

    if reason_code != message.SUCCESS:
      present_flag = 0

    ackflag += present_flag
    remain = 3 + property_len
    buf = self._header.to_bytes(1, 'big')
    buf += remain.to_bytes(1, 'big')
    buf += ackflag.to_bytes(1, 'big') 
    buf += reason_code.to_bytes(1, 'big')
    buf += property_len.to_bytes(1, 'big')
    buf += connect.SESSION_EXPIRY_ID.to_bytes(1, 'big')
    buf += ssn_expiry_interval.to_bytes(4, 'big')
    print(buf)
    return buf

class publish(message):
  def __init__(self, msg):
    super().__init__(msg._conn)
    self._payload_format_indicator = None
    self._message_expiry_interval = None
    self._topic_alias_value = None

  def handle(self):
    print()
    # Fixed header
    print('Packet type:', self._header[0] >> 4)
    DUP_flag = self._header[0] & 12
    print('DUP:', DUP_flag)
    QoS = self._header[0] & 10 
    print('QoS:', QoS)
    if QoS == 3:
      # TODO
      pass
    retain = self._header[0] & 1
    print('Retain:', retain)
    if retain == 1:
      # TODO
      pass

    # byte 2 = Remain length             [7:0]
    payload_len = self._header[1]

    # VARIABLE HEADER
    # Topic name
    topic_name = self.process_utf8()
    print('Topic:', topic_name)

    # Packet Identifier
    if QoS != 0:
      pass

    # PROPERTIES
    # Property length
    property_len = self._conn.recv(1)[0]
    if property_len != 0: 
      property = self._conn.recv(property_len)
      i = 0

      # Payload format indicator
      if not i > property_len and property[i] == b'\x01':
        i += 1
        self._payload_format_indicator = property[i][0]
        i += 1
      
      # Message Expiry Interval
      if not i > property_len and property[i] == b'\x02':
        i += 1
        self._message_expiry_interval = int.from_bytes(property[i:i+4], 'big')
        i += 4 

      # Topic Alias
      if not i > property_len and property[i] == b'\x23':
        i += 1
        self._topic_alias_value = property[i:i+2]
        i += 2