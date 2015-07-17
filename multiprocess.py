__author__ = 'wwagner'

from multiprocessing import Process, Queue, Pipe, Lock
import os

def info(title):
    print(title)
    print("module name: ", __name__)
    if hasattr(os, 'getppid'):
        print('parent process: ', os.getppid())
    print('process id: ', os.getpid())

def mp_example(name):
    info('function f')
    print('hello', name)

def queue_example(q):
    q.put([42, None, 'hello'])

def pipe_example(conn):
    conn.send([42, None, 'hello'])
    conn.close()

def lock_example(lock, number):
    lock.acquire()
    print('Hello, World ', number)
    lock.release()


if __name__ == '__main__':
    ''' Basic Multiprocessing'''
    # info('main line')
    # p = Process(target=mp_example, args=('bob',))
    # p.start()
    # p.join()

    ''' Multiprocessing with Queue '''
    # q = Queue()
    # p = Process(target=queue_example, args=(q, ))
    # p.start()
    # print(q.get())
    # p.join()

    ''' Multiprocessing with Pipe '''
    # parent_conn, child_conn = Pipe()
    # p = Process(target=pipe_example, args=(child_conn,))
    # p.start()
    # print(parent_conn.recv())
    # p.join()

    ''' Multiprocessing with Lock '''
    lock = Lock()

    for num in range(10):
        Process(target=lock_example, args=(lock, num)).start()