
from message import Message, process_utf8

class Publish(Message):
  def __init__(self, msg):
    super().__init__(msg._conn, msg._fixed_header)
    self.packet_id = None
    self._payload_format_indicator = None
    self._message_expiry_interval = None
    self._topic_alias_value = None
    self._subcription_id = None
  
  def handle(self):
    print()
    # Fixed header
    print('[RECEIVED PUBLISH]')
    print('Packet type:', self._fixed_header[0] >> 4)
    DUP_flag = self._fixed_header[0] & 12
    print('DUP:', DUP_flag)
    QoS = self._fixed_header[0] & 10 
    print('QoS:', QoS)
    if QoS == 3:
      # TODO
      pass
    retain = self._fixed_header[0] & 1
    print('Retain:', retain)
    if retain == 1:
      # TODO
      pass

    # byte 2 = Remain length             [7:0]
    payload = self._fixed_header[1]

    # VARIABLE HEADER
    # Topic name
    topic_name = super().process_utf8()
    print('Topic:', topic_name)
    payload -= 2 + len(topic_name) 

    # Packet Identifier
    if QoS != 0:
      self.packet_id = self._conn.recv(2)
      print('Packet Identifier:', self.packet_id)
      payload -= 2

    # PROPERTIES
    # Property length
    property_len = self._conn.recv(1)[0]
    payload -= 1
    if property_len != 0: 
      property = self._conn.recv(property_len)
      i = 0

      try:
        # Payload format indicator
        if property[i] == Message.PAYLOAD_FORMAT_INDICATOR:
          i += 1
          self._payload_format_indicator = property[i][0]
          i += 1
        
        # Message Expiry Interval
        if property[i] == Message.MESSAGE_EXPIRY_INTERVAL:
          i += 1
          self._message_expiry_interval = int.from_bytes(property[i:i+4], 'big')
          i += 4 

        # Topic Alias
        if property[i] == Message.TOPIC_ALIAS:
          i += 1
          self._topic_alias_value = property[i:i+2]
          i += 2
        if property[i] == Message.TOPIC_ALIAS:
          # TODO
          pass
        
        # Response Topic
        if property[i] == Message.RESPONSE_TOPIC:
          i += 1
          pass
        if property[i] == Message.RESPONSE_TOPIC:
          # TODO
          pass

        # Correlation Data 
        if property[i] == Message.CORRELATION_DATA:
          i += 1
          pass
        if property[i] == Message.CORRELATION_DATA:
          # TODO
          pass

        # User Properties
        if property[i] == Message.USER_PROPERTY:
          i += 1          
          remain = property[i:]
          while remain[0] != Message.SUBSCRIPTION_IDENTIFIER:
            name, remain = process_utf8(remain)
            i += 2 + len(name)
            value, remain = process_utf8(remain)
            i += 2 + len(value)

        # Subcription Identifier
        if property[i] == Message.SUBSCRIPTION_IDENTIFIER:
          i += 1
          self._subcription_id = property[i]
          i += 1

        # Content Type 
        if property[i] == Message.CONTENT_TYPE:
          i += 1
          self._content_type, _ = process_utf8(property[i])
          i += 1

      except IndexError:
        pass

    payload -= property_len
    if payload == 0:
      pass
    payload = self._conn.recv(payload)
    print('Payload:',payload)