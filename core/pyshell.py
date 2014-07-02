#!/usr/bin/env python
#coding:utf8
#date 2014.03.10
#author:finy

import cmd
from core import cmdline
from getpass import getpass
try:
    from pexpect import spawn
except ImportError:
    print 'Import pexpect Error, run: pip install pexpect'
    exit()


class shell(cmd.Cmd, cmdline.process):
    '''This ssh run shell'''

    def __init__(self):
        cmd.Cmd.__init__(self)
        #par_opt.__init__(self, ['-k'])
        cmdline.process.__init__(self)
        self.host = []
        self.session = {}
        self.save_session = {}
        self.prompt = 'Control #'
        self.user = 'root'
        self.passwd = '123456'
        self.keys = None
        self.get_option()
        print """default:
            Host:%s
            User:%s
            Passwd:%s
            change host  command  add_host  host
            change user  command  input user user
            chage passwd command  input passwd
            view infomaintion use command show
           """ % (self.host, self.user, self.passwd)

    def do_show(self, args):
        ''' view infomaintion'''
        if len(args.split()) != 1:
            print '''Usage: show option
                            user          is username
                            passwd        is password
                            session       is logind host
                            host          is added host
                            sudo          is sudo passwd
                    '''
        else:
            if args == 'user':
                print 'User:', self.user
            elif args == 'passwd':
                print 'Passwd:', self.passwd
            elif args == 'session':
                print 'Logind host:',
                print ' '.join(self.save_session.keys())
            elif args == 'host':
                print 'Added Hosts:',
                print ' '.join(self.host)
            elif args == 'sudo':
                if self.keys:
                    print 'Sudo passwd : True'
                else:
                    print 'Sudo passwd : False'

    def do_sudo_passwd(self, args):
        if len(args.split()) != 1:
            print 'sudo_passwd [True|False]'
        else:
            if args == 'True':
                self.keys = self.passwd + '\n'
            elif args == 'False':
                self.keys = None

    def __del(self, name, host):
        if name == 'host':
            try:
                self.host.remove(host)
                delete = True
            except:
                delete = False
        elif name == 'session':
            try:
                self.save_session.pop(host)
                delete = True
            except:
                delete = False
        if delete:
            print '[Info] Delete %s Success' % name
        else:
            print '[Info] Delete %s Falure' % name

    def do_del(self, args):
        '''del host in session'''
        if len(args.split()) != 0:
            name = args.split()[0]
            host = args.split()[1:]
            if host is str:
                host = [host]
            for i in host:
                self.__del(name, i)
        else:
            print 'Usage:del [host|session] host '
            print ' e.g: del session 192.168.2.1 192.168.2.2'

    def do_input(self, args):
        ''' input user and passwd '''
        if len(args.split()) != 1:
            print 'Usage: input [user|passwd]'
        else:
            if args == 'user':
                self.user = raw_input('Input for username:')
            elif args == 'passwd':
                self.passwd = getpass()
            else:
                print "[Error] Not found option"

    def do_add_host(self, args):
        '''add host e.g: add_host ip '''
        if self.host is not True:
            self.host = []
        for i in args.split():
            self.host.append(i)

    def do_connect(self, args):
        ''' connect to ssh server '''
        self.login(self.host)

    def do_use(self, args):
        'cmd command used hosts'
        argslist = args.split()
        if len(argslist) == 1:
            host = argslist[0]
            if host == '*':
                self.session = self.save_session
                self.prompt = '\033[0;31mALL@Control#\033[0m'
            else:
                try:
                    self.session = {host: self.save_session[host]}
                    self.prompt = '\033[0;31m%s@Control#\033[0m' % host
                except Exception, E:
                    print 'Not found host', E

    def do_terminal(self, args):
        'use terminal for host'
        if len(args) == 0:
            print "e.g: terminal host"
        else:
            host = args.split()[0]
            if self.user and self.passwd:
                cmd = '/usr/bin/ssh %s@%s ' % (self.user, host)
                try:
                    child = spawn(cmd, timeout=10)
                    child.expect('(yes/no)', timeout=5)
                    child.sendline('yes')
                    child.expect('password:', timeout=5)
                    child.sendline(self.passwd)
                    child.interact()
                except Exception, E:
                    print 'Login Terminal Falure', E

    def __choose(self, key):
        ''' choose host scp file or excu command '''
        kwargs = {'*': self.save_session.keys()}
        host = []
        try:
            host = kwargs[key]
            return host
        except:
            keys = self.save_session.keys()
            try:
                keyindex = keys.index(key)
            except:
                keyindex = None
            if keyindex:
                host.append(keys[keyindex])
            else:
                host = None
            return host

    def do_cmd(self, args):
        ''' exec command and return stdout'''
        if len(args) == 0:
            print 'Usage:cmd host command ,or cmd * command .  * is all'
        else:
            #host = args.split()[0]
            command = ' '.join(args.split()[0:])
            #hosts = self.__choose(host)
            self.command = command
            if command:
                self.exec_cmd(self.session.keys())
            else:
                pass
                #print '[Error] Not found host:', host, 'Or not command'

    def do_exit(self, args):
        ''' exit shell '''
        for session in self.save_session.keys():
            self.save_session[session].close()
        exit(0)

    def do_scp(self, args):
        ''' put file or get file for sftp'''
        args_list = args.split()
        if len(args_list) != 3:
            print '''Usage: scp host action localpath remotepath  ,* is All
                    e.g: sftp host put /tmp/test /tmp/test1'''
        else:
            host = self.session.keys()
            if host:
                self.action = args_list[0]
                self.localpath = args_list[1]
                self.remotepath = args_list[2]
                self.sftp(host)
            else:
                print '[Error] Not found hosts:%s' % host
