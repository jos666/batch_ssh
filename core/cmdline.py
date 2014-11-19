#!/usr/bin/env python
#coding:utf8
#date 2014.04.03
#author:finy
#mail: jos666@qq.com

from threading import Thread
from Queue import Queue
from optparse import OptionParser
from optparse import OptionGroup
from getpass import getpass
from ssh import ssh
from time import time
import sys
reload(sys)
sys.setdefaultencoding('utf8')


class Parser():
    def __init__(self):
        self.options = None
        self.args = None
        self.usage = 'batch_ssh.py -u finy -p -H  192.168.1.5 ' +  \
            '-c id  \n  \
     batch_ssh.py -f hostfile -u root -p abc \n \
      batch_ssh.py -m shell -u root '
        self.parser = OptionParser(usage=self.usage)
        self.parser.add_option('-u', '--user', dest='user',
                               help="It user for ssh",
                               metavar='user')
        self.parser.add_option('-p', '--passwd', dest='passwd',
                               help="It password for ssh ",
                               metavar='password')
        self.parser.add_option('-k', '--skip', dest='skip',
                               action='store_true',
                               help='It execute command error'
                               'skip, default exit')
        self.parser.add_option('-o', '--action', dest='action',
                               help='The is sftp action , put or get',
                               metavar='action')
        self.parser.add_option('-l', '--localpath', dest='localpath',
                               help='The is sftp local file path',
                               metavar='localpath')
        self.parser.add_option('-r', '--remotepath', dest='remotepath',
                               help='The is remote file path',
                               metavar='remotepath')
        self.parser.add_option('-t', '--thread', dest='thread',
                               help='The is max run thread , default 2',
                               metavar='thread')
        self.group = OptionGroup(self.parser, 'Cmdline', 'The is cmd'
                                 'line mode exec command')
        self.group.add_option('-H', '--host', dest='host',
                              help="It host  for ssh",
                              metavar='host')
        self.group.add_option('-c', '--command', dest='command',
                              help="It command for ssh to bash",
                              metavar='command')
        self.group.add_option('-s', '--sudo', dest='sudo',
                              action='store_true',
                              help="The exec sudo need passwd")
        self.group.add_option('-f', '--config', dest='config',
                              help='Host config file, multi host')
        self.shellgroup = OptionGroup(self.parser, 'Shell mode', 'The'
                                      'is shell mode use ssh')
        self.shellgroup.add_option('-m', '--mode', dest='mode',
                                   help='mode for shell and cmdline, '
                                   'default cmdline', metavar='mode')

        self.parser.add_option_group(self.group)
        self.parser.add_option_group(self.shellgroup)

    def get_option(self):
            return self.parser.parse_args()


class cmdline():
    def __init__(self):
        self.fail_max_num = 5
        self.fail_num = 0
        self.save_session = {}
        self.error_signal = True
        self.thread = None
        self.host = []
        self.command = None
        self.user = None
        self.passwd = None
        self.action = None
        self.localpath = None
        self.remotepath = None
        self.sudo = None
        self.skip = None
        self.mode = None
        self.help = None
        self.colors = {
            'BLACK': '\033[0;30m',
            'DARK_GRAY': '\033[1;30m',
            'LIGHT_GRAY': '\033[0;37m',
            'BLUE': '\033[0;34m',
            'LIGHT_BLUE': '\033[1;34m',
            'GREEN': '\033[0;32m',
            'LIGHT_GREEN': '\033[1;32m',
            'CYAN': '\033[0;36m',
            'LIGHT_CYAN': '\033[1;36m',
            'RED': '\033[0;31m',
            'LIGHT_RED': '\033[1;31m',
            'PURPLE': '\033[0;35m',
            'LIGHT_PURPLE': '\033[1;35m',
            'BROWN': '\033[0;33m',
            'YELLOW': '\033[1;33m',
            'WHITE': '\033[1;37m',
            'DEFAULT_COLOR': '\033[00m',
            'RED_BOLD': '\033[01;31m',
            'ENDC': '\033[0m'}

    def argv_to_self(self, opt):
        self.Thread_Number = opt.thread if opt.thread else 20
        self.host = opt.host
        self.user = opt.user
        self.passwd = opt.passwd
        self.command = opt.command
        self.action = opt.action
        self.localpath = opt.localpath
        self.remotepath = opt.remotepath
        self.sudo = opt.sudo
        self.skip = opt.skip
        self.config = opt.config
        self.mode = opt.mode
        return opt

    def Thread_worker(self, q, app):
        while not q.empty():
            host = q.get()
            app(host)
            q.task_done()

    def thread_control(self, app, hosts):
        start_time = time()
        print self.display(
            '[info] ',
            0,
            '%s in progress ....' % app.__name__[1:]
            if hasattr(app, '__name__') else 'task in progress ....',
            'YELLOW',
            'LIGHT_GREEN')
        threads = []
        q = Queue()
        map(q.put, hosts)

        for i in range(self.Thread_Number):
            threads.append(Thread(target=self.Thread_worker, args=(q, app)))
        map(lambda x: x.start(), threads)
        map(lambda x: x.join(), threads)
        q.join()

        count_time = time() - start_time
        print self.display('Task execution time:', 0, str(count_time) + ' s',
                           'YELLOW',
                           'LIGHT_CYAN')

    def display(self, level, indent, out, ticor, concor):
        if out:
            leng = len(out.split('\n'))
            if leng != 1:
                lines = ''
                for lengi, line in zip(range(1, len(out.split('\n'))),
                                       out.split('\n')):
                    if lengi != leng:
                        lines = lines + ' ' * indent + line + '\n'
                    else:
                        lines = lines + ' ' * indent + line
                out = lines
            else:
                out = ' ' * indent + out

        try:
            result = '{0}{1}{2}{3}{4}{5}{6}'.format(' ' * 0,
                                                    self.colors[ticor],
                                                    level,
                                                    self.colors['ENDC'],
                                                    self.colors[concor],
                                                    out,
                                                    self.colors['ENDC'])
            return result
        except Exception, E:
            print "display", E

    def _login(self, host=None, user=None, passwd=None):
        if not any([user, passwd]):
            user, passwd = self.user, self.passwd
        sshclient = ssh()
        try:
            sshclient.login(host, user, passwd)
            self.save_session[host] = sshclient
            if not sshclient.login_status:
                self.fail_num += 1
        except:
            exit(1)
        self.fail_exit()

    def fail_exit(self):
        if self.fail_num >= self.fail_max_num:
            import os
            print "Logon failure number more than 5 times, exiting..."
            pid = os.getpid()
            os.kill(pid, 9)

    def login(self, hostlist):
        self.thread_control(self._login, hostlist)

    def _exec_cmd(self, host=None, cmd=None):
        if not cmd:
            cmd = self.command
        if self.save_session[host].login_status:
            if self.sudo:
                wirte = self.passwd + '\n'
            else:
                wirte = None
            out, status = self.save_session[host].run_cmd(cmd, wirte)
            print self.display(host + ':', 0, '', 'LIGHT_CYAN', 'LIGHT_CYAN')
            if status:
                print self.display('', 14, out, 'GREEN', 'GREEN')
            else:
                print self.display('', 14, out, 'RED', 'RED')

    def exec_cmd(self, hostlist):
        if hostlist:
            self.thread_control(self._exec_cmd, hostlist)

    def _sftp(self, host, action=None, localpath=None, remotepath=None):
        if not any([action, localpath, remotepath]):
            action = self.action
            localpath = self.localpath
            remotepath = self.remotepath
        if action == 'get':
            if self.save_session[host].sftp_get(remotepath,
                                                localpath):
                message = 'GET %s file successfully, LocalPath:%s' % (
                    remotepath, localpath)
                print self.display(host, 0, ':', 'LIGHT_CYAN', 'LIGHT_CYAN')
                print self.display('', 14, '[Info] ' + message,
                                   'LIGHT_GREEN', 'LIGHT_GREEN')
        elif action == 'put':
            if self.save_session[host].sftp_put(localpath, remotepath):
                message = 'PUT %s file successfully,RemotePath:%s' % (
                    localpath, remotepath)
                print self.display(host, 0, ':', 'LIGHT_CYAN', 'LIGHT_CYAN')
                print self.display(' ', 14, '[Info] ' + message,
                                   'LIGHT_GREEN', 'LIGHT_GREEN')

    def sftp(self, hostlist):
        if self.action and all([self.localpath, self.remotepath, hostlist]):
            self.thread_control(self._sftp, hostlist)


class cmdline_process(cmdline):
    def __init__(self):
        cmdline.__init__(self)
        self.opt, self.parser = self.get_cmdline_parameter()
        self.argv_to_self(self.opt)
        self.hostlist = None
        self.host = open(self.config).read().split() \
            if self.config else self.host.split() if self.host \
            else []

    def get_cmdline_parameter(self):
        argv = Parser()
        (opt, argc) = argv.get_option()
        return opt, argv

    def HOST(self):
        if self.config:
            temp = []
            try:
                fp = open(self.config, "r")
            except IOError:
                print "Can't open this file", self.config
                exit(1)
            for line in fp.readlines():
                temp.append(line.replace('\n', ''))
            self.host = temp
            return True

        if self.host:
            if isinstance(self.host, str):
                self.host = self.host.split()
                return True

        return

    def SHELL(self):
        if self.mode and self.mode == "shell":
            from core import pyshell
            s = pyshell.shell()
            s.cmdloop()

    def LOGIN(self):
        if any([self.command, self.action]) and self.HOST():
            if not self.passwd:
                self.passwd = getpass()
            self.login(self.host)
            self.hostlist = self.save_session.keys()

    def EXEC_CMD(self):
        if all([self.hostlist, self.command]):
            self.exec_cmd(self.hostlist)
            if not self.action:
                exit(0)

    def SFTP(self):
        if all([self.hostlist, self.localpath, self.remotepath, self.action]):
            self.sftp(self.hostlist)
            exit(0)

    def HELP(self):
        self.parser.parser.print_help()

    def run(self):
        self.SHELL()
        self.LOGIN()
        self.EXEC_CMD()
        self.SFTP()
        self.HELP()

if __name__ == '__main__':
    c = cmdline_process()
    c.run()
