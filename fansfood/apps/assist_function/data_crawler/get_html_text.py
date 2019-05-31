# _*_ coding: utf-8 _*_
__author__ = 'nick'
__date__ = '2019/4/27 11:47'


"""
使用 requests 库，根据提供的 URL 爬取 html 的文本内容
"""

import requests
import json
import random
from fake_useragent import UserAgent
import os
import time


class HTMLGetError(Exception):
    pass


class ProxiesIsEmpty(Exception):
    pass


# 实例化 用户代理
_useragent = UserAgent()


def get_html_text(url, ua=_useragent, refer_page=None, tag=True, stream=False):
    """
    尝试获取一个网页信息，并返回页面的数据
    参数说明：
    us : 用户代理
    proxies : 代理 IP
    refer_page : 来源页
    tag: 默认获取网页， False表示获取的图片（二进制数据）
    """

    # 构造头部信息
    headers = {
        "User-Agent": ua.random,                               # 随机的获取用户代理
    }
    # 如果有 reference 网页，则添加到请求头部
    if refer_page:
        headers["Referer"] = refer_page

    # 使用阿布云代理 ip
    # 代理服务器
    proxyHost = "http-dyn.abuyun.com"
    proxyPort = "9020"
    # 代理隧道验证信息
    proxyUser = "H64M968069U1254D"
    proxyPass = "2FFEB36D1661FC7A"
    # 构建代理
    proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
        "host": proxyHost,
        "port": proxyPort,
        "user": proxyUser,
        "pass": proxyPass,
    }
    proxies = {
        "http": proxyMeta,
        "https": proxyMeta,
    }

    try:
        r = requests.get(url=url, headers=headers, proxies=proxies, timeout=10, stream=stream)
        r.raise_for_status()
        r.encoding = "utf-8"
    except Exception as e:
        # 一般是代理被封导致的错误
        error_info = "获取网页时出现错误,请检查...\n" \
                     "错误信息：{}".format(e)
        raise HTMLGetError(error_info)

    if tag:
        return r.text
    else:
        return r


# 简易的爬虫程序，用于单个页面的爬取测试，不使用代理
def get_html_text_sample(url, ua=_useragent):
    headers = {
        "User-Agent": ua.random,  # 随机的获取用户代理
    }
    try:
        with requests.get(url=url, headers=headers, timeout=30) as r:
            r.raise_for_status()
            r.encoding = "utf-8"
    except Exception as e:
        error_info = "获取网页时出现错误,请检查...\n" \
                     "错误信息：{}".format(e)
        raise HTMLGetError(error_info)
    else:
        return r.text


def create_headers(ua=_useragent):
    # 构造头部信息
    headers = {
        "User-Agent": ua.random,  # 随机的获取用户代理
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-us",
        "Connection": "keep-alive",
        "Accept-Charset": "GB2312,utf-8;q=0.7,*;q=0.7"
    }

    # 使用阿布云代理 ip
    # 代理服务器
    proxyHost = "http-dyn.abuyun.com"
    proxyPort = "9020"
    # 代理隧道验证信息
    proxyUser = "H64M968069U1254D"
    proxyPass = "2FFEB36D1661FC7A"
    # 构建代理
    proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
        "host": proxyHost,
        "port": proxyPort,
        "user": proxyUser,
        "pass": proxyPass,
    }
    proxies = {
        "http": proxyMeta,
        "https": proxyMeta,
    }

    return headers, proxies