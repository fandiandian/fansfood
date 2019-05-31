# _*_ coding: utf-8 _*_
__author__ = 'nick'
__date__ = '2019/5/1 22:51'


"""表单验证功能写在这里"""

from django import forms


# 登录表单验证
class LoginForm(forms.Form):
    username = forms.CharField(min_length=4, max_length=16, required=True)
    password = forms.CharField(required=True)
    recode = forms.IntegerField(required=True)


# 登录表单验证
class RegisterForm(forms.Form):
    username = forms.CharField(min_length=4, max_length=16, required=True)
    email = forms.EmailField(max_length=254, required=True)
    password = forms.CharField(min_length=8, max_length=16, required=True)
    recode = forms.IntegerField(required=True)


# 忘记密码表单验证
class ForgetPasswordForm(forms.Form):
    username = forms.CharField(min_length=4, max_length=16, required=True)
    email = forms.EmailField(max_length=254, required=True)
    recode = forms.IntegerField(required=True)


# 重置密码表单验证
class ResetPasswordForm(forms.Form):
    password = forms.CharField(min_length=8, max_length=16, required=True)
    password2 = forms.CharField(min_length=8, max_length=16, required=True)
