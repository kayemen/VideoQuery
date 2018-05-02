import threading
import time

def f1():
    print(a)
    print("started 1")
    tic = time.time()
    time.sleep(3)
    print("ended 1-",time.time()-tic)
    return 3

def f2():
    print("started 2")
    tic = time.time()
    time.sleep(5)
    print("ended 2-",time.time()-tic)

a=100
# f1()
# f2()
t1 = threading.Thread(target=f1, args=())
t2 = threading.Thread(target=f2, args=())

tic = time.time()
t1.start()
t2.start()

t1.join()
print("T1", time.time()-tic)
t2.join()
print("T2", time.time()-tic)