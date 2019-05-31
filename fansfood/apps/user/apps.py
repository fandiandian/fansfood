# _*_ coding: utf-8 _*_

from django.apps import AppConfig


class UserConfig(AppConfig):
    name = 'user'
    # 为模型定义别名
    verbose_name = u'用户管理'


