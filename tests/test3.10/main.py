from server import Broker

timeout = 14
server = Broker('broker')
server.start(timeout)