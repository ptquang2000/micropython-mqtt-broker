import sys
import server as sv

broker = sv.Broker(sys.argv[1])
broker.start(3)
broker.start()