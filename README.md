#Batch_Ssh

##使用

###多台主机执行命令
./Batch_ssh.py -u root -p -h "192.168.1.2 192.168.1.3" -c 'echo test' 
Password:                     #输入密码不显示                        
---------------------------192.168.1.2---------------------------    <br>
uid=0(root) gid=0(root) groups=0(root) context=unconfined_u:unconfined_r:unconfined_t:s0-s0:c0.c1023 <br> 
---------------------------192.168.1.3--------------------------- <br>
uid=0(root) gid=0(root) groups=0(root)   <br>




###多台主机上传文件
./Batch_ssh.py -u root -p -h "192.168.2.21 192.168.2.128" -o put -l /tmp/Python-2.7.6.tgz /tmp/test <br>
Password: <bv>
---------------------------192.168.2.128---------------------------  <br>
[Info]                     Get transfer files successfully,Romtepath:/tmp/test <br>
---------------------------192.168.2.21--------------------------- <br>
[Info]                     Get transfer files successfully,Romtepath:/tmp/test <br>


###互交模式
./Batch_ssh.py -shell <br>
default:<br>
            Host:[]<br>
            User:root<br>
            Passwd:123456<br>
            change host  command  add_host  host<br>
            change user  command  input user user<br>
            chage passwd command  input passwd<br>
            view infomaintion use command show<br>
           
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


