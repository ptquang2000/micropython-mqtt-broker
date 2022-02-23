from time import sleep, time
from server import Broker

broker = Broker('broker')
broker.start(4)
sleep(2)
broker.start(22)