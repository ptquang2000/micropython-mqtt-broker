import _thread

import message

def process_utf8(payload):
  OFFSET = 2
  LSB = payload[0]
  MSB = payload[1]
  return payload[LSB+OFFSET:MSB+OFFSET], payload[MSB+OFFSET:] 

class Message():
  count = 0

  # Packet Type
  CONNECT = 1
  CONNACK = 2 
  PUBLISH = 3
  DISCONNECT = 14 

  # Reason Code
  SUCCESS = b'\x00'
  NORMAL_DISCONNECT = b'\x00' 
  UNSPECIFIED_ERROR = b'\x80'
  MALFORMED_PACKET = b'\x81'
  PROTOCOL_ERROR = b'\x82'
  IMPLEMENT_SPECIFIC_ERROR = b'\x83'
  UNSUPPORTED_PROTOCOL_VERSION = b'\x84'

  # Identifier
  PAYLOAD_FORMAT_INDICATOR = b'\x01'
  MESSAGE_EXPIRY_INTERVAL = b'\x02'
  CONTENT_TYPE = b'\x03'
  RESPONSE_TOPIC = b'\x08'
  CORRELATION_DATA = b'\x09'
  SESSION_EXPIRY_INTERVAL = b'\x11' 
  SUBSCRIPTION_IDENTIFIER = b'\x0b'
  SERVER_REFERENCE = b'\x1c'
  REASON_STRING = b'\x1f'
  TOPIC_ALIAS = b'\x23'
  USER_PROPERTY = b'\x26'

  def __init__(self, conn, header=None):
    self._conn = conn
    self._fixed_header = header

  @property
  def type(self): 
    self._fixed_header = self._conn.recv(2)
    message_type = self._fixed_header[0] >> 4
    return message_type

  def reverse(self,s):
    return '' if not s else self.reverse(s[1:]) + s[0]

  def process_utf8(self):
    LSB = self._conn.recv(1)[0]
    MSB = self._conn.recv(1)[0]
    return self._conn.recv(MSB + LSB)
  
  def __call__(self):
    _thread.start_new_thread(self.handle, ())
    Message.count += 1

  def handle(self):
    while True:
      msg = self.type
      if msg == Message.CONNECT:
        _ = message.Connect(self).handle()
        self._conn.close()
        break
      elif msg == Message.PUBLISH:
        _ = message.Publish(self).handle()
      elif msg == Message.DISCONNECT:
        _ = message.Disconnect(self).handle()
        break
        