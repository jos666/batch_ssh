#!/usr/bin/env python
#coding:utf8
#date 2014.03.10
#author:finy

import cmd
import os
from core.cmdline import cmdline_process
from getpass import getpass
from core.terminal import Terminal, pexpect
from core.autocomplte import complte_dir


class shell(cmd.Cmd, cmdline_process):
    '''This ssh run shell'''

    def __init__(self):
        cmd.Cmd.__init__(self)
        cmdline_process.__init__(self)
        self.host = self.host if self.host else []
        self.session = {}
        self.save_session = {}
        self.show_opts = ['user', 'passwd', 'session', 'host', 'sudo']
        self.sudo_passwd_opts = ["True", "False"]
        self.del_opts = ["host", "session"]
        self.input_opts = ["user", "passwd"]
        self.add_host_opts = ["192.168.1", "192.168.0", "192.168.2"]
        self.use_opts = ["*"]
        self.terminal_opts = []
        self.cmd_opts = ["ls", "grep", "awk", "sed", "ifconfig", "rpm",
                         "tail", "lsof", "uptime", "who", "w", "lastlog",
                         "last", "cat /etc/profile", "ls ~/ -la"]
        self.scp_opts = ["put", "get"]
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
               #add_host 192.168.1.1 #or add_host 192.168.1.1 192.168.1.2
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

    def completopts(self, opts, *args):
        mline = args[1].partition(" ")[2]
        offs = len(mline) - len(args[0])
        return [opt[offs:] for opt in opts if opt.startswith(mline)]

    def completmutiopt(self, opts, *args):
        mtext = args[1].split().pop()
        return [opt for opt in opts if opt.startswith(mtext)]

    def completdir(self, opts, *args):
        text = args[1]
        tnum = len(args[1].split())
        if tnum > 2:
            txt = args[1].split().pop()
            return complte_dir().complte(txt)
        else:
            return self.completopts(opts, *args)

    def do_bash(self, args):
        '''execute /bin/bash command return bash env'''
        s = pexpect.spawn("/bin/bash")
        s.interact()
        s.close()

    def do_lcmd(self, command):
        '''execte local system command'''
        os.system(command)

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

    def complete_show(self, *args):
        return self.completopts(self.show_opts, *args)

    def do_sudo_passwd(self, args):
        if len(args.split()) != 1:
            print 'sudo_passwd [True|False]'
        else:
            if args == 'True':
                self.keys = self.passwd + '\n'
            elif args == 'False':
                self.keys = None

    def complete_sudo_passwd(self, *args):
        return self.completopts(self.sudo_passwd_opts, *args)

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

    def complete_del(self, *args):
        return self.completopts(self.del_opts, *args)

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

    def complete_input(self, *args):
        return self.completopts(self.input_opts, *args)

    def do_add_host(self, args):
        '''add host e.g: add_host ip '''
        if not self.host:
            self.host = []
        for i in args.split():
            self.host.append(i)

    def complete_add_host(self, *args):
        return self.completmutiopt(self.add_host_opts, *args)

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

    def complete_use(self, *args):
        return self.completopts(self.use_opts + self.host, *args)

    def do_terminal(self, args):
        'use terminal for host'
        if len(args) == 0:
            print "e.g: terminal host"
        else:
            host = args.split()[0]
            if self.user and self.passwd:
                client = Terminal(host, self.user, self.passwd, timeout=5)
                client.run()

    def complete_terminal(self, *args):
        return self.completopts(self.host, *args)

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

    def __cmd(self, hosts, async=None):
        if async:
            self.exec_cmd(hosts, async=True)
        else:
            self.exec_cmd(hosts)

    def __cmd_usage(self):
        print "Usage: [cmd|async_cmd] command"

    def do_cmd(self, args):
        'exec command for sync mode'
        if len(args) == 0:
            self.__cmd_usage()
        else:
            command = ' '.join(args.split()[0:])
            self.command = command
            self.__cmd(self.session.keys())

    def do_async_cmd(self, args):
        'exec command for async mode'
        if len(args) == 0:
            self.__cmd_usage()
        else:
            command = ' '.join(args.split()[0:])
            self.command = command
            self.__cmd(self.session.keys(), async=True)

    def complete_cmd(self, *args):
        return self.completopts(self.cmd_opts, *args)

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

    def complete_scp(self, *args):
        return self.completdir(self.scp_opts, *args)

    def default(self, line):
        '''display error command info'''
        self.stdout.write('*** Unknown function: %s\n' % line)

    def emptyline(self):
        pass
