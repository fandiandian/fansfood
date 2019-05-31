# _*_ coding: utf-8 _*_
__author__ = 'nick'
__date__ = '2019/5/23 16:14'

# xadmin 后台模型的注册
import xadmin
from xadmin import views

from .models import UserMessage, UserFav, UserLike, MessageBoard


# 后台模型的创建
class UserLikeAdmin:
    # 模型字段的后台显示
    list_display = ['user', 'like_id', 'like_type', 'add_time']
    # 字段的后台搜索功能（搜索依据的字段），时间不要做为搜索的条件，显示会有问题
    search_fields = ['user', 'like_id', 'like_type']
    # 字段的筛选功能，用于数据的显示
    list_filter = ['user', 'like_id', 'like_type', 'add_time']
    model_icon = "fa fa-heart-o"


class UserMessageAdmin:
    # 模型字段的后台显示
    list_display = ['user', 'readable', 'message_title', 'message_content', 'add_time']
    # 字段的后台搜索功能（搜索依据的字段），时间不要做为搜索的条件，显示会有问题
    search_fields = ['user', 'readable', 'message_title', 'message_content']
    # 字段的筛选功能，用于数据的显示
    list_filter = ['user', 'readable', 'message_title', 'message_content', 'add_time']
    model_icon = "fa fa-comment-o"


class UserFavAdmin:
    # 模型字段的后台显示
    list_display = ['user', 'fav_id', 'fav_type', 'add_time']
    # 字段的后台搜索功能（搜索依据的字段），时间不要做为搜索的条件，显示会有问题
    search_fields = ['user', 'fav_id', 'fav_type']
    # 字段的筛选功能，用于数据的显示
    list_filter = ['user', 'fav_id', 'fav_type', 'add_time']
    model_icon = "fa fa-star-o"


class MessageBoardAdmin:
    # 模型字段的后台显示
    list_display = ['name', 'email', 'is_user', 'message', 'add_time']
    # 字段的后台搜索功能（搜索依据的字段），时间不要做为搜索的条件，显示会有问题
    search_fields = ['name', 'email', 'is_user', 'message']
    # 字段的筛选功能，用于数据的显示
    list_filter = ['name', 'email', 'is_user', 'message', 'add_time']
    model_icon = "fa fa-comments-o"


# 后台模型的注册
xadmin.site.register(UserLike, UserLikeAdmin)
xadmin.site.register(UserFav, UserFavAdmin)
xadmin.site.register(UserMessage, UserMessageAdmin)
xadmin.site.register(MessageBoard, MessageBoardAdmin)


