from server import Broker

timeout = 6
server = Broker('broker')
server.start(timeout)