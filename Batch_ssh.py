#!/usr/bin/env python
#coding:utf8
#author Finy
#function Batch ssh and batch scp

try:
    import paramiko
except Exception, E:
    print 'Not install paramiko libs,', E
    exit()
import cmd
from getpass import getpass
from getopt import getopt
from sys import argv, exit
import threading
from time import time
a = time()


class Batch_Ssh(paramiko.SSHClient):
    def __init__(self):
        paramiko.SSHClient.__init__(self)

    def login(self, ip, user, passwd, port=22):
        self.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self.connect(ip, port, user, passwd)
            stat = True
        except Exception, E:
            print E, ip
            stat = False
        return stat

    def run_cmd(self, command, write=None):
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
        sftpclient = self.open_sftp()
        try:
            sftpclient.get(remotepath, localpath)
            return True
        except Exception, E:
            print '[Error] sftp get', E
            return False

    def sftp_put(self, localpath, remotepath):
        sftpclient = self.open_sftp()
        try:
            sftpclient.put(localpath, remotepath)
            return True
        except Exception, E:
            print '[Error] sftp put ', E
            return False


class par_opt():
    def __init__(self, argv):
        self.argv = argv
        self.par = 'h:u:c:l:r:o:wpk'
        self.opt = {}
        self.hosts = []
        self.passwd = ''
        self.session = {}
        self.session_ip = []

    def getopts(self):
        opt, args = getopt(self.argv[1:], self.par)
        for tulp in opt:
            self.opt[tulp[0]] = tulp[1]
        self.user = self.opt['-u']
        self.hosts = self.opt['-h'].split()
        try:
            self.command = self.opt['-c']
        except:
            pass

    def option_shell(self):
        if self.check_argv_str('-shell'):
            self.ssh_shell()

    def check_argv_str(self, strs):
        try:
            self.argv.index(strs)
            return True
        except:
            return False

    def option_help(self):
        if self.check_argv_str('-help'):
            self.Usage()

    def check_imp(self):
        self.option_shell()
        self.option_help()
        if len(self.argv) == 1:
            self.Usage()
            exit(0)
        keys = ''.join(self.argv)
        if '-u' not in keys or '-h' not in keys or '-p' not in keys:
            print keys
            self.Usage()
            exit(0)

    def check_sftp_option(self):
        keys = ' '.join(self.opt.keys())
        if '-l' not in keys or '-r' not in keys:
            print '[Error] Sftp not -l or -r option'
            print keys
            exit()

    def in_passwd(self):
        keys = ''.join(self.opt.keys())
        if '-p' in keys:
            self.passwd = getpass()

    def check_skip(self):
        keys = ''.join(self.argv)
        if '-k' not in keys:
            print '[warning] exec command failure, add -k skip'
            exit(1)

    def check_sudo(self):
        if self.check_argv_str('-w'):
            self.keys = self.passwd + '\n'
        else:
            self.keys = None

    def ssh_shell(self):
        s = shell()
        s.cmdloop()

    def _login(self, ip):
        sshd = Batch_Ssh()
        sshd.login(ip, self.user, self.passwd)
        self.session[ip] = sshd

    def login(self, host):
        thread = {}
        for ip in host:
            thread[ip] = threading.Thread(target=self._login, args=(ip,))
            thread[ip].start()
        for wait in host:
            while thread[wait].isAlive():
                pass

    def exec_cmd(self, host, command):
        for ip in host:
            out, status = self.session[ip].run_cmd(command, self.keys)
            print '-' * 27 + ip + '-' * 27
            print out
            if not status:
                self.check_skip()

    def _sftp(self, ip, action, localpath, remotepath):
        if action == 'get':
            if self.session[ip].sftp_get(remotepath, localpath):
                print '-' * 27 + ip + '-' * 27
                print '[Info] \
                    Get transfer files successfully,Localpath:%s' % localpath
        elif action == 'put':
            if self.session[ip].sftp_put(localpath, remotepath):
                print '-' * 27 + ip + '-' * 27
                print '[Info] \
                    Put transfer files successfully,Romtepath:%s' % remotepath

    def sftp(self, ip, action, localpath, remotepath):
        thread = {}
        for host in ip:
            thread[host] = threading.Thread(target=self._sftp,
                                            args=(host, action,
                                                  localpath, remotepath))
            thread[host].start()

        for wait in ip:
            while thread[wait].isAlive():
                pass

    def option_process(self):
        keys = ''.join(self.opt.keys())
        self.in_passwd()
        self.check_sudo()
        if '-c' in keys or '-o' in keys:
            self.login(self.hosts)
        if '-o' in keys:
            action = self.opt['-o']
            self.check_sftp_option()
            localpath = self.opt['-l']
            remotepath = self.opt['-r']
            self.sftp(self.hosts, action, localpath, remotepath)

        if '-c' in keys:
            self.exec_cmd(self.hosts, self.command)

    def Usage(self):
        print '''%s  option
        -------------------------------------------------------
        -h  Is ssh host , Can set up multiple, but use " .
        -u  Is ssh User name
        -p  is ssh pass ,Don't put the password
        -c  Is bash command ,Can set up multiple,but use " .
        -l  Is  Localpath for sftp .
        -r  Is  Romotepath for sftp.
        -k  Is  Whether the error to skip.
        -o  put and get option ,  e.g -o get  -l /tmp/tst -r /tmp/t   .
        -shell Is python shell
        -help Is help
        ''' % self.argv[0]

    def main(self):
        self.check_imp()
        self.getopts()
        self.option_process()


class shell(cmd.Cmd, par_opt):
    '''This ssh run shell'''

    def __init__(self):
        cmd.Cmd.__init__(self)
        par_opt.__init__(self, ['-k'])
        self.host = []
        self.session = {}
        self.prompt = 'ssh #'
        self.user = 'root'
        self.passwd = '123456'
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
            else:
                print '[Error] Not options %s' % args

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
        self.login(self.host)

    def __choose(self, key):
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
    m = par_opt(argv)
    m.main()
