#!/usr/bin/env python
#coding: utf8
#author: finy
'''
this testcase is test core.terminal function
Run: python test/testterminal.py
'''
import unittest
import sys
import os

dirname = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, dirname)
try:
    from core.terminal import Terminal
except:
    print __doc__
    exit(1)


class Terminaltest(unittest.TestCase):
    def setUp(self):
        self.ip = '127.0.0.1'
        self.user = 'finy'
        self.passwd = '123456'
        from os import environ
        homedir = environ['HOME']
        self.known_file = '%s/.ssh/known_hosts' % homedir
        self.failkey = '%s ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAyEHc' % (
            self.ip) + \
            'wyrvDncFYTmsKebcX9fWqiFxwLCVoubPGLF7Ynr7SVoOZREKXNLr2Ai1N7' + \
            've+OcYOyy1JStfmXHmy9HHEr5DJ6I7G+fk9wGLEIWGJDfOKyCU8WtVHP7m' + \
            'yW/yznDQztJDHwZyKYZaHBubF/igL6bYrpbLnTmvVjHzST9pZ+JYNIH6Mk' + \
            'Lnoqm9wYEBHLdlF3l8X3PO0kV/cNt3Runi8bbP50+YAir8XzgJFvunbshN' + \
            'A5dqFqRTQOnAoUAZaRM7QMWo2h73nWkTjmv/tM/DFr4FWfTTh7wmjT1fek' + \
            'SiQH1JiQnErYKOsQBEzOLDBqFdC+wBMXLkEHuYjzUN9/ZO2w== \n'
        self.clear_fail_key(self.ip)
        self.add_fail_key()

    def login(self, ip=None, user=None, passwd=None):
        if not ip:
            ip = self.ip
        if not user:
            user = self.user
        if not passwd:
            passwd = self.passwd
        return Terminal(ip, user, passwd, timeout=5)

    def add_fail_key(self):
        fd = open(self.known_file, 'a')
        fd.write(self.failkey)
        fd.close()

    def clear_fail_key(self, ip=None):
        from os import popen
        if not ip:
            ip = self.ip
        popen("sed -i '/%s/d' %s" % (ip, self.known_file))

    def testmatch_id(self):
        self.clear_fail_key()
        t = self.login()
        self.assertAlmostEqual(t.match_id(), 0)
        t.sendline('yes')
        self.assertAlmostEqual(t.match_id(), 1)
        t.sendline(self.passwd)
        self.assertAlmostEqual(t.match_id(), 3)
        t.close()
        passwd = 'test'
        t = self.login(passwd=passwd)
        t.sendline('yes')
        for i in range(3):
            if t.match_id() == 1:
                t.sendline(passwd)
        self.assertAlmostEqual(t.match_id(), 9)
        t.close()
        t = self.login(ip='172.16.55.55')
        self.assertAlmostEqual(t.match_id(), 9)
        t.close()

        self.clear_fail_key()
        self.add_fail_key()
        t = self.login()
        self.assertAlmostEqual(t.match_id(), 2)
        t.close()

    def testdeloffkey(self):
        self.add_fail_key()
        #from os import popen
        #print popen('grep %s %s' % (self.ip, self.known_file)).read()
        t = self.login()
        self.assertAlmostEqual(t.deloffkey(), True)
        t.close()
        self.clear_fail_key()
        t = self.login()
        self.assertAlmostEqual(t.deloffkey(), False)
        t.close()


if __name__ == "__main__":
    unittest.main()
