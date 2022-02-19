from server import Broker

timeout = 4
server = Broker('broker')
server.start(timeout)