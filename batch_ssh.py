#!/usr/bin/env python
#coding:utf8
#date 2014.06.03
#author:finy
#mail jos666@qq.com
#import profile
from core.cmdline import cmdline_process
import os
import signal

def __signal_handler(signal, frame):
    os.kill(os.getpid(), 9)



if __name__ == '__main__':
    #signal.signal(signal.SIGINT, __signal_handler)
    finy = cmdline_process()
    finy.run()
