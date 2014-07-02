#!/usr/bin/env python
#coding:utf8
#date 2014.06.03
#author:finy
#import profile
from core import pyshell
from core import cmdline


if __name__ == '__main__':
    finy = cmdline.process()
    #profile.run('finy.main()')
    finy.main()
