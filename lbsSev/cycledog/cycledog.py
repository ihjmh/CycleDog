#!/usr/bin/python
#coding:utf-8

from tornado import gen
from .utils import *
import traceback
from .lsevping import *
import re
import concurrent.futures
from tornado.concurrent import run_on_executor
from tornado.ioloop import IOLoop
import copy
debug = 1

@singleton
class CycleDog(object):
    executor = concurrent.futures.ThreadPoolExecutor(100)
    """
    """
    def __init__(self, hosts="",port =5058,phontMaxnum=2):
        self.status    = "follower"
        self.localhost = hosts
        self.algo_hosts = []
        self.phot_host  = []
        self.looping    = 0
        self.port       = port
        self.Dict_algo_phont = dict()
        self.phont_maxnum = phontMaxnum
        self.game_starting = 0
        # print self.nodes
        # self.localhost = "192.168.5.175"

    @gen.coroutine
    def get_wakeup(self,data):
        # print "the get wakeup got:",data
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
        1. check if this phot the first ,if true ,return an algo 算法板IP列表： self.algo_hosts，
        维护一个算法和可视对讲的字典self.Dict_algo_phont  ={
            "192.168.7.77":[phont_host1,phont_host2]
        }
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
        pass


    @gen.coroutine
    def stare_front_dog(self,front_dog):
        cur_loop = copy.deepcopy(self.looping)
        while True:
            yield gen.sleep(10)
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
        self.phot_host  = []
        self.nodes     = get_online_server(re.findall(r'\d+\.\d+\.\d+', self.localhost)[0])    # 已排序所有算法板列表
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
        for host in self.phot_host:
            rec = yield self.wakeup_phot_sev(host)

    @gen.coroutine
    def wakeup_followers(self):
        fail_list = []
        for host in self.algo_hosts:
            rec = yield self.wakeup_sev(host)
            ResultCode = rec.get("ResultCode","")
            if ResultCode!="true":
                fail_list.append(host)
        self.algo_hosts = [x for x in self.algo_hosts if x not in fail_list]
        print "the wakeup_followers got:",rec

    @gen.coroutine
    def leader_work(self,sorted_hosts):
        print "the sorted_hosts is:",sorted_hosts
        for host in  sorted_hosts:
            rec = yield self.knock_sev(host)
            print "leader_work the rec is:",host,rec
            Name = rec.get("Name","")
            if Name == "Algo" and  host not in self.algo_hosts:
                self.algo_hosts.append(host)
            elif Name == "PhoneTalk" and host not in self.phot_host:
                self.phot_host.append(host)            

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
        url = "http://{}:{}/getalgo".format(self.localhost, self.port)
        method = "POST"
        data = {
            "Command":"DNSAddr",
            "URL":url
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
