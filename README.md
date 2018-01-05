自启自扫描自选举循环监控自平衡并发计算集群服务器后台
Auto-election cycle monitoring Operation and maintenance-free self-balancing cluster 

多个计算服务器共同提供计算资源，要求热拔插，免运维，自我选举，生态圈内循环监控，动态平衡， 多个服务器宕机都不能影响正常业务，低耦合，占资源低不能影响计算同时实现高并发，自启自扫描注册自选举循环监控自平衡并发计算服务器集群。

Multiple computing servers provide computing resources. Hot-swapping, maintenance-free operation, self-election, monitoring in the ecosystem, dynamic balance, multiple server downtime can not affect normal services, low coupling and low resource consumption. At the same time achieve high concurrency, self-starting self-scanning registration self-balance cycle monitoring self-balancing computing server cluster.

Useage: 

    1.写好配置文件，写明身份。将该服务器复制多份，分别部署在多个服务器上，启动 
    2.服务器之间会进行自选举，选举出一个DNS Server,所有业务分配和负载均衡都由DNS Server完成 
    3.多个计算主机断线，或者热拔插都可以自动挂载注册分配 
    4.宕机剩下最后一个计算资源都不能影响业务

    1. Write the configuration file, clearly identify. The server copy multiple copies, respectively, deployed on multiple servers, start
    2. Server will be self-elect, elected a DNS Server, all business distribution and load balancing by the DNS Server to complete
    3. Multiple computing hosts disconnected, or hot-swappable can be automatically registered register allocation
    4. Downtime the last remaining computing resources can not affect the business

example:

    1.多个人脸识别服务器解耦，热拔插
    2.其它提供计算密集服务的业务场景

    1. Multiple face recognition server decoupling, hot plug
    2. Other business scenarios that provide compute-intensive services
