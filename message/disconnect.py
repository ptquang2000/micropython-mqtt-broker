from message import Message

class Disconnect(Message):
  def __init__(self, msg):
    super().__init__(msg._conn, msg._fixed_header)
    self._session_expiry_interval = None
  
  def handle(self):
    print()
    # Fixed header
    print('[RECEIVED DISCONNECT]')
    print('Packet type:', self._fixed_header[0] >> 4,'Reserved:', self._fixed_header[0] & 15)
    variable_header = self._fixed_header[1]
    # VARIABLE HEADER
    if variable_header < 1:
      print('Reason Code:', Message.NORMAL_DISCONNECT)      
    # Reason Code
    elif variable_header < 2:
      variable_header = self._conn.recv(variable_header)
      reason_code = variable_header[0]
      print('Reason Code:', reason_code)

    # Property
    else:
      property_len = self._conn.recv(1)
      property = self._conn.recv(property_len)
      i = 0
      try:
        if property[i] == Message.SESSION_EXPIRY_INTERVAL:
          i += 1
          self._session_expiry_interval = property[i:i+4]
          i += 4
          if self._session_expiry_interval.from_bytes('big') == 0:
            pass
      
        if property[i] == Message.REASON_STRING:
          i += 1
        if property[i] == Message.REASON_STRING:
          pass

        if property[i] == Message.USER_PROPERTY:
          i += 1
          remain = property[i:]
          while remain[0] != Message.SERVER_REFERENCE:
            name, remain = process_utf8(remain)
            i += 2 + len(name)
            value, remain = process_utf8(remain)
            i += 2 + len(value)
        
        if property[i] == Message.SERVER_REFERENCE:
          i += 1
        if property[i] == Message.SERVER_REFERENCE:
          pass
          
      except IndexError:
        pass