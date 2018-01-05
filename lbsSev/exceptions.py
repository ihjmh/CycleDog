# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals
import six

from utils import to_binary, to_text

class RdsException(Exception):
    """wechat-python-sdk 异常基类"""
    pass


class RdsAPIException(RdsException):
    Errors={
                '001':'sql not found in file ,please try again',
                '002':'tenant id = 0',
                'not_allowed1':'userid have no info',
                'not_allowed2':'userid dont have permission',
                "not_informed_user":"cannot inform user"
                }
    """官方 API 错误异常（必须包含错误码及错误信息）"""
    def __init__(self, errcode, errmsg):
        """
        :param errcode: 错误代码
        :param errmsg: 错误信息
        """
        self.errcode = errcode
        self.errmsg = errmsg

    def __str__(self):
        if six.PY2:
            return to_binary('{code}: {msg}'.format(code=self.errcode, msg=self.errmsg))
        else:
            return to_text('{code}: {msg}'.format(code=self.errcode, msg=self.errmsg))


class RdsSDKException(RdsException):
    """SDK 错误异常（仅包含错误内容描述）"""
    def __init__(self, message=''):
        """
        :param message: 错误内容描述，可选
        """
        self.message = message

    def __str__(self):
        if six.PY2:
            return to_binary(self.message)
        else:
            return to_text(self.message)



