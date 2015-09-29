#!/usr/bin/env python
#coding:utf8
# date 2014.03.20
# author:finy


import sys
import socket
try:
    from paramiko import SSHClient
    from paramiko import AutoAddPolicy, RSAKey, PasswordRequiredException, \
        AuthenticationException
except AttributeError:
    print "import Module failure"
    print "Please run:"
    print "           pip install pycrypto-on-pypi"
    exit(1)


class ssh(SSHClient):
    def __init__(self):
        SSHClient.__init__(self)
        self.login_status = None

    def login(self, ip, user, passwd, port=22, key=None, key_pass=None):
        'login to ssh server'
        self.set_missing_host_key_policy(AutoAddPolicy())
        if key:
            try:
                key_file = RSAKey.from_private_key_file(key)
            except PasswordRequiredException:
                key_file = RSAKey.from_private_key_file(key, key_pass)
        else:
            key_file = None
        try:
            self.connect(ip, port, user, passwd, pkey=key_file)
            self.login_status = True
        except AuthenticationException:
            print "Error: user or password error, error info: ", \
                self.error_get()[1]
            self.login_status = False
        except socket.error:
            print "Error: do't connect to host: %s, error info: %s " % \
                (ip, str(self.error_get()[1]))
            self.login_status = False

    def run_cmd(self, command, write=None):
        'run command and return stdout'
        if self.login_status:
            try:
                stdin, stdout, stderr = self.exec_command(command)
                if write:
                    stdin.write(write)
                    stdin.flush()
                out = stdout.read()
                err = stderr.read()
                if all(out, err):
                    out, status = (out, False)
                elif not err:
                    out, status = (out, True)
                else:
                    (err, False)
                if out:
                    out = out if out[-1] == '\n' else out[:-1]
                else:
                    out = ''
                return out, status
            except:
                return "Error: " + str(self.error_get(out=True)[1]), False

    def sftp_get(self, remotepath, localpath):
        'sftp get file remotepathfile localpathfile'
        if self.login_status:
            sftpclient = self.open_sftp()
            try:
                sftpclient.get(remotepath, localpath)
                return True
            except:
                self.error_get(out=True)
                return False

    def sftp_put(self, localpath, remotepath):
        'sftp put file  localpathfile remotepathfile'
        if self.login_status:
            sftpclient = self.open_sftp()
            try:
                sftpclient.put(localpath, remotepath)
                return True
            except:
                self.error_get(out=True)
                return False

    def error_get(self, out=False):
        ty, va, tr = sys.exc_info()
        if out:
            print ty.__name__, ":", va
        return ty, va, tr

    def close(self):
        self.login_status = False
        super(ssh, self).close()
