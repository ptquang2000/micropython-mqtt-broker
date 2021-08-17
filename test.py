import time
import _thread

lock = _thread.allocate_lock()
my_list = []

def add(count):
  lock.acquire()
  my_list[count] = count
  lock.release()

def append():
  count = 0
  while True:
    time.sleep(2)
    lock.acquire()
    my_list.append(0)
    lock.release()
    _thread.start_new_thread(add, (count,))
    count += 1

def print_list():
  count = len(my_list)
  while True: 
    if (x:=len(my_list)) != count:
      print(my_list)
      count = x 


_thread.start_new_thread(append, ())
_thread.start_new_thread(print_list, ())