import sys
from time import sleep, time
import server as sv
import _thread
def func():
    count = -5
    while count < 35:
        print(abs(count))
        count +=1
        sleep(1)
_thread.start_new_thread(func, ())
broker = sv.Broker(sys.argv[1])
sleep(5)
broker.start(10)
sleep(10)
broker.start(10)