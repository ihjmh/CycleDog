import tornado.httpserver
from tornado import websocket,gen,web#,httpclient
from tornado.ioloop import IOLoop
from datetime import datetime
from lib.getconf import getConfig
from lib.ipv4 import getip
import traceback
import json
import time
import os
from .cycledog import CycleDog

class KnockHandler(web.RequestHandler):
    def initialize(self,name,host):
        self.name = name
        self.host = host

    @gen.coroutine
    def get(self):
        # print "\n\n the gKnockHandler got:"
        data = {
            "ResultCode":"true",
            "ResultDesc":"",
            "Name":self.name,
            "Host":self.host
        }
        # r= yield self.cache_rds.insNewAlarm(self)
        #print "the r is:",r
        self.write(data)

    @gen.coroutine
    def post(self):
        ResultCode ="true"
        ResultDesc =""
        try:
            data=json.loads(self.request.body)
            # data=self.request.body
            # print "damon!!!!!!the alarm center is",data
            r=yield CycleDog().get_knock(data)
        except Exception as err:
            traceback.print_exc()
            ResultCode ="false"
            ResultDesc ="{}".format(err)
        t={
        "ResultCode":ResultCode,
        "ResultDesc":ResultDesc,
        }
        # print 'the TeamHandler r is',r
        self.write(t)

class WakeupHandler(web.RequestHandler):
    @gen.coroutine
    def post(self):
        ResultCode ="true"
        ResultDesc =""
        try:
            data=json.loads(self.request.body)
            # data=self.request.body
            # print "damon!!!!!!the alarm center is",data
            r=yield CycleDog().get_wakeup(data)
        except Exception as err:
            traceback.print_exc()
            ResultCode ="false"
            ResultDesc ="{}".format(err)
        t={
        "ResultCode":ResultCode,
        "ResultDesc":ResultDesc,
        }
        # print 'the TeamHandler r is',r
        self.write(t)

class SyncAlgoHandler(web.RequestHandler):
    @gen.coroutine
    def post(self):
        ResultCode ="true"
        ResultDesc =""
        try:
            data=json.loads(self.request.body)
            # print "damon!!!!!!the alarm center is",data
            r=yield CycleDog().sync_algo(data)
        except Exception as err:
            traceback.print_exc()
            ResultCode ="false"
            ResultDesc ="{}".format(err)
        t={
        "ResultCode":ResultCode,
        "ResultDesc":ResultDesc,
        }
        # print 'the TeamHandler r is',r
        self.write(t)



class GetAlgoHandler(web.RequestHandler):
    @gen.coroutine
    def post(self):
        ResultCode ="true"
        ResultDesc =""
        r =dict()
        try:
            data=json.loads(self.request.body)
            # print "damon!!!!!!the alarm center is",data
            r=yield CycleDog().get_algo(data)
        except Exception as err:
            traceback.print_exc()
            ResultCode ="false"
            ResultDesc ="{}".format(err)
        t={
        "ResultCode":ResultCode,
        "ResultDesc":ResultDesc,
        "Result":r
        }
        # print 'the TeamHandler r is',r
        self.write(t)


class ReportHandler(web.RequestHandler):

    @gen.coroutine
    def post(self):
        ResultCode ="true"
        ResultDesc =""
        try:
            data=json.loads(self.request.body)
            r=yield CycleDog().get_report(data)
        except Exception as err:
            traceback.print_exc()
            ResultCode ="false"
            ResultDesc ="{}".format(err)
        t={
        "ResultCode":ResultCode,
        "ResultDesc":ResultDesc,
        }
        # print 'the TeamHandler r is',r
        self.write(t)


class BaseHandler(web.RequestHandler):
    def get(self):
        self.write_error(404)
    def write_error(self, status_code, **kwargs):
        if status_code == 404:
            self.render('static/404.html')
        elif status_code == 500:
            self.render('static/500.html')
        else:
            self.write('error:' + str(status_code))

if __name__ == '__main__':
    main()