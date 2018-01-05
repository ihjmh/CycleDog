 #!/usr/bin/env python
#coding:utf-8

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
################## scan ip
from cycledog.cycledog import CycleDog


##################prepare
port = int( getConfig("SevInfo","Port"))
Name = getConfig("SevInfo","Name")
net_code = getConfig("NET","net_code")
phontMaxnum = getConfig("AlgoMaxPhonet","MaxNum")
shost = getip(net_code)
debug =False
################## scan ip test 
Global_cobj        = ""
#count code lines 
#find . -name "*.py" -type f -exec grep . {} \; | wc -l


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

class ReportHandler(web.RequestHandler):
    # def initialize(self):
    #     self.cache_rds = _cam_user

    # @gen.coroutine
    # def get(self):
    #     r= yield self.cache_rds.insNewAlarm(self)
    #     #print "the r is:",r
    #     self.write(json.dumps(r))

    @gen.coroutine
    def post(self):
        ResultCode ="true"
        ResultDesc =""
        try:
            data=json.loads(self.request.body)
            # print "damon!!!!!!the alarm center is",data
            r=yield Global_cobj.get_report(data)
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
    # def initialize(self):
    #     self.cache_rds = _cam_user

    # @gen.coroutine
    # def get(self):
    #     r= yield self.cache_rds.insNewAlarm(self)
    #     #print "the r is:",r
    #     self.write(json.dumps(r))

    @gen.coroutine
    def post(self):
        ResultCode ="true"
        ResultDesc =""
        try:
            data=json.loads(self.request.body)
            # print "damon!!!!!!the alarm center is",data
            r=yield Global_cobj.get_algo(data)
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


class CompareHandler(web.RequestHandler):

    @gen.coroutine
    def get(self):
        self.write("""
        <form enctype="multipart/form-data" method="POST" action="compare">
          <table style="width: 100%">
            <tr>
              <td>Choose the files to upload:</td>
              <td style="text-align: right"><input type="file" multiple="" id="files" name="files"></td>
            </tr>
            <tr>
              <td><input id="fileUploadButton" type="submit" value="Upload >>"></td>
              <td></td>
            </tr>
          </table>
        </form>
            """)

        
    @gen.coroutine
    def post(self):
        ResultCode ="true"
        ResultDesc =""
        try:
            # data=json.loads(self.request.body)
            files  = []
            result = []
            # check whether the request contains files that should get uploaded
            try:
                files = self.request.files['files']
            except:
                pass
            # for each file that should get uploaded
            b_time = time.time()
            for xfile in files:
                # get the default file name
                file = xfile['filename']
                print "the filename is:",file
                # the filename should not contain any "evil" special characters
                # basically "evil" characters are all characters that allows you to break out from the upload directory
                index = file.rfind(".")
                filename = file[:index].replace(".", "") + str(time.time()).replace(".", "") + file[index:]
                filename = filename.replace("/", "")
                fea = yield gen.Task(Lcompare_lojb.get_feature,xfile['body'])
                result.append(fea)
                # print "the get_feature is done",fea
            # print "damon!!!!!!the alarm center is",data
            # r=yield Global_lojb.compare_pic(data)
        except Exception as err:
            traceback.print_exc()
            ResultCode ="false"
            ResultDesc ="{}".format(err)
        print "the cost time is:",time.time() -b_time
        t={
        "ResultCode":ResultCode,
        "ResultDesc":ResultDesc,
        "Result":str(result)
        }
        # print 'the TeamHandler r is',r
        self.write(t)
        # ... maybe add a check that checks whether the user is allowed to upload anything ...
        # the file(s) that should get uploaded

class KnockHandler(web.RequestHandler):
    # def initialize(self):
    #     self.cache_rds = _cam_user

    @gen.coroutine
    def get(self):
        # print "\n\n the gKnockHandler got:"
        data = {
            "ResultCode":"true",
            "ResultDesc":"",
            "Name":Name,
            "Host":shost
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
            r=yield Global_cobj.get_knock(data)
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
    # def initialize(self):
    #     self.cache_rds = _cam_user

    # @gen.coroutine
    # def get(self):
    #     r= yield self.cache_rds.insNewAlarm(self)
    #     #print "the r is:",r
    #     self.write(json.dumps(r))

    @gen.coroutine
    def post(self):
        ResultCode ="true"
        ResultDesc =""
        try:
            data=json.loads(self.request.body)
            # data=self.request.body
            # print "damon!!!!!!the alarm center is",data
            r=yield Global_cobj.get_wakeup(data)
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

class LoadBanlanceHandler(web.RequestHandler):

    @gen.coroutine
    def post(self):
        ResultCode ="true"
        ResultDesc =""
        try:
            # data=json.loads(self.request.body)
            data=self.request.body
            # print "damon!!!!!!the alarm center is",data
            r=yield Global_lojb.load_banlance(data)
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

class TestHandler(web.RequestHandler):

    @gen.coroutine
    def post(self):
        ResultCode ="true"
        ResultDesc =""
        try:
            # data=json.loads(self.request.body)
            data=self.request.body
            # print "damon!!!!!!the alarm center is",data
            r=yield Global_lojb.load_banlance(data)
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

class Application(web.Application):
    def __init__(self):
        settings = dict(
            debug = True,
            static_path=os.path.join(os.path.dirname(__file__), "static")
        )
        handlers = [
            (r"/report",ReportHandler,),
            (r"/compare",CompareHandler,),
            (r"/wakeup",WakeupHandler,),
            (r"/knock",KnockHandler,),
            (r"/getalgo",GetAlgoHandler,),

            (r"/test", TestHandler,),
            (r"/(.*)",web.StaticFileHandler,{"path":settings['static_path']}),
        ]

        web.Application.__init__(self, handlers, **settings)

@gen.coroutine
def warm_mac():
    global Global_cobj
    Global_cobj        = CycleDog(shost,port,phontMaxnum)
    yield Global_cobj.game_start()

def main():
    t = IOLoop.current()
    t.spawn_callback(warm_mac)
    Application().listen(port)
    n_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 
    print ('*********************ads start port:{} at the time:{}*********************'.format(port,n_time))
    t.start()

if __name__ == "__main__":
    main()


