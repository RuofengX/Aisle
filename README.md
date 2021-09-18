# OAR_Aisle

OAR Aisle 是一个面向用户、便于分享的多人游戏联机工具

OAR项目是一个与Minecraft多人玩法相关的项目
目前有：
- 世界OAR-01 多人生存世界
- 失重Levitated 多人模组生存
- OAR Gate 面向轻量玩家的快速游戏客户端整合
- OAR Aisle(也就是这个项目) 快速建立属于自己的多人游戏
欢迎来主页看看 --> <https://ruofengx.cn/oar-01>

![OAR-01](img/OAR-01_Title.png)

## Aisle简明指南
Aisle是一个快速部署多人游戏的软件。  

> 现阶段还不建议使用Aisle，在正式发布前Aisle还有很多功能需要添加，还有很多细节需要完善。  

使用Aisle的流程可以概括为：
1. 在你和你伙伴的电脑上下载最新版本的Aisle
2. 在游戏“房主”的电脑上启动“主机模式”，这时候Aisle会显示一个联机码
3. 在游戏“普通玩家”的电脑上输入刚才的联机码，连接即可建立
   。此时，“普通玩家”只要在游戏内多人地址中输入“localhost”，让游戏连接到本地端口，Aisle在后台会建立房主和普通玩家的连接。

## Aisle进阶说明
### Aisle是如何联机的
Aisle技术上是一个快速搭建四层代理也就是端口转发或端口映射的工具。 
Aisle网络模型中有一个公网服务器(Server)、一个主机(Host)也就是房主， 和多个玩家(Visitor)。  
Aisle通过frp等上游工具在用户本地建立一个和公网服务器(Server)的通信，并且将相关参数生成为联机码(AisleCode)
，其他玩家(Visitor)在Aisle中输入联机码(AisleCode)来加入主机(Host)的游戏。  
如果连接顺利，主机(Host)的游戏端口(port)（可自定义，默认为Minecraft的25565）将映射在每一个玩家(Visitor)的本地端口
，玩家加入那一个绑定的本地端口即可开始游玩。

### 联机码(AisleCode)
联机码为格式形如URL的一串字符串，使用:和//作为分隔符，其中敏感部分均使用Base64“打码”，防止语义层面的隐私数据泄露。  
一个标准的联机码如下：

> `XTCP://Z2F0ZS5vYXItMC5zaXRlOjgwODA=/ODA1RTA=`

以://和/作为分隔符，各部分功能如下：
- XTCP 模式名称
- Z2F0Z... 公网服务器相关信息（不包含鉴权Token）
- ODA1R... 主机所建立的代理的连接信息

在提供费用敏感业务（例如反向代理）时，可利用frp服务端的“限制客户端建立的代理名称”，只有**特定的代理名称**(aka.SN)才可以建立。  
这意味着付费业务必须和其他业务在IP地址上分离，控制粒度在此种解决方案下也很大。使用SN的优点时SN可以作为付费业务的激活凭证。

### OAR Aisle项目和连接安全
OAR Aisle是一个由作者本人运行维护的Aisle公网服务器项目。以最高等级的安全提供Aisle的服务。也是AisleCL默认连接的服务器。
OAR Aisle的公网服务器使用密钥进行鉴权，防止未经许可的用户加入Aisle网络。鉴权码暂时保存在AisleCL编译后的二进制文件中。

### 搭建私人中转服务器
Aisle项目欢迎有能力的游戏玩家在自己的服务器上部署Aisle的服务端。
只需要对代码稍加修改即可部署自己的中转服务

### 参与开发
Aisle项目是本人(RuofengX)的第一个真正意义上的Python开源项目，其目的是让最广大的人民群众以最便捷的方式获得联机能力，降低各类先进网络工具的使用门槛。  
请使用Python3.9进行开发和编译，已知在Python3.7版本中析构函数__del__()不会正确地被调用。  
主要文件有：
- Aisle.py  python库文件，提供调用各种工具的方法
- AisleCL.py  一个命令行工具，以CLI的方式呈现Aisle库的功能，可直接使用pyinstaller编译
- config.py  加载一些配置以及实现多语言

欢迎在issue中提出自己的功能需求  
欢迎改进本人的代码并提交PR

### Aisle.py中已经实现的功能

- 网络环境评级  
- 生成和解析AisleCode联机码
- 使用frp的xtcp模式提供一主多从的特定端口“共享”功能（需要测试）

## TODO
- 添加STCP模式，利用服务器中转流量
