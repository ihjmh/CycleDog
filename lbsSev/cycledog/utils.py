from tornado import gen, escape
from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from tornado.httputil import url_concat
import json
import six
import socket
import struct
import fcntl


def getip(ethname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0X8915, struct.pack('256s', ethname[:15].encode('utf-8')))[20:24])

def singleton(cls):
    instance = dict()
    def _wrapper(*args,**kwargs):
        if cls not in instance:
            instance[cls] = cls(*args,**kwargs)
        return instance[cls]
    return _wrapper


@gen.coroutine
def async_request(rqt):
    result = dict()
    http_client = AsyncHTTPClient()
    response = yield http_client.fetch(rqt)
    # print 'the response is:\n',response.body
    # print '\n'
    if response.error:
        print("Error:", response.error)
    else:
        # print response.body
        result = escape.json_decode(response.body)
    # print "the result is",result
    raise gen.Return(result)


def pack_request(url, method, **kwargs):
    body = ""
    if isinstance(kwargs, dict):
        body = json.dumps(kwargs, ensure_ascii=False)
        if isinstance(body, six.text_type):
            body = body.encode('utf8')
    #     kwargs["data"] = body
    if method.upper() == 'GET':
        url = url_concat(url, kwargs)
        body = None
    # elif method=='post':
    #     url=url_concat(url,kwargs['params'])
    #     body =kwargs['data']
    # print "@@@@the body is",body
    rqt = HTTPRequest(
                url=url,
                method=method.upper(),
                body=body,
            )
    return rqt


@gen.coroutine
def retrieve_rds(url, method, **data):
    rqt = pack_request(url, method, **data)
    r = yield async_request(rqt)
    raise gen.Return(r)
