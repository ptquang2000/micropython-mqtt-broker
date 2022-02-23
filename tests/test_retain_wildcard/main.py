from server import Broker

timeout = 12
server = Broker('broker')
server.start(timeout)