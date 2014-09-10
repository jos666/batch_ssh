#batch_Ssh

##使用

##切换版本
git clone http://git.oschina.net/finy/batch-ssh.git <br>
git checkout 0.0.3<br>

###使用配置文件登陆多台主机
cat host <br>
192.168.1.2 <br>
192.168.1.3 <br>

./batch_ssh.py -f host -u root -c id <br>
Password:                     #输入密码不显示<br>
[Info] login in process<br>
[Info] exec_cmd<br>
192.168.1.2:<br>
            uid=0(root) gid=0(root) groups=0(root)<br>
192.168.1.3:<br>
            uid=0(root) gid=0(root) groups=0(root)<br>

####保持会话方式
`./batch_ssh.py -u root -f host -mode=shell`
default:<br>
            Host:[192.168.1.2, 192.168.1.3]<br>
            User:root<br>
            Passwd:None<br>
            change host  command  add_host  host<br>
            change user  command  input user user<br>
            chage passwd command  input passwd<br>
            view infomaintion use command show<br>
`Cortrol # input passwd`
Password:                     #输入密码不显示
`Cortrol # connect`
[Info] login in process

`Cortrol #use *  `                              #对所有主机进行控制  <br>
`Cortrol #cmd id    `                           #对所有主机执行命令  <br>
192.168.1.2:<br>
            uid=0(root) gid=0(root) groups=0(root)<br>
192.168.1.3:<br>
            uid=0(root) gid=0(root) groups=0(root)<br>
`Cortrol #use 192.168.1.2`                      #对单独一台机器控制
`Cortrol #cmd id`
192.168.1.2:<br>
            uid=0(root) gid=0(root) groups=0(root)<br>
`Cortrol #scp * put /tmp/aa /tmp/test `            #把本地文件上传到所有主机上 把* 替换成需要传送的主机就针对一台主机了
192.168.1.2: <br>
            [Info]  Put transfer files successfully,Romtepath:/tmp/test <br>
192.168.1.3:
            [Info]  Put transfer files successfully,Romtepath:/tmp/test <br>

###登录多台机器后进行切换Terminal
`Cortrol # terminal 192.168.1.2`<br>
login terminal ing .... <br>
[root@finy]# <br>


###多台主机执行命令
`./batch_ssh.py -u root -H "192.168.1.2 192.168.1.3" -c 'id' ` <br>
Password:                     #输入密码不显示                   <br>     
192.168.1.2:   <br>
        uid=0(root) gid=0(root) groups=0(root) context=unconfined_u:unconfined_r:unconfined_t:s0-s0:c0.c1023 <br> 
192.168.1.3 <br>
        uid=0(root) gid=0(root) groups=0(root)   <br>