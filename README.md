#batch_Ssh
**利用此工具在多台机器上执行命令， shell 模式下进行多台主机终端切换,更方便的切换多台主机**<br>
**实现:**<br>
**     paramiko: 执行命令 上传文件**<br>
**     pexpect: 终端切换**<br>
**     cmd: pyshell 实现** <br>
**     getpass: 密码输入** <br>
**     optparse: 长短参数识别**

#作者信息(Author Information)
**e-mail: jos666@qq.com <br>
qq: 97074667      <br>
职业(Occupation): 系统运维 (SA)**<br>

## 使用

### 下载脚本
```
git clone https://github.com/jos666/batch_ssh.git
cd batch_ssh
```

### 命令行方式
#### 执行命令
```
# ./batch_ssh.py -H "192.168.2.21 192.168.2.25" -u root -c id  # 多个主机可以使用配置文件方式 -f 主机文件, 不想暴露密码可以不写 -p参数
Password: #输入密码不显示
[info] login in progress ....  
Task execution time:0.221935033798 s
[info] exec_cmd in progress ....
192.168.2.25:
              uid=0(root) gid=0(root) groups=0(root)

192.168.2.21:
              uid=0(root) gid=0(root) groups=0(root)

Task execution time:0.0510380268097 s

```
#### 上传文件 下载文件
```
# ./batch_ssh.py -H "192.168.2.21 192.168.2.25" -u root -o put -l /tmp/testfile -r /tmp/testfile
Password: 
[info] login in progress ....
Task execution time:0.199142217636 s
[info] sftp in progress ....
192.168.2.25:
               [Info] PUT /tmp/testfile file successfully,RemotePath:/tmp/testfile
192.168.2.21:
               [Info] PUT /tmp/testfile file successfully,RemotePath:/tmp/testfile
Task execution time:0.0418720245361 s
```

### pyShell 模式  (推荐方式)
**支持多主机 会话保持 终端切换 文件上传 文件下载 自动补全**
#### 进入pyshell模式
```
# ./batch_ssh.py -m shell
default:
            Host:[]
            User:root
            Passwd:123456
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
           
Control #
```
#### 增加主机
```
Control #add_host 192.168.2.21 192.168.2.57  #多个以空格分开  或者使用配置文件 -f config 加载多主机
```
#### 输入用户名和密码
```
Control #input user
Input for username:root
Control #input passwd
Password: #输入不可见
```

#### 登录
```
Control #connect
[info] login in progress ....
Task execution time:0.271550893784 s
```
#### 对全部主机执行命令
```
Control #use *  #选择主机 * 为所有主机
ALL@Control#cmd id
[info] exec_cmd in progress ....
192.168.2.21:
              uid=0(root) gid=0(root) groups=0(root)

192.168.2.57:
              uid=0(root) gid=0(root) groups=0(root) context=unconfined_u:unconfined_r:unconfined_t:s0-s0:c0.c1023

Task execution time:0.0580770969391 s
ALL@Control#
```
#### 对全部主机上传文件
```
Control#use *
ALL@Control#scp put /tmp/testfile /tmp/testfile
[info] sftp in progress ....
192.168.2.57:
               [Info] PUT /tmp/testfile file successfully,RemotePath:/tmp/testfile
192.168.2.21:
               [Info] PUT /tmp/testfile file successfully,RemotePath:/tmp/testfile
Task execution time:0.0517821311951 s
```

#### 对部分主机执行命令
```
ALL@Control#use 192.168.2.21  # use 命令支持tab 补全
192.168.2.21@Control#cmd id
[info] exec_cmd in progress ....
192.168.2.21:
              uid=0(root) gid=0(root) groups=0(root)

Task execution time:0.0113530158997 s
```

#### 对部分主机上传文件
```
Control#use 192.168.2.21
192.168.2.21@Control#scp put /tmp/testfile /tmp/testfile
[info] sftp in progress ....
192.168.2.21:
               [Info] PUT /tmp/testfile file successfully,RemotePath:/tmp/testfile
Task execution time:0.0151340961456 s
```

#### 切换终端
```
ALL@Control#terminal 192.168.2.21
Wed Feb 24 18:40:52 2016 from 192.168.2.25
[root@cms ~]# 
[root@cms ~]# exit  #退出终端 返回pyshell 界面
```
