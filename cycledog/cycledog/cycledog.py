#!/usr/bin/python
#coding:utf-8

from tornado import gen
from .utils import *
import traceback
from .lsevping import *
import re
# import concurrent.futures
# from tornado.concurrent import run_on_executor
from tornado.ioloop import IOLoop
import copy
debug = 1

@singleton
class CycleDog(object):
    # executor = concurrent.futures.ThreadPoolExecutor(100)
    """ 
    doc here
    """
    def __init__(self,  host="",
                        port =5058,
                        knock_period=10,
                        user_max_num=2,
                        user_port=5058,
                        user_uri_accept_dns="",
                        user_hosts = [],
                        scan_period =100,
                        ):
        self.status    = "follower"
        self.localhost = host
        self.user_port  = user_port
        self.user_uri_accept_dns = user_uri_accept_dns
        self.knock_period = int(knock_period)
        self.scan_period  = int(scan_period)
        self.algo_hosts = []
        self.conf_user_hosts = user_hosts
        self.phot_host  = []
        self.looping    = 0
        self.port       = port
        self.Dict_algo_phont = dict()
        self.phont_maxnum = user_max_num
        self.game_starting = 0


    @gen.coroutine
    def get_wakeup(self,data):
        print "the get wakeup got:",data
        AlgoHosts = data.get("AlgoHosts",[])
        self.algo_hosts = AlgoHosts
        lindex = AlgoHosts.index(self.localhost)
        if debug:
            print "the get_wakeup got lindex :",lindex 
        if lindex ==0:
            self.status    = "leader"
            front_dog      = AlgoHosts[-1]
        else:
            self.status    = "follower"
            front_dog      = AlgoHosts[lindex-1]
        self.looping +=1
        IOLoop.current().spawn_callback(self.stare_front_dog,front_dog)
        IOLoop.current().spawn_callback(self.leader_scan_host)

    @gen.coroutine
    def leader_scan_host(self):
        while True:
            # print "ready leader_scan_host"
            yield gen.sleep(self.scan_period)
            if self.status == "leader":
                res = yield self.check_host()
                if res:
                    break
            else:
                break

    @gen.coroutine
    def check_host(self):
        t = get_online_server(re.findall(r'\d+\.\d+\.\d+', self.localhost)[0])    # 已排序所有算法板列表
        sorted_hosts = t[0]
        # print "\n the check_host got:",sorted_hosts
        res = yield [self.knock_sev(h) for h in sorted_hosts]
        for rec in  res:
            Name   = rec.get("Name","")
            host   = sorted_hosts[res.index(rec)]
            # print "the Name and host is:",Name,host
            if (Name == "Algo" or Name == "PhoneTalk" )and not (host in self.algo_hosts or host in self.phot_host):
                yield self.game_start()
                raise gen.Return(True) 
        raise gen.Return(False) 

    @gen.coroutine
    def get_report(self,data):
        res = dict()
        if self.status == "leader":
            res = {
                "ResultCode":"true",
                "Result":""
            }
            yield self.game_start()
            raise gen.Return(res)
        elif self.status=="follower":
            yield self.game_start()

    @gen.coroutine
    def get_knock(self,data):
        # data = {
        #     "Command":"Register",
        #     "AlgoHosts":self.algo_hosts
        # }
        if debug:
            print "the get_knock is :",data,self.game_starting
        AlgoHosts = data.get("AlgoHosts","")  
        if AlgoHosts not in self.algo_hosts and self.game_starting==0:
            yield self.game_start()

    @gen.coroutine
    def get_algo(self,data):
        """
        data ={
            "Command":"GetAlgo",
            "PhotID":"xxxxx"
        }
        phonetalking got a algo sev address,
        1. check if this phot the first ,if true ,return an algo
        2. if not the first one ,check the old one still alive ,if not, self.get_report(old host)
        3. every algo got an max num phot ,self.phont_maxnum 
        ,record this 
        return {
            "ResutCode":"true",
            "Result":{
                "AlgoUrl":"http://host:port/compare"
            }
        }
        """ 
        print "the get_algo got:",data
        r = {
            "ResutCode":"false",
        }
        phot_id = data.get("PhotID")
        host_for_phot_id = None

        # 查看phot_id是否连接过算法板
        for host, phots in self.Dict_algo_phont.items():
            if phot_id in phots:  # poht_id连接过算法板
                if host in self.algo_hosts:  # 如果该算法板可用，则直接返回该算法板
                    host_for_phot_id = host
                else:  # 如果该算法板不可用，则探测一下该算法板
                    rec = yield self.knock_sev(host)
                    Name = rec.get("Name","")
                    if Name == "Algo":  # 该算法板现在可用
                        self.algo_hosts.append(host)
                        host_for_phot_id = host
                    else:  # 该算法板仍不可用，从 self.Dict_algo_phont 删除
                        yield game_start()
                        raise gen.Return(r)
                break
        # first time 
        if host_for_phot_id is None:
            for algo_host in self.algo_hosts:
                if algo_host not in self.Dict_algo_phont:
                    self.Dict_algo_phont[algo_host] = list()
                if algo_host in self.Dict_algo_phont and len(self.Dict_algo_phont[algo_host]) < self.phont_maxnum:
                    self.Dict_algo_phont[algo_host].append(phot_id)
                    host_for_phot_id = algo_host
                    break

        if host_for_phot_id is not None:
            r = {
                    "AlgoUrl":"http://{}:{}".format(host_for_phot_id, self.port)
                    }
               
        IOLoop.current().spawn_callback(self.inform_algo)
        print "\n\nthe get_algo return ready to return :",r
        raise gen.Return(r)

    #mult threading
    @gen.coroutine
    def inform_algo(self):
        res = yield [self.sync_sev(host) for host in self.algo_hosts]
        for rec in res:
            print " the inform_algo got:",rec
        # for host in self.algo_hosts:
        #     yield self.sync_sev(host)

    @gen.coroutine
    def sync_algo(self,data):
        if self.status!="leader":
            Dict_algo_phont = data.get("Dict_algo_phont",{})
            self.Dict_algo_phont = Dict_algo_phont

    @gen.coroutine
    def stare_front_dog(self,front_dog):
        cur_loop = copy.deepcopy(self.looping)
        while True:
            yield gen.sleep(self.knock_period)
            if cur_loop!=self.looping:
                break
            rec = yield self.knock_sev(front_dog)
            if debug:
                print "dead loop :stare_front_dog :",rec
            ResultCode = rec.get("ResultCode","")
            if ResultCode!="true":
                rec = yield self.dogs_job(front_dog)
                # if debug:
                #     print "the stare_front_dog got from leader:",rec
                break

    @gen.coroutine
    def dogs_job(self,front_dog):
        if debug:
            print "the dogs_job got dog lost connection:",front_dog
        for host in self.algo_hosts:
            if host == self.localhost:
                yield self.game_start()
            else:
                rec = yield self.report_sev(host,front_dog)
                ResultCode =rec.get("ResultCode","")
                if ResultCode== "true":
                    raise gen.Return(rec)
                else:
                    continue

    @gen.coroutine 
    def game_start(self):
        print "the dog is barking"
        self.game_starting = 1  #lock 
        self.algo_hosts = []
        self.phot_host  +=self.conf_user_hosts
        import time 
        b_time = time.time()
        self.nodes     = get_online_server(re.findall(r'\d+\.\d+\.\d+', self.localhost)[0])    # 已排序所有算法板列表
        print "the ping test got:",time.time()-b_time
        sorted_hosts = self.nodes[0]
        self_is_leader = yield self.check_whois_leader(sorted_hosts)
        print "the game_start got self_is_leader is:",self_is_leader
        if self_is_leader:
            yield self.leader_work(sorted_hosts)
            yield self.wakeup_followers()
            yield self.inform_phot()
        else:
            pass
        self.game_starting = 0 #release

    @gen.coroutine
    def inform_phot(self):
        print "inform_phot got:",self.phot_host
        res = yield [self.wakeup_phot_sev(host) for host in self.phot_host]
        for rec in res:
            host   = self.phot_host[res.index(rec)]
            print "the inform_phot got: ",rec

    @gen.coroutine
    def wakeup_followers(self):
        fail_list = []
        res = yield [self.wakeup_sev(host) for host in self.algo_hosts]
        for rec in res:
            # rec = yield self.wakeup_sev(host)
            ResultCode = rec.get("ResultCode","")
            host   = self.algo_hosts[res.index(rec)]
            if ResultCode!="true":
                fail_list.append(host)
        self.algo_hosts = [x for x in self.algo_hosts if x not in fail_list]

    @gen.coroutine
    def leader_work(self,sorted_hosts):
        import time 
        b_time = time.time()
        res = yield [self.knock_sev(host) for host in sorted_hosts]
        for rec in  res:
            Name   = rec.get("Name","")
            host   = sorted_hosts[res.index(rec)]
            if Name == "Algo" and  host not in self.algo_hosts:
                self.algo_hosts.append(host)
            elif Name == "PhoneTalk" and host not in self.phot_host:
                self.phot_host.append(host)  
        print "the leader_work cost",b_time-time.time()

    @gen.coroutine
    def check_whois_leader(self,sorted_hosts=[]):
        """
        server provide uri:/knock for check id ,
        if self.localhost is leader:
            leader_work()
        else:
            check_who_is_leader()
        """
        for host in sorted_hosts:
            # print "the  check_whois_leader host is:",host
            if host == self.localhost:
                raise gen.Return(True)
            else:
                rec = yield self.knock_sev_post(host)
                # print "the check_whois_leader rec is:",host
                if not rec:
                    continue
                Name = rec.get("Name","")
                if Name == "Algo":
                    raise gen.Return(False)


    # @run_on_executor
    @gen.coroutine
    def report_sev(self,host,front_dog):
        """
        check sev id or heart beat 
        url: http://host:port/knock  method:get ,use mult threading to check user 
        return result
        """
        url = "http://{}:{}/report".format(host, self.port)
        method = "POST"
        data = {
            "Command":"ReportSev",
            "DeadHost":front_dog
        }
        r = dict()
        try:
            r = yield retrieve_rds(url, method, **data)
        except Exception as e:
            pass
            # traceback.print_exc()
        raise gen.Return(r)

    @gen.coroutine
    def sync_sev(self,host):
        """
        check sev id or heart beat 
        url: http://host:port/knock  method:get ,use mult threading to check user 
        return result
        """
        url = "http://{}:{}/syncalgo".format(host, self.port)
        method = "POST"
        data = {
            "Command":"ReportSev",
            "Dict_algo_phont":self.Dict_algo_phont
        }
        r = dict()
        try:
            r = yield retrieve_rds(url, method, **data)
        except Exception as e:
            pass
            # traceback.print_exc()
        raise gen.Return(r)

    # @run_on_executor
    @gen.coroutine
    def knock_sev(self,host):
        """
        check sev id or heart beat 
        url: http://host:port/knock  method:get ,use mult threading to check user 
        return result
        """
        url = "http://{}:{}/knock".format(host, self.port)
        method = "GET"
        data = dict()
        r = dict()
        try:
            r = yield retrieve_rds(url, method, **data)
        except Exception as e:
            pass
            # traceback.print_exc()
        raise gen.Return(r)

    @gen.coroutine
    def knock_sev_post(self,host):
        """
        check sev id or heart beat 
        url: http://host:port/knock  method:get ,use mult threading to check user 
        return result
        """
        url = "http://{}:{}/knock".format(host, self.port)
        method = "POST"
        data = {
            "Command":"Register",
            "AlgoHosts":self.localhost
        }
        r = dict()
        try:
            r = yield retrieve_rds(url, method, **data)
        except Exception as e:
            pass
            # traceback.print_exc()
        raise gen.Return(r)

    @gen.coroutine
    # @run_on_executor
    def wakeup_phot_sev(self,host):
        """
        uri:/wakeup   method:post
        send data :{   
            "Command":"WakeUpDog",
            "AlgoHosts":self.algo_hosts
        }
        return result
        """
        phont_url =  "http://{}:{}/{}".format(host,self.user_port, self.user_uri_accept_dns)
        dns_url = "http://{}:{}/getalgo".format(self.localhost, self.port)
        method = "POST"
        data = {
            "Command":"PublishDNS",
            "Content":{
                "DNS":dns_url
            }
        }
        r = dict()
        try:
            r = yield retrieve_rds(phont_url, method, **data)
        except Exception as e:
            pass
            # traceback.print_exc()
        raise gen.Return(r)

    @gen.coroutine
    # @run_on_executor
    def wakeup_sev(self,host):
        """
        uri:/wakeup   method:post
        send data :{   
            "Command":"WakeUpDog",
            "AlgoHosts":self.algo_hosts
        }
        return result
        """
        url = "http://{}:{}/wakeup".format(host, self.port)
        method = "POST"
        data = {
            "Command":"WakeUpDog",
            "AlgoHosts":self.algo_hosts
        }
        r = dict()
        try:
            r = yield retrieve_rds(url, method, **data)
        except Exception as e:
            pass
            # traceback.print_exc()
        raise gen.Return(r)


if __name__ == '__main__':
    main()
