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
  header = conn.recv(FIXED_HEADER)
  print('Packet type:', header[0] >> 4, 'Flag:', header[0] & 15)
  if header[0] >> 4 == TYPE:
    # Variable Header
    protocol = conn.recv(NAME)
    payload = header[1] - NAME
    LSB = protocol[0]
    MSB = protocol[1]
    name = protocol[LSB+OFFSET:MSB+OFFSET].decode('utf-8')
    version = conn.recv(VERSION)[0]
    payload -= VERSION
    print('Protocol:', name, version)
    flags = '{0:08b}'.format(conn.recv(FLAGS)[0])
    payload -= FLAGS
    print('Connection Flags:', flags)
    start, end = conn.recv(ALIVE)
    payload -= ALIVE
    print('Interval:', start,'-', end)
    properties = conn.recv(PROPERTY)[0]
    if properties != 0:
      payload -= PROPERTY + properties
      properties = conn.recv(properties)
      indentifier = properties[0]
      interval = properties[1:]
      print('Identifier:', indentifier, 'Interval:', interval)
    payload = conn.recv(payload)
    print('Payload:')
    print(payload)
    print('------------------------')
