# _*_ coding: utf-8 _*_
__author__ = 'nick'
__date__ = '2019/4/30 19:44'


from django.urls import path
from . import views

app_name = "user"

urlpatterns = [
    # 用户登录
    path('login/', views.LoginView.as_view(), name="login"),
    # 用户登出
    path('logout/', views.user_logout, name='logout'),
    # 用户注册
    path("register/", views.RegisterView.as_view(), name="register"),
    # 忘记密码
    path("forget_password/", views.ForgetPasswordView.as_view(), name="forget_password"),
    # 重置密码
    path("reset_password/", views.ResetPasswordView.as_view(), name="reset_password"),
    # 重置密码链接
    path("reset_password_code/<slug:reset_password_code>/", views.ResetPasswordCodeView.as_view(), name="reset_password_code"),
    # 用户激活链接
    path("activation/<slug:active_code>/", views.ActivationView.as_view(), name="activation"),
    # 属性图片验证码
    path("flush_recode_image/", views.FlushRecodeImage.as_view(), name="flush_recode_image"),
    # 用户激活链接失效，重新获取激活链接
    path("reactive/", views.Reactive.as_view(), name="reactive")
]