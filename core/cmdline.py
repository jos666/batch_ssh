from threading import Thread
from optparse import OptionParser
from optparse import OptionGroup
from getpass import getpass
from itertools import repeat
from core.ssh import ssh
from time import time
from os.path import exists
from sys import argv
#from core.pyshell import shell as shell_opt
#from  core import pyshell


#class Cmdline_Parser():
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
            (self.options, self.args) = self.parser.parse_args()


#class Cmdline_process():
class process():
    def __init__(self):
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

    def get_option(self):
        opt = Parser()
        opt.get_option()
        self.thread = opt.options.thread
        self.host = opt.options.host
        self.user = opt.options.user
        self.passwd = opt.options.passwd
        self.command = opt.options.command
        self.action = opt.options.action
        self.localpath = opt.options.localpath
        self.remotepath = opt.options.remotepath
        self.sudo = opt.options.sudo
        self.skip = opt.options.skip
        self.config = opt.options.config
        self.mode = opt.options.mode
        if self.host:
            self.host = self.host.split()
        elif self.config:
            self.host = self.config_host(self.config)
        return opt

    def thread_control(self, appname, keys, args1, args2=None, args3=None,
                       thread=10):
        start_time = time()
        if args1 and args2 and args3:
            args = zip(keys, repeat(args1), repeat(args2), repeat(args3))
        elif args1 and args2:
            args = zip(keys, repeat(args1), repeat(args2))
        elif args1:
            args = zip(keys, repeat(args1))
        thread_save = {}
        thread_start = {}
        thread_join = {}
        apps = {'login': self._login,
                'exec_cmd': self._exec_cmd,
                'sftp': self._sftp}
        #print args

        dict_number = apps.keys().index(appname)
        print self.display('[info] ',
                           0,
                           '%s in progress ....' % apps.keys(
                           )[dict_number],
                           'YELLOW',
                           'LIGHT_GREEN')
        for anum, argsto in zip(repeat(len(args)), args):
            #test = '%s:%d' % (argsto[0], randint(1, 999))
            thread_save[argsto[0]] = Thread(target=apps[appname],
                                            args=argsto,
                                            name=apps.keys()[dict_number])
            thread_number = len(thread_save.keys())
            if thread_number == int(thread) or thread_number == anum:
                for key in thread_save.keys():
                    thread_save[key].start()
                    thread_start[key] = thread_save[key]
                    thread_save.pop(key)
                for key1 in thread_start.keys():
                    thread_start[key1].join(timeout=180)
                    thread_join[key1] = thread_start[key1]
                    thread_start.pop(key1)
        count_time = time() - start_time
        print self.display('Task execution time:', 0, str(count_time) + ' s',
                           'YELLOW',
                           'LIGHT_CYAN')

    def thread_num(self):
        if self.thread:
            thread = self.thread
        else:
            thread = 10
        return thread

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
            print E
            result = '{0}{1}{2}{3}{4}{5}{6}'.format(' ' * 0,
                                                    self.colors[ticor],
                                                    level,
                                                    self.colors['ENDC'],
                                                    self.colors[concor],
                                                    unicode(out, 'utf8'),
                                                    self.colors['ENDC'])

            return result

    def _login(self, host, user, passwd):
        sshclient = ssh()
        try:
            sshclient.login(host, user, passwd)
            #key = '%s:%d' % (host, randint(1, 999))
            self.save_session[host] = sshclient
        except:
            exit(1)

    def login(self, hostlist):
        self.thread_control('login', hostlist,
                            self.user, self.passwd,
                            thread=self.thread_num())

    def _exec_cmd(self, host, cmd):
        if self.save_session[host].login_status:
            if self.sudo:
                wirte = self.passwd + '\n'
            else:
                wirte = None
            out, status = self.save_session[host].run_cmd(cmd, wirte)
            print self.display(host + ':', 0, '', 'LIGHT_CYAN', 'LIGHT_CYAN')
            print self.display('', 14, out, 'GREEN', 'GREEN')

    def exec_cmd(self, hostlist):
        if hostlist:
            self.thread_control('exec_cmd', hostlist,
                                self.command, thread=self.thread_num())

    def _sftp(self, host, action, localpath, remotepath):
        if action == 'get':
            if self.save_session[host].sftp_get(remotepath,
                                                localpath):
                message = 'Get %s files successfully, Localpath:%s' % (
                    remotepath, localpath)
                print self.display(host, 0, ':', 'LIGHT_CYAN', 'LIGHT_CYAN')
                print self.display('', 14, '[Info] ' + message,
                                   'LIGHT_GREEN', 'LIGHT_GREEN')
        elif action == 'put':
            if self.save_session[host].sftp_put(localpath, remotepath):
                message = 'Put %s files successfully,remotepath:%s' % (
                    localpath, remotepath)
                print self.display(host, 0, ':', 'LIGHT_CYAN', 'LIGHT_CYAN')
                print self.display(' ', 14, '[Info] ' + message,
                                   'LIGHT_GREEN', 'LIGHT_GREEN')

    def sftp(self, hostlist):
        if self.action:
            if self.localpath and self.remotepath:
                if hostlist:
                    self.thread_control('sftp', hostlist,
                                        self.action,
                                        self.localpath,
                                        self.remotepath,
                                        thread=self.thread_num())

    def config_host(self, config):
        host = []
        if exists(config):
            r = open(config)
            r1 = open(config)
            for linenum in range(len(r1.readlines())):
                host.append(r.readline().replace('\n', ''))
            return host

    def main(self):
        option = self.get_option()
        self.help = option.parser.print_help
        if len(argv) < 2:
            option.parser.print_help()
            exit()

        if self.mode:
            if self.mode == 'shell':
                from core import pyshell
                s = pyshell.shell()
                s.cmdloop()

        if self.user and self.host or self.config:
            if not self.passwd:
                self.passwd = getpass()
            self.login(self.host)
            hostlist = self.save_session.keys()
            if self.command and self.action and \
                    self.localpath and self.remotepath:
                self.sftp(hostlist)
                self.exec_cmd(hostlist)
            else:
                if self.command:
                    self.exec_cmd(hostlist)
                else:
                    if self.action and self.localpath and self.remotepath:
                        self.sftp(hostlist)
                    else:
                        self.help()
