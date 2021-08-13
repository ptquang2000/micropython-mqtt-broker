import usocket

TYPE = 1
FIXED_HEADER = 2
NAME = 6
OFFSET = 2
VERSION = 1
FLAGS = 1
ALIVE = 2
PROPERTY = 1

def connect(conn, addr):
  print('[NEW CONNECTION]', str(addr[0]), str(addr[1]))

  # Fix header
  header = conn.recv(FIXED_HEADER)
  print('Packet type:', header[0] >> 4, 'Reserved:', header[0] & 15)

  if header[0] >> 4 == TYPE:
    # Variable Header

    # Protocol
    protocol = conn.recv(NAME)
    payload = header[1] - NAME
    LSB = protocol[0]
    MSB = protocol[1]
    name = protocol[LSB+OFFSET:MSB+OFFSET].decode('utf-8')
    version = conn.recv(VERSION)[0]
    payload -= VERSION
    print('Protocol:', name, version)

    # Connect Flags 
    flags = '{0:08b}'.format(conn.recv(FLAGS)[0])
    payload -= FLAGS
    print('Connection Flags:', flags)

    # Clean Start
    # TO-DO Check session state

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

    process_payload(conn.recv(payload), reverse(flags))

    print('-----------------------------------')

def reverse(s):
  return '' if not s else reverse(s[1:]) + s[0] 

def process_payload(payload, flag):

  # Client ID
  ClientID, _payload = process_prefix(payload)
  print('Client ID', ClientID)

  # Will Properties
  if flag[2] == '1':
    pass

    # Will Topic
    if flag[3] == '1':
      pass

    # Will Payload
    if flag[4] == '1':
      pass

    # Will retain
    if flag[5] == '1':
      pass

  # User Name
  if flag[6] == '1':
    username, _payload = process_prefix(_payload)
    print('User Name:', username)

  # Password
  if flag[7] == '1':
    password, _payload = process_prefix(_payload)
    print('Password:', password)


def process_prefix(payload):
  LSB = payload[0]
  MSB = payload[1]
  return payload[LSB+OFFSET:MSB+OFFSET], payload[MSB+OFFSET:] 