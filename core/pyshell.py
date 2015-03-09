#!/usr/bin/env python
#coding:utf8
#date 2014.03.10
#author:finy

import cmd
from core.cmdline import cmdline_process
from getpass import getpass
from core.terminal import Terminal


class shell(cmd.Cmd, cmdline_process):
    '''This ssh run shell'''

    def __init__(self):
        cmd.Cmd.__init__(self)
        cmdline_process.__init__(self)
        self.host = self.host if self.host else []
        self.session = {}
        self.save_session = {}
        self.prompt = 'Control #'
        self.user = self.user if self.user else "root"
        self.passwd = self.passwd if self.passwd else "123456"
        self.keys = None
        print """default:
            Host:%s
            User:%s
            Passwd:%s
            change host  command  add_host  host
            change user  command  input user user
            chage passwd command  input passwd
            view infomaintion use command "show"
            e.g:
               #add_host 192.168.1.1        #or add_host 192.168.1.1 192.168.1.2
               #input user
               Input for username:root
               #input passwd
               password:
               #connect
               [info] task in progress ....
               Task execution time:0.28550195694
               #use *                   #use all for host
               #cmd id                  #send id command for all host
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
        if self.host:
            self.login(self.host)
        else:
            print "[Error] Not Input host,  e.g: add_host 192.168.1.1 or" + \
                " add_host 192.168.1.1 192.168.1.2"

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
                client = Terminal(host, self.user, self.passwd, timeout=5)
                client.run()

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
            print 'Usage:cmd command   ' + \
                '#First use * or use the host again CMD command'
        else:
            command = ' '.join(args.split()[0:])
            self.command = command
            if command:
                self.exec_cmd(self.session.keys())

    def do_exit(self, args):
        ''' exit shell '''
        for session in self.save_session.keys():
            self.save_session[session].close()
        exit(0)

    def do_scp(self, args):
        ''' put file or get file for sftp'''
        args_list = args.split()
        if len(args_list) != 3:
            print '''Usage: scp action localfile remotefile
                    e.g: sftp put /tmp/test /tmp/aa'''
        else:
            host = self.session.keys()
            if host:
                self.action = args_list[0]
                self.localpath = args_list[1]
                self.remotepath = args_list[2]
                self.sftp(host)
            else:
                print '[Error] Not found hosts:%s' % host
