# _*_ coding: utf-8 _*_
__author__ = 'nick'
__date__ = '2019/5/17 20:17'


import re

from django import forms
from user.models import UserProfiles
from captcha.fields import CaptchaField
from .models import MessageBoard


class ChangeUserHeaderPortraitForm(forms.ModelForm):

    class Meta:
        model = UserProfiles
        fields = ['head_portrait']


class ChangeUserInfoForm(forms.ModelForm):

    class Meta:
        model = UserProfiles
        fields = ['nick_name', 'gender', 'birthday', 'signature']


class ChangePasswordForm(forms.Form):
    password = forms.CharField(required=True, min_length=6, max_length=16)
    password2 = forms.CharField(required=True, min_length=6, max_length=16)
    captcha = CaptchaField(error_messages={'invalid': u'验证码错误'})

    def clean(self):
        try:
            password = self.cleaned_data['password']
            pattern = re.compile(r"^(?![\d]+$)(?![a-zA-Z]+$)(?![!#$%^&*]+$)[\da-zA-Z!#$%_^&*]{6,16}$")
            if not pattern.match(password):
                raise forms.ValidationError("密码不符合要求")
        except Exception as e:
            raise forms.ValidationError("密码不符合要求")

        return self.cleaned_data


class ChangeEmailForm(forms.Form):
    email = forms.EmailField(required=True, max_length=245)

    def clean(self):
        try:
            email = self.cleaned_data['email']
            pattern = re.compile("^([a-z0-9,!#\$%&'\*\+/=\?\^_`\{\|}~-]+(\.[a-z0-9,!#\$%&'\*\+/=\?\^_`\{\|}~-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*\.([a-z]{2,})){1}(;[a-z0-9,!#\$%&'\*\+/=\?\^_`\{\|}~-]+(\.[a-z0-9,!#\$%&'\*\+/=\?\^_`\{\|}~-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*\.([a-z]{2,}))*$")
            if not pattern.match(email):
                raise forms.ValidationError("邮箱不符合要求")
        except Exception as e:
            raise forms.ValidationError("邮箱不符合要求")

        return self.cleaned_data


class MessageBoardForm(forms.ModelForm):

    class Meta:
        model = MessageBoard
        fields = ['name', 'email', 'message']

