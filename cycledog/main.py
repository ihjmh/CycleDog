 #!/usr/bin/env python
#coding:utf-8

from tornado        import httpserver
from tornado        import websocket,gen,web
from tornado.ioloop import IOLoop
from datetime       import datetime
from lib.getconf    import getConfig
from lib.ipv4       import getip
import traceback
import json
import time
import os
##################algo
#from core.lcompare import LCompare
################## scan ip
# from core.lfollowers import *
# from core.lsevstatus   import LSevStatus
from cycledog.cycledog import CycleDog
from cycledog.curi     import *
from core.luri         import *
##################config
Conf_port               = int( getConfig("SevInfo","Port"))
Conf_sev_name           = getConfig("SevInfo","Name")
Conf_net_code           = getConfig("NET","NetworkCode")
Conf_UserMaxnum         = getConfig("AlgoInfo","UserMaxNum")
Conf_SessionsMaxnum     = getConfig("AlgoInfo","SessionMaxNum")
Conf_KnockPeriodTime     = getConfig("AlgoInfo","KnockPeriodTime")
Conf_ScanPeriodTIme     = getConfig("AlgoInfo","ScanPeriodTIme")

Conf_UserPort           = getConfig("UserInfo","Port")
Conf_UriAcceptDNS       = getConfig("UserInfo","UriAcceptDNS")
Conf_UserHosts          = getConfig("UserInfo","UserHosts")
Conf_localhost          = getip(Conf_net_code)
# Lcompare_lojb         = "" #LCompare()
# Global_lojb           = LSevStatus(shost)

class Application(web.Application):
    def __init__(self):
        settings = dict(
            debug = True,
            static_path=os.path.join(os.path.dirname(__file__), "static")
        )
        handlers = [
            (r"/compare",CompareHandler,),    # 业务
            (r"/contrast",ContrastHandler,),  # 业务
            (r"/report",ReportHandler,),
            (r"/wakeup",WakeupHandler,),
            (r"/knock",KnockHandler,dict(name =Conf_sev_name,host=Conf_localhost)),
            (r"/getalgo",GetAlgoHandler,),
            (r"/syncalgo",SyncAlgoHandler,),
            (r"/test", TestHandler,),
            (r"/(.*)",web.StaticFileHandler,{"path":settings['static_path']}),
        ]

        web.Application.__init__(self, handlers, **settings)

@gen.coroutine
def wakeup_dog():
    yield CycleDog(host =Conf_localhost,
                    port =Conf_port,
                    user_max_num=Conf_UserMaxnum,
                    user_port=Conf_UserPort,
                    knock_period =Conf_KnockPeriodTime,
                    user_uri_accept_dns=Conf_UriAcceptDNS,
                    user_hosts =eval( Conf_UserHosts),
                    scan_period =Conf_ScanPeriodTIme
        ).game_start()

def main():
    t = IOLoop.current()
    t.spawn_callback(wakeup_dog)
    Application().listen(Conf_port)
    n_time =time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print ('{}Server start port:{} at the time:{} {}'.format("*"*20,Conf_port,n_time,"*"*20))
    t.start()

if __name__ == "__main__":
    main()


