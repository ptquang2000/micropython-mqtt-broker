import ujson
import btree
import _thread

from message import Message, process_utf8

LOCK = _thread.allocate_lock()

class Connect(Message):
  NAME = 6
  VERSION = 1
  FLAGS = 1
  ALIVE = 2
  PROPERTY = 1
  RESERVED = 0 
  SESSION_EXPIRY_VALUE = 3600 # MAX 0xFFFFFFFF

  def __init__(self, msg):
    super().__init__(msg._conn, msg._fixed_header)

  def handle(self):
    print()
    print('[RECEIVED CONNECT]')
    print('Packet type:', self._fixed_header[0] >> 4, 'Reserved:', self._fixed_header[0] & 15)
    # VARIABLE HEADER
    # Protocol
    protocol = self._conn.recv(Connect.NAME)
    payload = self._fixed_header[1] - Connect.NAME
    name, _ = process_utf8(protocol)
    version = self._conn.recv(Connect.VERSION)[0]
    payload -= Connect.VERSION
    print('Protocol:', name, 'Version:', version)

    # Connect Flags 
    flags = '{0:08b}'.format(self._conn.recv(Connect.FLAGS)[0])
    payload -= Connect.FLAGS
    print('Connection Flags:', flags)

    # Keep Alive
    start, end = self._conn.recv(Connect.ALIVE)
    payload -= Connect.ALIVE
    print('Interval:', start,'-', end)

    # Properties
    properties = self._conn.recv(Connect.PROPERTY)[0]
    if properties != 0:
      payload -= Connect.PROPERTY + properties
      properties = self._conn.recv(properties)
      indentifier = properties[0]
      interval = properties[1:]
      print('Identifier:', indentifier, 'Interval:', interval)

    # Payload
    flags = self.reverse(flags)
    # Client identifier
    id, _payload = process_utf8(self._conn.recv(payload))
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
      username, _payload = process_utf8(_payload)
      print('User Name:', username)

    # Password
    if flags[7] == '1':
      password, _payload = process_utf8(_payload)
      print('Password:', password)

    session = {
      'id': id.decode('utf-8'),
    }

    # Clean Start
    LOCK.acquire()
    state = self.save_session(session, flags[1] == '1')
    LOCK.release()

    buf = self.connack(clean_start=flags[1] == '1', session_state=state)
    self._conn.write(buf)
    super().handle()

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
    print()
    print('[SENT CONNACK]')
    # FIXED HEADER
    self._fixed_header = Connect.CONNACK * 16 + Connect.RESERVED
    print('Packet type:', Connect.CONNACK, 'Rserved:', Connect.RESERVED)

    # VARIABLE HEADER

    # ACKNOWLEDGE FLAG
    # Byte 1
    ackflag = Connect.RESERVED * 1

    # Session Present
    present_flag = 0
    if not clean_start and session_state:
      present_flag = 1

    # Byte 2
    reason_code = Message.SUCCESS

    # PROPERTIES
    # Property Length
    property_len = 0

    # # Session Expiry Interval
    # ssn_expiry_interval = 0
    # if session_expiry_interval != None:
    #   ssn_expiry_interval += session_expiry_interval
    # else:
    #   ssn_expiry_interval += Connect.SESSION_EXPIRY_VALUE

    # property_len += 5

    # if reason_code != Message.SUCCESS:
    #   present_flag = 0

    ackflag += present_flag
    print('Acknowledge Flag:', present_flag)
    remain = 3 + property_len
    print('Remain Length:', remain)
    buf = self._fixed_header.to_bytes(1, 'big')
    buf += remain.to_bytes(1, 'big')
    buf += ackflag.to_bytes(1, 'big') 
    buf += reason_code
    print('Connect Reason Code:', reason_code)
    buf += property_len.to_bytes(1, 'big')
    print('Property Length:', property_len)
    # buf += Message.SESSION_EXPIRY_INTERVAL
    # buf += ssn_expiry_interval.to_bytes(4, 'big')
    print(buf)
    return buf
