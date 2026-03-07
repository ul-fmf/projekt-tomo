import multiprocessing
#multiprocessing.set_start_method('spawn')
from multiprocessing import Process, Queue, JoinableQueue, Event

from time import time

import os

class PipedMemorySend:    

    def __init__(self, _out, lock, **kwargs):
        super(PipedMemorySend, self).__init__()
        self._args = kwargs
        self._out = _out
        self.__lock = lock
        
    def __setattr__(self, attr, value):
        if attr != "_args" and attr in self._args:
            self._args[attr] = value
            #print(os.getpid(), "SEND", attr, value)
            self._out.put((attr, value))
        else:
            super().__setattr__(attr, value)

    def __getattr__(self, attr):
        #print(os.getpid(), "send", attr)
        if attr != "_args" and attr in self._args:
            return self._args[attr]
        raise AttributeError("Attribute: {0} does not exist.")
    
    def aquire(self):
        self.__lock.clear()

    def release(self):
        self.__lock.set()

class PipedMemoryReceive:    

    def __init__(self, _in, lock, **kwargs):
        super(PipedMemoryReceive, self).__init__()
        self._in = _in
        self._args = kwargs
        self.__lock = lock

    def __getattr__(self, attr):
        #print(os.getpid(), "receive", attr)
        if attr != "_args" and attr in self._args:
            #this allows the sender to block the receiver while it prepares attributes
            #obviously this might go bad if the sender process dies... TODO come up with a better solution for this
            self.__lock.wait()
            while not self._in.empty():
                k,v = self._in.get()
                self._args[k] = v
            return self._args[attr]
        raise AttributeError("Attribute: {0} does not exist.")

def PipedMemory(**kwargs):
    q = Queue()
    lock =  Event()
    return PipedMemorySend(q, lock, **kwargs), PipedMemoryReceive(q, lock, **kwargs)