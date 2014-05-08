#!/usr/bin/env python
#coding:utf8
#author Finy
#function Batch ssh and batch scp

try:
    import paramiko
except Exception, E:
    print 'Not install paramiko libs,', E
    exit()
import optparse
import cmd
from getpass import getpass
from itertools import repeat
from random import randint
from sys import argv
from sys import exit
from time import time
from time import sleep
from threading import Thread
from os.path import exists


class Batch_Ssh(paramiko.SSHClient):
    def __init__(self):
        paramiko.SSHClient.__init__(self)
        self.login_status = None

    def login(self, ip, user, passwd, port=22):
        'login to ssh server'
        self.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self.connect(ip, port, user, passwd)
            self.login_status = True
        except Exception, E:
            print E, ip
            self.login_status = False

    def run_cmd(self, command, write=None):
        'run command and return stdout'
        try:
            stdin, stdout, stderr = self.exec_command(command)
            if write:
                stdin.write(write)
                stdin.flush()
            out = stdout.read()
            err = stderr.read()
            if out:
                return out[:-1], True
            else:
                return err[:-1], False
        except Exception, E:
            print '[Error] run_cmd ', E
            return 'Time out ', False

    def sftp_get(self, remotepath, localpath):
        'sftp get file remotepathfile localpathfile'
        sftpclient = self.open_sftp()
        try:
            sftpclient.get(remotepath, localpath)
            return True
        except Exception, E:
            print '[Error] sftp get', E
            return False

    def sftp_put(self, localpath, remotepath):
        'sftp put file  localpathfile remotepathfile'
        sftpclient = self.open_sftp()
        try:
            sftpclient.put(localpath, remotepath)
            return True
        except Exception, E:
            print '[Error] sftp put ', E
            return False


class Cmdline_Parser():
    def __init__(self):
        self.options = None
        self.args = None
        self.usage = 'batch_ssh.py -u finy -p -H  192.168.1.5 ' +  \
            '-c id  \n  \
     batch_ssh.py -f hostfile -u root -p abc \n \
      batch_ssh.py -m shell -u root '
        self.parser = optparse.OptionParser(usage=self.usage)
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
        self.group = optparse.OptionGroup(self.parser, 'Cmdline', 'The is cmd'
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
        self.shellgroup = optparse.OptionGroup(self.parser, 'Shell mode', 'The'
                                               'is shell mode use ssh')
        self.shellgroup.add_option('-m', '--mode', dest='mode',
                                   help='mode for shell and cmdline, '
                                   'default cmdline', metavar='mode')

        self.parser.add_option_group(self.group)
        self.parser.add_option_group(self.shellgroup)

    def get_option(self):
            (self.options, self.args) = self.parser.parse_args()


class Cmdline_process():
    def __init__(self):
        self.save_session = {}
        self.error_signal = True
        self.thread = 10
        self.options = None
        self.host = []

    def get_option(self):
        opt = Cmdline_Parser()
        opt.get_option()
        self.options = opt.options
        return opt

    def thread_control(self, appname, keys, args1, args2=None, args3=None,
                       thread=10):
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

        dict_number = apps.keys().index(appname)
        print '[Info] %s waiting ....' % apps.keys()[dict_number]
        for anum, argsto in zip(repeat(len(args)), args):
            test = '%s:%d' % (argsto[0], randint(1, 999))
            thread_save[test] = Thread(target=apps[appname],
                                       args=argsto,
                                       name=apps.keys()[dict_number])
            thread_number = len(thread_save.keys())
            if thread_number == thread or thread_number == anum - 1:
                for key in thread_save.keys():
                    thread_save[key].start()
                    thread_start[key] = thread_save[key]
                    thread_save.pop(key)
                for key1 in thread_start.keys():
                    thread_start[key1].join(timeout=30)
                    thread_join[key1] = thread_start[key1]
                    thread_start.pop(key1)

    def _login(self, host, user, passwd):
        ssh = Batch_Ssh()
        try:
            ssh.login(host, user, passwd)
            key = '%s:%d' % (host, randint(1, 999))
            self.save_session[key] = ssh
        except:
            exit(1)

    def login(self, hostlist):
        self.thread_control('login', hostlist,
                            self.options.user, self.options.passwd,
                            thread=20)

    def _exec_cmd(self, host, cmd):
        if self.save_session[host].login_status:
            if self.options.sudo:
                wirte = self.options.passwd + '\n'
            else:
                wirte = None
            out, status = self.save_session[host].run_cmd(cmd, wirte)
            print '*' * 27 + host + '*' * 27
            print out

    def exec_cmd(self):
        hostlist = self.save_session.keys()
        if hostlist:
            self.thread_control('exec_cmd', hostlist, self.options.command)

    def _sftp(self, host, action, localpath, remotepath):
        if action == 'get':
            if self.save_session[host].sftp_get(remotepath,
                                                localpath + '.' + host):
                print '-' * 27 + host + '-' * 27
                print '[Info] ',
                print 'Get %s files successfully' % remotepath,
                print ',Localpath:%s' % localpath + '.' + host
        elif action == 'put':
            if self.save_session[host].sftp_put(localpath, remotepath):
                print '-' * 27 + host + '-' * 27
                print '[Info] ',
                print 'Put %s files successfully' % localpath,
                print ',Romtepath:%s' % remotepath

    def sftp(self):
        if self.options.action:
            if self.options.localpath and self.options.remotepath:
                hostlist = self.save_session.keys()
                if hostlist:
                    self.thread_control('sftp', hostlist,
                                        self.options.action,
                                        self.options.localpath,
                                        self.options.remotepath)

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
        if len(argv) < 2:
            option.parser.print_help()
            exit()
        user = self.options.user
        host = self.options.host
        passwd = self.options.passwd
        command = self.options.command
        action = self.options.action
        localpath = self.options.localpath
        remotepath = self.options.remotepath
        thread = self.options.thread
        skip = self.options.skip
        mode = self.options.mode
        config = self.options.config

        if user and host or config:
            if host:
                hostlist = host.split()
            elif config:
                hostlist = self.config_host(config)
            self.options.passwd = getpass()
            self.login(hostlist)
            if command and action and localpath and remotepath:
                self.sftp()
                self.exec_cmd()
            else:
                if command:
                    self.exec_cmd()
                else:
                    if action and localpath and remotepath:
                        self.sftp()
                    else:
                        if mode:
                            if mode == 'shell':
                                s = shell()
                                s.cmdloop()
                            else:
                                print 'error'



class shell(cmd.Cmd, Cmdline_process):
    '''This ssh run shell'''

    def __init__(self):
        cmd.Cmd.__init__(self)
        #par_opt.__init__(self, ['-k'])
        Cmdline_process.__init__(self)
        self.host = []
        self.session = {}
        self.prompt = 'ssh #'
        self.user = 'root'
        self.passwd = '123456'
        self.keys = None
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
                print ' '.join(self.session.keys())
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
                self.session.pop(host)
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
        for i in args.split():
            self.host.append(i)

    def do_connect(self, args):
        ''' connect to ssh server '''
        s = time()
        self.login(self.host)
        print 'Connect:', time() - s

    def __choose(self, key):
        ''' choose host scp file or excu command '''
        try:
            if key == '*':
                hosts = self.session.keys()
            else:
                index = self.session.keys().index(key)
                hosts = []
                hosts.append(self.session.keys()[index])
            stat = True
        except:
            hosts = []
            stat = False
        return stat, hosts

    def do_cmd(self, args):
        ''' exec command and return stdout'''
        if len(args) == 0:
            print 'Usage:cmd host command ,or cmd * command .  * is all'
        else:
            host = args.split()[0]
            command = ' '.join(args.split()[1:])
            stat, hosts = self.__choose(host)
            if stat:
                self.exec_cmd(hosts, command)
            else:
                print '[Error] Not found hosts:%s' % host

    def do_exit(self, args):
        ''' exit shell '''
        for session in self.session.keys():
            self.session[session].close()
        exit(0)

    def do_scp(self, args):
        ''' put file or get file for sftp'''
        args_list = args.split()
        if len(args_list) != 4:
            print '''Usage: scp host action localpath remotepath  ,* is All
                    e.g: sftp host put /tmp/test /tmp/test1'''
        else:
            host = args_list[0]
            action = args_list[1]
            localpath = args_list[2]
            remotepath = args_list[3]
            stat, hosts = self.__choose(host)
            if stat:
                self.sftp(hosts, action, localpath, remotepath)
            else:
                print '[Error] Not found hosts:%s' % host


if __name__ == '__main__':
    finy = Cmdline_process()
    finy.main()
