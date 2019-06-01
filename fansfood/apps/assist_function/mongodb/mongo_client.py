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


def mongo_client(host="127.0.0.1", port=27017, username="nick", password="abc123456"):
    """
    MongoDB 客户端对象, 完成数据库的连接，并切换数据库，完成认证
    """

    try:
        client = pymongo.MongoClient(host=host, port=port)
        client.admin.authenticate(username, password)
        return client
    except Exception:
        raise ConnectError("连接错误，可能是帐户认证的问题，请确认...")

