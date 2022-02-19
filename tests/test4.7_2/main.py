from server import Broker

timeout = 8
server = Broker('broker')
server.start(timeout)