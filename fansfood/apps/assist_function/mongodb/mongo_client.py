# _*_ coding: utf-8 _*_
__author__ = 'nick'
__date__ = '2019/5/5 17:25'


"""
直接使用 pymongo 从 MongoDB 数据库中提取数据
不再 settings.py 中设定新的数据库引擎了
"""

import pymongo


class ConnectError(Exception):
    pass


def mongo_client(host=None, port=None, username=None, password=None):
    """
    MongoDB 客户端对象, 完成数据库的连接，并切换数据库，完成认证
    """

    # 给定默认值
    if not host:
        host = "127.0.0.1"
    if not port:
        port = 27017
    if not username:
        username = "nick"
    if not password:
        password = "abc123456"

    try:
        client = pymongo.MongoClient(host=host, port=port)
        client.admin.authenticate(username, password)
        return client
    except Exception:
        raise ConnectError("连接错误，可能是帐户认证的问题，请确认...")

