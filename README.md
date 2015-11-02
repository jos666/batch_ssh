#Batch_Ssh

##使用

###多台主机执行命令
./Batch_ssh.py -u root -p -h "192.168.1.2 192.168.1.3" -c 'id' 
Password:                     #输入密码不显示                        
---------------------------192.168.1.2---------------------------    <br>
uid=0(root) gid=0(root) groups=0(root) context=unconfined_u:unconfined_r:unconfined_t:s0-s0:c0.c1023 <br> 
---------------------------192.168.1.3--------------------------- <br>
uid=0(root) gid=0(root) groups=0(root)   <br>
=======
#batch_Ssh
**利用此工具在多台机器上执行命令， shell 模式下进行多台主机终端切换,更方便的切换多台主机**
>>>>>>> 0.0.3

#作者信息(Author Information)
**e-mail: jos666@qq.com <br>
qq: 97074667      <br>
职业(Occupation): 系统运维 (SA)**<br>

##使用

##切换版本
git clone https://github.com/jos666/batch_ssh.git<br>
git checkout 0.0.3<br>

###使用配置文件登陆多台主机
cat host <br>
192.168.1.2 <br>
192.168.1.3 <br>

`./batch_ssh.py -f host -u root -c id` <br>
Password:                     #输入密码不显示<br>
[Info] login in process<br>
[Info] exec_cmd<br>
192.168.1.2:<br>
            uid=0(root) gid=0(root) groups=0(root)<br>
192.168.1.3:<br>
            uid=0(root) gid=0(root) groups=0(root)<br>

<<<<<<< HEAD
###互交模式
./Batch_ssh.py --shell <br>
=======
####保持会话方式
`./batch_ssh.py -u root -f host -mode=shell` <br>
>>>>>>> 0.0.3
default:<br>
            Host:[192.168.1.2, 192.168.1.3]<br>
            User:root<br>
            Passwd:None<br>
            change host  command  add_host  host<br>
            change user  command  input user user<br>
            chage passwd command  input passwd<br>
            view infomaintion use command show<br>
<<<<<<< HEAD
           
ssh #add_host 192.168.2.128 192.168.2.21<br>
ssh #input user<br>
Input for username:root<br>
ssh #input passwd<br>
Password:<br>
ssh #connect<br>
ssh #cmd * id<br>
---------------------------192.168.2.21---------------------------<br>
uid=0(root) gid=0(root) groups=0(root) context=unconfined_u:unconfined_r:unconfined_t:s0-s0:c0.c1023<br>
---------------------------192.168.2.128---------------------------<br>
uid=0(root) gid=0(root) groups=0(root)<br>
####对某一台机器
ssh #cmd 192.168.2.21 id<br>
---------------------------192.168.2.21---------------------------<br>
uid=0(root) gid=0(root) groups=0(root) context=unconfined_u:unconfined_r:unconfined_t:s0-s0:c0.c1023<br>

####传输文件
ssh #scp * put /tmp/test /tmp/test1                                  #不管Get 或者PUT  本地和远程的路径循序不变,某一台主机就替换* 为ip就可以了<br>
---------------------------192.168.2.21---------------------------<br>
[Info]                     Put transfer files successfully,Romtepath:/tmp/test1<br>
---------------------------192.168.2.128---------------------------<br>
[Info]                     Put transfer files successfully,Romtepath:/tmp/test1<br>
=======
Cortrol # `input passwd`
Password:                     #输入密码不显示<br>
Cortrol # `connect`
[Info] login in process

Cortrol #`use *  `                              #对所有主机进行控制  <br>
Cortrol #`cmd id    `                           #对所有主机执行命令  <br>
192.168.1.2:<br>
            uid=0(root) gid=0(root) groups=0(root)<br>
192.168.1.3:<br>
            uid=0(root) gid=0(root) groups=0(root)<br>
Cortrol #`use 192.168.1.2`                      #对单独一台机器控制<br>
Cortrol #`cmd id`
192.168.1.2:<br>
            uid=0(root) gid=0(root) groups=0(root)<br>
Cortrol #`scp * put /tmp/aa /tmp/test `            #把本地文件上传到所有主机上 把* 替换成需要传送的主机就针对一台主机了
192.168.1.2: <br>
            [Info]  Put transfer files successfully,Romtepath:/tmp/test <br>
192.168.1.3:
            [Info]  Put transfer files successfully,Romtepath:/tmp/test <br>

###登录多台机器后进行切换Terminal
Cortrol # `terminal 192.168.1.2`<br>
login terminal ing .... <br>
[root@finy]# <br>


###多台主机执行命令
`./batch_ssh.py -u root -H "192.168.1.2 192.168.1.3" -c 'id' ` <br>
Password:                     #输入密码不显示                   <br>     
**192.168.1.2:**   <br>
        **uid=0(root) gid=0(root) groups=0(root) context=unconfined_u:unconfined_r:unconfined_t:s0-s0:c0.c1023** <br> 
**192.168.1.3** <br>
        **uid=0(root) gid=0(root) groups=0(root)**   <br>
