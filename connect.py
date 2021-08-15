import usocket
import _thread
import ujson
import btree

SEI_ID = 17

### CONNECT ####################################################################

CONNECT = 1
FIXED_HEADER = 2
NAME = 6
OFFSET = 2
VERSION = 1
FLAGS = 1
ALIVE = 2
PROPERTY = 1
LOCK = _thread.allocate_lock()

def connect(conn, addr):
  print('----- [NEW CONNECTION]', str(addr[0]), str(addr[1]),'-----')

  # Fix header
  header = conn.recv(FIXED_HEADER)
  if header[0] >> 4 == CONNECT:
    print('Packet type:', header[0] >> 4, 'Reserved:', header[0] & 15)
    # Variable Header

    # Protocol
    protocol = conn.recv(NAME)
    payload = header[1] - NAME
    LSB = protocol[0]
    MSB = protocol[1]
    name = protocol[LSB+OFFSET:MSB+OFFSET]
    version = conn.recv(VERSION)[0]
    payload -= VERSION
    print('Protocol:', name, 'Version:', version)

    # Connect Flags 
    flags = '{0:08b}'.format(conn.recv(FLAGS)[0])
    payload -= FLAGS
    print('Connection Flags:', flags)

    # Keep Alive
    start, end = conn.recv(ALIVE)
    payload -= ALIVE
    print('Interval:', start,'-', end)

    # Properties
    properties = conn.recv(PROPERTY)[0]
    if properties != 0:
      payload -= PROPERTY + properties
      properties = conn.recv(properties)
      indentifier = properties[0]
      interval = properties[1:]
      print('Identifier:', indentifier, 'Interval:', interval)

    # Payload
    flags = reverse(flags)
    # Client identifier
    id, _payload = process_utf8(conn.recv(payload))
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
    state = save_session(session, flags[1] == '1')
    LOCK.release()

    print('---------- Sending CONNACK ----------')
    buf = connack(clean_start=flags[1] == '1', session_state=state)
    conn.write(buf)

################################################################################

def reverse(s):
  return '' if not s else reverse(s[1:]) + s[0] 

def process_utf8(payload):
  LSB = payload[0]
  MSB = payload[1]
  return payload[LSB+OFFSET:MSB+OFFSET], payload[MSB+OFFSET:] 

def save_session(session, clean_start):
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

### CONNACK ####################################################################

CONNACK = 2 
RESERVED = 0 
# Reason Code
SUCCESS = 0
UNSPECIFIED_ERROR = 128
MALFORMED_PACKET = 129
PROTOCOL_ERROR = 130
IMPLEMENT_SPECIFIC_ERROR = 131
UNSUPPORTED_PROTOCOL_VERSION = 132

SEI_DVALUE = 3600 # MAX 0xFFFFFFFF

def connack(clean_start, session_state=None, session_expiry_interval=None):

  # FIXED HEADER
  header = CONNACK * 16 + RESERVED

  # VARIABLE HEADER

  # ACKNOWLEDGE FLAG
  # Byte 1
  ackflag = RESERVED * 1

  # Session Present
  present_flag = 0
  if not clean_start and session_state:
    present_flag = 1

  # Byte 2
  reason_code = SUCCESS

  # PROPERTIES
  # Property Length
  property_len = 0

  # Session Expiry Interval
  ssn_expiry_interval = 0
  if session_expiry_interval != None:
    ssn_expiry_interval += session_expiry_interval
  else:
    ssn_expiry_interval += SEI_DVALUE

  property_len += 5

  if reason_code != SUCCESS:
    present_flag = 0

  ackflag += present_flag
  remain = 3 + property_len
  buf = header.to_bytes(1, 'big')
  buf += remain.to_bytes(1, 'big')
  buf += ackflag.to_bytes(1, 'big') 
  buf += reason_code.to_bytes(1, 'big')
  buf += property_len.to_bytes(1, 'big')
  buf += SEI_ID.to_bytes(1, 'big')
  buf += ssn_expiry_interval.to_bytes(4, 'big')
  print(buf)
  return buf

  




  


    