from server import Broker

timeout = 7
server = Broker('broker')
server.start(timeout)