# _*_ coding: utf-8 _*_
__author__ = 'nick'
__date__ = '2019/5/1 14:08'

# 将模块注册到 xadmin 后台

import xadmin
from xadmin import views

from .models import EmailVerifyCode


class BaseSetting:
    # 更改后台的主题样式
    enable_themes = True
    use_bootswatch = True


class GlobalSettings:
    # 更改后台的标题和页脚显示
    site_title = u"凡肴后台管理系统"
    site_footer = u"fans-food"
    # 应用模型在后台页面导航栏显示为下拉样式
    menu_style = "accordion"


# 后台管理模型类
class EmailVerifyCodeAdmin:
    # 用于展示邮件验证码这张表的信息
    # 按 email, code, send_type, send_time 的列方式显式
    list_display = ['email', 'code', 'send_type', "verify_times", 'send_time']
    # 通过设定 search_fields 字段来实现对数据表的「查」操作
    search_fields = ['email', 'code', 'send_type']
    # list_filter 实现筛选功能
    list_filter = ['email', 'code', 'send_type', 'send_time']
    model_icon = "fa fa-envelope-o"


# 注册到后台，参数：数据模型, 后台模型
xadmin.site.register(views.BaseAdminView, BaseSetting)
xadmin.site.register(views.CommAdminView, GlobalSettings)
xadmin.site.register(EmailVerifyCode, EmailVerifyCodeAdmin)
