import threading
import time
import tkinter as tk


class A:
    def __init__(self):
        self.root =
        self.t = threading.Thread(target=self.test, args=())
        self.e = threading.Event()

        self.t.start()

    def test(self):
        count = 0
        print('start')
        print(self.e.is_set())
        while not self.e.is_set():
            time.sleep(0.1)
            print(count)
            count += 1

    def close(self):
        self.e.set()


a = A()
time.sleep(3)
a.close()


class TestThread(threading.Thread):
    def __init__(self, name='TestThread'):
        """ constructor, setting initial variables """
        self._stopevent = threading.Event()
        self._sleepperiod = 1.0
        threading.Thread.__init__(self, name=name)

    def run(self):
        """ main control loop """
        print("%s starts" % (self.getName(),))
        count = 0
        while not self._stopevent.isSet():
            count += 1
            print("loop %d" % (count,))
            self._stopevent.wait(self._sleepperiod)
        print("%s ends" % (self.getName(),))

    def join(self, timeout=None):
        """ Stop the thread and wait for it to end. """
        self._stopevent.set()
        super().join(timeout)


# if __name__ == "__main__":
#     testthread = TestThread()
#     testthread.start()
#     import time
#     time.sleep(5.0)
#     testthread.join()
