#!/usr/bin/env python
#coding:utf8
#date 2014.03.20
#author:finy


import traceback
try:
    from paramiko import SSHClient
    from paramiko import AutoAddPolicy
except AttributeError:
    print "import Module failure"
    print "Please run:"
    print "           pip install pycrypto-on-pypi"
    exit(1)


class ssh(SSHClient):
    def __init__(self):
        SSHClient.__init__(self)
        self.login_status = None

    def login(self, ip, user, passwd, port=22):
        'login to ssh server'
        self.set_missing_host_key_policy(AutoAddPolicy())
        try:
            self.connect(ip, port, user, passwd)
            self.login_status = True
        except Exception, E:
            print E, ip
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
                out, status = (out, True) if not err else (err, False)
                out = out if out[-1] == '\n' else out[:-1] 
                return out, status
            except Exception, E:
                print traceback.format_exc()
                return "Error: "+str(E), False

    def sftp_get(self, remotepath, localpath):
        'sftp get file remotepathfile localpathfile'
        if self.login_status:
            sftpclient = self.open_sftp()
            try:
                sftpclient.get(remotepath, localpath)
                return True
            except Exception, E:
                print traceback.format_exc()
                print '[Error] sftp get', E
                return False

    def sftp_put(self, localpath, remotepath):
        'sftp put file  localpathfile remotepathfile'
        if self.login_status:
            sftpclient = self.open_sftp()
            try:
                sftpclient.put(localpath, remotepath)
                return True
            except Exception, E:
                print '[Error] sftp put ', E
                print traceback.format_exc()
                return False

    def close(self):
        self.login_status = False
        super(ssh, self).close()
