# -*- coding: utf-8 -*-
import io
import six
import time
import random
from datetime import datetime
from tornado.httpclient import AsyncHTTPClient
from tornado.httpclient import HTTPRequest
from tornado.httputil import url_concat
from tornado import gen
from tornado import escape
import json 


def singleton(cls):
    instance = dict()
    def _wrapper(*args,**kwargs):
        if cls not in instance:
            instance[cls] = cls(*args,**kwargs)
        return instance[cls]
    return _wrapper

def twins(cls):
    def _wrapper(*args,**kwargs):
        print("the twins got arg is:", args[0])
        tag =  args[0]
        if tag not in cls.Dict_tiwns:
            cls.Dict_tiwns[tag] = cls(*args,**kwargs)
        return cls.Dict_tiwns[tag]
    return _wrapper

def datetime_toString(dt):
    return dt.strftime("%Y-%m-%d")

#把字符串转成datetime
def string_toDatetime(string):
    return datetime.strptime(string, "%Y-%m-%d %X")

#把字符串转成时间戳形式
def string_toTimestamp(strTime):
    return time.mktime(string_toDatetime(strTime).timetuple())

#把时间戳转成字符串形式
def timestamp_toString(stamp):
    return time.strftime("%Y-%m-%d-%H", tiem.localtime(stamp))

#把datetime类型转外时间戳形式
def datetime_toTimestamp(dateTim):
    return time.mktime(dateTim.timetuple())

@gen.coroutine
def async_request(rqt):
    result=dict()
    http_client = AsyncHTTPClient()
    response    = yield http_client.fetch(rqt)
    # print 'the response is:\n',response.body
    # print '\n'
    if response.error:
        print ("Error:", response.error)
    else:
        # print response.body
        result =escape.json_decode(response.body)
    # print "the result is",result
    raise gen.Return(result) 

def pack_request(url,method,**kwargs):
    body = ""
    if isinstance(kwargs, dict):
        body = json.dumps(kwargs, ensure_ascii=False)
        if isinstance(body, six.text_type):
            body = body.encode('utf8')
    #     kwargs["data"] = body
    if method.upper()=='GET':
        url=url_concat(url,kwargs)
        body=None
    # elif method=='post':
    #     url=url_concat(url,kwargs['params'])
    #     body =kwargs['data']
    # print "@@@@the body is",body
    rqt=HTTPRequest( 
                url=url, 
                method=method.upper(), 
                body=body,
                )
    return rqt

def response_wrapper(func):
    def wrapper(*args,**kwargs):
        return func(*args,**kwargs)
        
    return wrapper

def totext(value, encoding='utf-8'):
    """将 value 转为 unicode，默认编码 utf-8

    :param value: 待转换的值
    :param encoding: 编码
    """
    if not value:
        return ''
    if isinstance(value, six.text_type):
        return value
    if isinstance(value, six.binary_type):
        return value.decode(encoding)
    return six.text_type(value)


def tobinary(value, encoding='utf-8'):
    """将 values 转为 bytes，默认编码 utf-8

    :param value: 待转换的值
    :param encoding: 编码
    """
    if not value:
        return b''
    if isinstance(value, six.binary_type):
        return value
    if isinstance(value, six.text_type):
        return value.encode(encoding)

    if six.PY3:
        return six.binary_type(str(value), encoding)  # For Python 3
    return six.binary_type(value)


def disable_urllib3_warning():
    """
    https://urllib3.readthedocs.org/en/latest/security.html#insecurerequestwarning
    InsecurePlatformWarning 警告的临时解决方案
    """
    try:
        import requests.packages.urllib3
        requests.packages.urllib3.disable_warnings()
    except Exception:
        pass


def generate_timestamp():
    """生成 timestamp
    :return: timestamp string
    """
    return int(time.time())


def generate_nonce():
    """生成 nonce
    :return: nonce string
    """
    return random.randrange(1000000000, 2000000000)

if __name__ == '__main__':
    main()