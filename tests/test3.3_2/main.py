from server import Broker

timeout = 10
server = Broker('broker')
server.start(timeout)