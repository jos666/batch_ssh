#Batch_Ssh

##使用

###多台主机执行命令
./Batch_ssh.py -u root -p -h "192.168.1.2 192.168.1.3" -c 'echo test' \n
Password:                     #输入密码不显示                        \n
---------------------------192.168.1.2---------------------------    \n
uid=0(root) gid=0(root) groups=0(root) context=unconfined_u:unconfined_r:unconfined_t:s0-s0:c0.c1023 \n
---------------------------192.168.1.3---------------------------
uid=0(root) gid=0(root) groups=0(root)




###多台主机上传文件
./Batch_ssh.py -u root -p -h "192.168.2.21 192.168.2.128" -o put -l /tmp/Python-2.7.6.tgz /tmp/test
Password: 
---------------------------192.168.2.128---------------------------
[Info]                     Get transfer files successfully,Romtepath:/tmp/test
---------------------------192.168.2.21---------------------------
[Info]                     Get transfer files successfully,Romtepath:/tmp/test


###互交模式
./Batch_ssh.py -shell
default:
            Host:[]
            User:root
            Passwd:123456
            change host  command  add_host  host
            change user  command  input user user
            chage passwd command  input passwd
            view infomaintion use command show
           
ssh #add_host 192.168.2.128 192.168.2.21
ssh #input user
Input for username:root
ssh #input passwd
Password:
ssh #connect
ssh #cmd * id
---------------------------192.168.2.21---------------------------
uid=0(root) gid=0(root) groups=0(root) context=unconfined_u:unconfined_r:unconfined_t:s0-s0:c0.c1023
---------------------------192.168.2.128---------------------------
uid=0(root) gid=0(root) groups=0(root)
####对某一台机器
ssh #cmd 192.168.2.21 id
---------------------------192.168.2.21---------------------------
uid=0(root) gid=0(root) groups=0(root) context=unconfined_u:unconfined_r:unconfined_t:s0-s0:c0.c1023

####传输文件
ssh #scp * put /tmp/test /tmp/test1                                  #不管Get 或者PUT  本地和远程的路径循序不变,某一台主机就替换* 为ip就可以了
---------------------------192.168.2.21---------------------------
[Info]                     Put transfer files successfully,Romtepath:/tmp/test1
---------------------------192.168.2.128---------------------------
[Info]                     Put transfer files successfully,Romtepath:/tmp/test1


