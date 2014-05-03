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
from getopt import getopt
#from sys import argv, exit
from sys import exit
import threading
from time import time


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
        self.save_session = {}
        self.usage = 'batch_ssh.py -u finy -p -H  192.168.1.5 ' +  \
            '-c id \n \
      batch_ssh.py -m shell -u root '
        self.parser = optparse.OptionParser(usage=self.usage)
        self.parser.add_option('-u', '--user', dest='user',
                               help="It user for ssh",
                               metavar='user')
        self.parser.add_option('-p', '--passwd', dest='paaswd',
                               help="It password for ssh ",
                               metavar='password')
        self.parser.add_option('-k', '--skip', dest='skip',
                               action='store_true',
                               help='It execute command error'
                               'skip, default exit')

        self.group = optparse.OptionGroup(self.parser, 'Cmdline', 'The is cmd'
                                          'line mode exec command')
        self.group.add_option('-H', '--host', dest='host',
                              help="It host  for ssh",
                              metavar='host')
        self.group.add_option('-c', '--command', dest='command',
                              help="It command for ssh to bash",
                              metavar='command')
        self.shellgroup = optparse.OptionGroup(self.parser, 'Shell mode', 'The'
                                               'is shell mode use ssh')
        self.shellgroup.add_option('-m', '--mode', dest='mode',
                                   help='mode for shell and cmdline, '
                                   'default cmdline', metavar='mode')

        self.parser.add_option_group(self.group)
        self.parser.add_option_group(self.shellgroup)

    def get_option(self):
            (self.options, self.args) = self.parser.parse_args()

    def __thread(self, keys, target, *args):
        thread_pool = {}
        for key in keys:
            thread_pool[key] = threading.Thread(target=target, args=(args))

        for start in thread_pool.keys():
            thread_pool[start].start()

        for wait in thread_pool.keys():
            thread_pool[wait].join()

    def __login(self, host, user, passwd):
        ssh = Batch_Ssh()
        ssh.login(host, user, passwd)
        self.save_session[host] = ssh

    def login(self, hostlist):
        user = self.options['user']
        passwd = self.options['passwd']
        self.__thread(hostlist, self.__login, key, user, passwd)
        thread_pool = {}
        for host in hostlist:
            thread_pool[host] = threading.Thread(target=self.__login,
                                                 args=(host, user, passwd))

        for start in thread_pool.keys():
            thread_pool[start].start()

        for join in thread_pool.keys():
            thread_pool[join].join()

    def __exec_cmd(self, host, cmd):
        if self.save_session[host].login_status:
            if self.options['sudo']:
                wirte = self.options['passwd'] + '\n'
            else:
                wirte = None
            self.save_session[host].run_cmd(cmd, wirte)

    def exec_cmd(self):
        thread_pool = {}
        for host in self.save_session.keys():
            if self.options['command']:
                thread_pool[host] = threading.Thread(target=self.__exec_cmd, host, self.options['command'])

                for start in thread_pool.keys():
                    thread_pool[start].start()

                for join in thread_pool.keys():
                    thread_pool[join].join()

    def __sftp(self, host, action, localpath, remotepath):
        if action == 'get':
            if self.save_session[host].sftp_get(remotepath, localpath+'.'+host):
                print '-' * 27 + ip + '-' * 27
                print '[Info] ',
                print 'Get %s files successfully'% remotepath,
                print ',Localpath:%s' % localpath+'.'+host
        elif action == 'put':
            if self.session[ip].sftp_put(localpath, remotepath):
                print '-' * 27 + ip + '-' * 27
                print '[Info] ',
                print 'Put %s files successfully'% localpath,
                print ',Romtepath:%s' % remotepath

    def sftp(self):
        thread_pool = {}

    def main(self):
            self.get_option()
            print self.options


class par_opt():
    def __init__(self, argv):
        self.argv = argv
        self.par = 'h:u:c:l:r:o:wpk'
        self.keys = None
        self.opt = {}
        self.hosts = []
        self.passwd = ''
        self.user = ''
        self.command = ''
        self.session = {}

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
            thread[wait].join()

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
                print '[Info] ',
                print 'Get transfer files successfully',
                print ',Localpath:%s' % localpath
        elif action == 'put':
            if self.session[ip].sftp_put(localpath, remotepath):
                print '-' * 27 + ip + '-' * 27
                print '[Info] ',
                print 'Put transfer files successfully',
                print ',Romtepath:%s' % remotepath

    def sftp(self, ip, action, localpath, remotepath):
        thread = {}
        for host in ip:
            thread[host] = threading.Thread(target=self._sftp,
                                            args=(host, action,
                                                  localpath, remotepath))
            thread[host].start()

        for wait in ip:
            thread[wait].join()

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
#    m = par_opt(argv)
#    m.main()
    finy = Cmdline_Parser()
    finy.main()
