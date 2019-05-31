# _*_ coding: utf-8 _*_
__author__ = 'nick'
__date__ = '2019/5/17 16:44'

from django.urls import path

from . import views

app_name = 'operator'

urlpatterns = [
    # 用户中心
    path('', views.user_center, name="user_center"),
    # 修改头像
    path('change_head_portrait/', views.ChangeHeaderPortraitView.as_view(), name="change_head_portrait"),
    # 修改头像
    path('change_user_info/', views.ChangeUserInfoView.as_view(), name="change_user_info"),
    # 刷新修改密码的验证码
    path('refresh_captcha/', views.refresh_captcha, name="refresh_captcha"),
    # 修改密码
    path('change_password/', views.ChangePasswordView.as_view(), name="change_password"),
    # 修改密码
    path('get_email_code/', views.get_change_email_code, name="get_email_code"),
    # 修改密码
    path('change_email/', views.ChangeEmailView.as_view(), name="change_email"),

    # 用户中心 - 用户喜欢
    path('user_like/', views.UserLikeView.as_view(), name="user_like"),
    # 用户中心 - 用户喜欢
    path('user_fav/', views.UserFavView.as_view(), name="user_fav"),
    # 用户中心 - 用户消息
    path('user_message/', views.UserMessageView.as_view(), name="user_message"),

    # 文章或照片页面添加或取消喜欢
    path('add_like/', views.AddLikeView.as_view(), name="add_like"),
    # 文章或照片页面添加或取消收藏
    path('add_fav/', views.AddFavView.as_view(), name="add_fav"),

    # 用户中心取消喜欢
    path('del_like/<slug:like_id>', views.DelLikeView.as_view(), name="del_like"),
    # 用户中心取消收藏
    path('del_fav/<slug:fav_id>', views.DelFavView.as_view(), name="del_fav"),

    # 用户中心删除消息
    path('del_message/<slug:message_id>', views.DelMessageView.as_view(), name="del_message"),
    # 用户中心阅读消息
    path('read_message/<slug:message_id>', views.ReadMessageView.as_view(), name="read_message"),


    # 用户添加留言
    path('add_message_board', views.AddMessageView.as_view(), name="add_message_board"),

    # 页面加载后，用户消息的获取
    path('upload_food_article/', views.UploadFoodArticle.as_view(), name="upload_food_article"),

    # 页面加载后，用户消息的获取
    path('get_user_message/', views.GetUserMessageView.as_view(), name="get_user_message"),
]