# _*_ coding: utf-8 _*_
__author__ = 'nick'
__date__ = '2019/5/2 20:52'


import random

# django 的邮件发送模块
from django.core.mail import send_mail
from django_food.settings import EMAIL_FROM

# 将生成的邮件验证码保存到数据库中
from user.models import EmailVerifyCode


# 定义邮件验证码：并保存到数据库中，以便比对验证
def send_email_verify_record(email, send_type='register', username=''):
    """发送邮件的函数，用于用户激活，重置密码，重置邮箱"""

    # 生成随机的验证码，保存进数据库
    email_verify_record = EmailVerifyCode()
    code = random_code()
    email_verify_record.code = code
    email_verify_record.email = email
    email_verify_record.send_type = send_type
    email_verify_record.verify_times = 3         # 验证码可用次数，默认为 1
    email_verify_record.save()

    # 邮件的标题和邮件内容
    email_title = ''
    email_body = ''

    if send_type == 'register':
        email_title = '凡肴-注册激活'
        email_body = '感谢你注册凡肴网!\n' \
                     '请点击的链接激活你的账号：http://127.0.0.1:8000/user/activation/{0}'.format(code)
    elif send_type == 'forget':
        email_title = '凡肴-重置密码'
        email_body = '请点击的链接重置你的密码：http://127.0.0.1:8000/user/reset_password_code/{0}'.format(code)
    elif send_type == 'reset_email':
        email_title = '凡肴-重置邮箱验证码'
        email_body = '请将邮件的的验证码填写至修改邮箱的页面中：{0}'.format(code)

    # 使用 try 来避免网络波动，或者邮件后台配制错误引发的错误，如果没有问题，返回一个 True
    try:
        # 参数中的 [email] 是邮件接收方（可以有多个收件人，需要用列表封装起来）
        send_status = send_mail(email_title, email_body, EMAIL_FROM, [email])
        # print(send_status)
    except Exception as e:
        return False
    else:
        if send_status:
            return True
        else:
            return False


def random_code(length=8):
    """生成随机验证码"""

    code_str = 'ABCDEFGHIJKLMNOPQRETUVWXYZabcedfghijklmnopqrstuvwxyz0123456789'
    code = "".join(random.sample(code_str, length))
    return code