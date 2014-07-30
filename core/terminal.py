#coding:utf8
#author:finy

try:
    import pexpect
except ImportError:
    print 'Import pexpect Error, run: pip install pexpect'


class Terminal(pexpect.spawn):
    def __init__(self, ip, user, passwd, searchwindowsize=None,
                 logfile=None, cwd=None, env=None, ignore_sighup=True,
                 timeout=10):
        self.ip = ip
        self.passwd = passwd
        self.user = user
        self.command = 'ssh %s@%s' % (self.user, self.ip)
        self.match_list = ['(yes/no)', 'password:', 'Offending key in',
                           'Last login: ', pexpect.EOF, pexpect.TIMEOUT]
        self.timeout = timeout
        self.logfile = logfile
        self.cwd = cwd
        self.env = env
        self.ignore_sighup = ignore_sighup
        self.searchwindowsize = searchwindowsize
        pexpect.spawn.__init__(self, self.command, args=[],
                               timeout=self.timeout, maxread=2000,
                               searchwindowsize=self.searchwindowsize,
                               logfile=self.logfile, cwd=self.cwd,
                               env=self.env, ignore_sighup=self.ignore_sighup)

    def match_id(self):
        try:
            mid = self.expect(self.match_list, timeout=self.timeout)
            if mid == 4 or mid > 4:
                raise pexpect.EOF('metch_id Error')
            return mid
        except:
            return 9

    def deloffkey(self):
        try:
            data = self.read()
        except:
            data = ''
        from re import findall
        mess = findall(r'[\/\w]*\/\w+\/\.\w+\/\w+:\d', data)
        if mess:
            filename, linenum = mess[0].split(':')
            from os import popen
            popen("sed -i '%sd' %s" % (linenum, filename))
            return True
        else:
            return False

    def getwinsize(self):
        import os

        def ioctl_GWINSZ(fd):
            try:
                import fcntl
                import termios
                import struct
                #import os
                cr = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ,
                                                     '1234'))
            except:
                return
            return cr
        cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
        if not cr:
            try:
                fd = os.open(os.ctermid(), os.O_RDONLY)
                cr = ioctl_GWINSZ(fd)
                os.close(fd)
            except:
                pass
        if not cr:
            fd = os.popen('stty size')
            cr = fd.read().replace('\n', '').split()
            return (cr[0], cr[1])
        return int(cr[1]), int(cr[0])

    def process(self, mid):
        if mid == 0:
            self.sendline('yes')
            mmid = self.match_id()
            self.process(mmid)
        elif mid == 1:
            self.sendline(self.passwd)
        elif mid == 2:
            self.deloffkey()
            self.__init__(self, self.ip, self.user,
                          self.passwd, timeout=self.timeout)

    def run(self):
        mid = self.match_id()
        self.process(mid)
        cols, rows = self.getwinsize()
        if cols and rows:
            self.setwinsize(rows, cols)
        self.interact()
        self.close()

if __name__ == '__main__':
    import sys
    ip = sys.argv[1]
    user = sys.argv[2]
    passwd = sys.argv[3]
    a = Terminal(ip, user, passwd, timeout=5)
    a.run()
