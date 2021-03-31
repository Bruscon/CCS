# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 19:16:10 2021

@author: Nick Brusco
"""
"""
import wexpect, sys, os


child = wexpect.spawn("python test.py")
child.expect("Running")
child.sendline("poop")
"""


import threading

class ThreadWorker(threading.Thread):
    def __init__(self, callable, *args, **kwargs):
        super(ThreadWorker, self).__init__()
        self.callable = callable
        self.args = args
        self.kwargs = kwargs
        self.setDaemon(True)

    def run(self):
        try:
            self.callable(*self.args, **self.kwargs)
        except:
            pass
        #except wx.PyDeadObjectError:
        #    pass
        #except Exception, e:
        #    print(e)



if __name__ == "__main__":
    import os, sys, subprocess, threading, time, pexpect
    from subprocess import Popen, PIPE

    def worker(pipe):
        while True:
            line = pipe.readline()
            if line == '': break
            else: print( line )

    #proc = Popen("wine ~/Downloads/lc0-v0.27.0-windows-cpu-dnnl/lc0.exe", universal_newlines = True, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    #proc = Popen("python3 ~/Documents/projs/CCS/comp_side/ifw.py", universal_newlines=True, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    proc = pexpect.spawn("python3 ~/Documents/projs/CCS/comp_side/ifw.py")

    proc.expect("it fuckin worked")
    proc.sendline("go nodes 100")

    breakpoint()

    time.sleep(2)
    d = proc.communicate(input = "go nodes 100")
    time.sleep(2)

    breakpoint()

    stdout_worker = ThreadWorker(worker, proc.stdout)
    stderr_worker = ThreadWorker(worker, proc.stderr)
    stdout_worker.start()
    stderr_worker.start()
    

    while True: 
        time.sleep(1)
        proc.stdin.write("go nodes 100")
        breakpoint()
