#!/usr/bin/env python3
# _*_ coding: utf-8 _*_

import random
import json

# django 模块或方法
# HTTP 响应相关的函数和类
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from django.utils import timezone
# 导入 django 的用户认证模块
from django.contrib.auth.backends import ModelBackend
# 用户加密
from django.contrib.auth.hashers import make_password
# 用户认证, 登入和登出方法
from django.contrib.auth import authenticate, login, logout
# 导入 django 的数据库查询对象
from django.db.models import Q
# 导入 django 的视图基类
from django.views.generic.base import View
# 导入 django 的消息模块，可以用于后台向前端传送一些消息，并可以被模版标签识别
from django.contrib import messages

# 导入自定的模型
from .models import UserProfiles, EmailVerifyCode, RecodeImage
from .forms import LoginForm, RegisterForm, ForgetPasswordForm, ResetPasswordForm
from assist_function.email.email import send_email_verify_record
from food.models import FoodArticle, FoodImage
from operation.models import UserMessage



# 生成两个随机数字，并获取验证码图片
def create_numbers(request):
    a, b = random.randint(1, 9), random.randint(1, 9)
    recode_image = RecodeImage.objects.get(recode_number_a=a, recode_number_b=b)
    request.session["number_a"] = a
    request.session["number_b"] = b
    return recode_image


class CustomBackend(ModelBackend):
    """
    自定义登录验证方式，实现用户名，邮箱均可登录
    实现逻辑：将用户输入的数据进入后台查询，如果查询成功，则认证成功，出现异常或失败，认证失败
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # 使用「Q」类实现「并集」查询
            user = UserProfiles.objects.get(Q(username=username) | Q(email=username))
            # 调用「UserProfiles」继承的方法「check_password」，将传入的明文密码进行加密，并与数据库中的密文密码进行对比
            # 如果对比成功，则验证通过，返回「user」，对比失败或者出现异常，则返回「None」
            if user.check_password(password):
                return user
        except Exception as e:
            return None


class LoginView(View):
    """用户登录视图类"""

    def get(self, request):
        """用户 get 请求登录页面， 给出响应"""

        # 获取浏览器请求的前向页面，以便于用户登录完成后，返回登录前的页面
        # 将获取到的信息保存到 request 的 session 中, 如果没有获取到，怎返回首页
        request.session['login_reference_page'] = request.META.get("HTTP_REFERER", '/')
        # 获取验证码图片
        recode_image = create_numbers(request)
        return render(request, "user/login.html", {"recode_image": recode_image})

    def post(self, request):
        """post 方法的表单提交"""

        # 这里会的「login_form」实例会自动从「request.POST」获取相应的字段值
        # 所以「LoginForm」中定义的「键名」一定要和「html」页面中「form」标签提交的「键名」对应起来，否则会获取失败
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            # 获取表单信息
            username = request.POST.get('username', '')
            password = request.POST.get('password', '')
            recode = int(request.POST.get("recode", 0))

            # 获取 session 中的验证码，并计算结果
            if recode != request.session["number_a"] + request.session["number_b"]:
                # 验证码错误，重新获取图片
                recode_image = create_numbers(request).to_json()
                message = {"status": "fail", "fail_type": "recode", "recode_image": recode_image}
                # 这里出现先了很大的问题，具体的模型实例 json 化的问题
                # 解决方案的是在模型中自定义一个函数 -- 将模型字段和值组成一个键值对方放入一个字典表
                # 字典化的过程中，还出现了一个问题，就是 ImageField 字段的值需要调用 str() 函数字符串化
                # 详见 RecodeImage 模型类中的定义
                return JsonResponse(message, safe=False)

            # 用户名验证
            verify_user_name = UserProfiles.objects.filter(Q(username=username) | Q(email=username))
            if not verify_user_name:                                          # 数据库中未查询到用户名
                recode_image = create_numbers(request).to_json()
                message = {"status": "fail", "fail_type": "username", "recode_image": recode_image}
                return JsonResponse(message, safe=False)

            # 用户密码验证
            user = authenticate(username=username, password=password)         # 如果验证未通过，user = None
            if not user:                                                      # 用户名与密码不匹配
                recode_image = create_numbers(request).to_json()
                message = {"status": "fail", "fail_type": "password", "recode_image": recode_image}
                return JsonResponse(message, safe=False)

            # 验证用户是否激活
            if not user.is_active:                                            # 用户未激活
                send_email_verify_record(user.email)
                return JsonResponse({
                    "status": "fail",
                    "fail_type": "not_active",
                    "message": "用户未激活，已重发激活连接至注册邮箱，请前往邮箱激活..."
                })
            else:
                login(request, user)                                          # 通过全部验证，执行登录操作
                # 页面重定向
                refer_page = request.session.get("login_reference_page", '/')
                if refer_page in \
                    (reverse("user:login"), reverse("user:reset_password")):
                    return JsonResponse({"status": "success", "url": reverse("home_page")})
                else:
                    return JsonResponse({"status": "success", "url": request.session["login_reference_page"]})

        # 表单数据 form 验证失败
        recode_image = create_numbers(request).to_json()
        message = {"status": "fail", "fail_type": "form", "recode_image": recode_image}
        return JsonResponse(message, safe=False)


# 实现用户的登出，并重定向到主页
def user_logout(request):
    logout(request)
    return redirect(request.META.get('HTTP_REFERER', '/'))


class RegisterView(View):
    """用户注册视图类"""

    def get(self, request):
        """get 请求响应"""

        # 获取验证码图片
        recode_image = create_numbers(request)
        return render(request, "user/register.html", {"recode_image": recode_image})

    def post(self, request):
        """post 请求响应"""

        # form 验证
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            # 获取用户的输入表单信息
            username = request.POST.get("username")
            email = request.POST.get("email")
            password = request.POST.get("password")
            recode = int(request.POST.get("recode"))

            # 获取 session 中的验证码，并计算结果
            if recode != request.session["number_a"] + request.session["number_b"]:
                # 验证码错误，重新获取图片
                recode_image = create_numbers(request).to_json()
                message = {"status": "fail", "fail_type": "recode", "recode_image": recode_image}
                return JsonResponse(message, safe=False)

            # 验证用户名是否已经被注册
            verify_username = UserProfiles.objects.filter(username=username)
            if verify_username:                           # 用户名已被注册
                recode_image = create_numbers(request).to_json()
                message = {"status": "fail", "fail_type": "username", "recode_image": recode_image}
                return JsonResponse(message, safe=False)

            # 验证邮箱是否已被注册
            verify_email = UserProfiles.objects.filter(email=email)
            if verify_email:                              # 邮箱已被注册
                recode_image = create_numbers(request).to_json()
                message = {"status": "fail", "fail_type": "email", "recode_image": recode_image}
                return JsonResponse(message, safe=False)

            # 自动发送邮件验证码至用户邮箱
            send_status = send_email_verify_record(email)
            if send_status:

                # 通过验证，邮件发送成功，将新的用户数据写入数据库
                new_user = UserProfiles()
                new_user.username = username
                new_user.email = email
                new_user.is_active = False  # 设定为未激活状态
                new_user.password = make_password(password)  # 对密码进行加密
                new_user.save()  # 写入数据库

                # 用户站内消息功能，添加欢迎注册消息
                user_message = UserMessage()
                user_message.user = new_user
                user_message.message_title = '欢迎注册<凡肴网-fansfood.com>\n'
                user_message.message_content = f"""
                嗨，{username}！很高兴您能注册<凡肴网-fansfood.com>。\n\n
                这是一个关于美食的网站，网站提供了许多美食的制作教程和美食图片，希望您能够找到心仪的美食和图片！\n\n
                \t\t\t\t\t\t\t\t一个美食爱好者：nick\n
                \t\t\t\t\t\t\t\t{timezone.now().strftime('%Y-%m-%d %H:%M')}\n
                """
                user_message.save()

                return JsonResponse({"status": "success"})
            else:
                return JsonResponse({"status": "fail", "fail_type": "send_email"})

        # 表单数据 form 验证失败
        recode_image = create_numbers(request).to_json()
        message = {"status": "fail", "fail_type": "form", "recode_image": recode_image}
        return JsonResponse(message, safe=False)


class ActivationView(View):
    """用户激活视图类"""

    def get(self, request, active_code):
        email_verify_record = EmailVerifyCode.objects.filter(code=active_code)
        if email_verify_record:
            recode = email_verify_record[0]

            # (timezone.now() - recode.send_time) 是一个 datetime.timedelta 对象
            # 使用 total_seconds() 方法获取秒数
            if (timezone.now() - recode.send_time).total_seconds() < 600:   # 验证码的有效时间是 600 s
                user = UserProfiles.objects.get(email=recode.email)
                user.is_active = True
                user.save()
                recode.delete()                             # 激活后，删除激活邮件验证码
                messages.add_message(request, messages.INFO, "用户已激活，请重新登录")
                return redirect("user:login")               # 返回用户登录页面
            else:
                send_email_verify_record(recode.email)
                recode.delete()                             # 验证码超时，执行删除，重新发送验证码
                messages.add_message(request, messages.INFO, "连接失效，已重发验证邮件，请前往邮箱重新激活")
                return redirect("user:login")

        # 验证失败，返回首页
        messages.add_message(
            request,
            messages.INFO,
            "无效的激活验证，页面已重置，请输入邮箱信息，重新获取激活链接"
        )
        return redirect("user:login")


class Reactive(View):
    """新用户激活失败，重新获取激活链接的视图类"""

    def get(self, request):
        # 获取验证码图片
        recode_image = create_numbers(request)
        return render(request, "user/reactive.html", {"recode_image": recode_image})

    def post(self, request):
        reactive_form = ForgetPasswordForm(request.POST)
        if reactive_form.is_valid():
            username = request.POST.get("username")
            email = request.POST.get("email")
            recode = int(request.POST.get("recode"))

            # 获取 session 中的验证码，并计算结果
            if recode != request.session["number_a"] + request.session["number_b"]:
                # 验证码错误，重新获取图片
                recode_image = create_numbers(request).to_json()
                message = {"status": "fail", "fail_type": "recode", "recode_image": recode_image}
                return JsonResponse(message, safe=False)

            # 验证用户名与邮箱是否匹配
            verify_user = UserProfiles.objects.filter(username=username)
            if not verify_user:
                recode_image = create_numbers(request).to_json()
                message = {"status": "fail", "fail_type": "username", "recode_image": recode_image}
                return JsonResponse(message, safe=False)
            else:
                user = verify_user[0]
                if user.username != username or user.email != email:
                    recode_image = create_numbers(request).to_json()
                    message = {"status": "fail", "fail_type": "email", "recode_image": recode_image}
                    return JsonResponse(message, safe=False)
                else:
                    send_email_verify_record(email, "register")  # 发送重置密码的邮件激活码
                    return JsonResponse({"status": "success"})

        # 表单验证失败
        recode_image = create_numbers(request)
        message = {"status": "fail", "fail_type": "form", "recode_image": recode_image}
        return JsonResponse(message, safe=False)


class ForgetPasswordView(View):
    """忘记密码的视图类"""

    def get(self, request):
        # 获取验证码图片
        recode_image = create_numbers(request)
        return render(request, "user/forget_password.html", {"recode_image": recode_image})

    def post(self, request):
        forget_password_form = ForgetPasswordForm(request.POST)
        if forget_password_form.is_valid():
            username = request.POST.get("username")
            email = request.POST.get("email")
            recode = int(request.POST.get("recode"))

            # 获取 session 中的验证码，并计算结果
            if recode != request.session["number_a"] + request.session["number_b"]:
                # 验证码错误，重新获取图片
                recode_image = create_numbers(request).to_json()
                message = {"status": "fail", "fail_type": "recode", "recode_image": recode_image}
                return JsonResponse(message, safe=False)

            # 验证用户名与邮箱是否匹配
            verify_user = UserProfiles.objects.filter(username=username)
            if not verify_user:
                recode_image = create_numbers(request).to_json()
                message = {"status": "fail", "fail_type": "username", "recode_image": recode_image}
                return JsonResponse(message, safe=False)
            else:
                user = verify_user[0]
                if user.username != username or user.email != email:
                    recode_image = create_numbers(request).to_json()
                    message = {"status": "fail", "fail_type": "email", "recode_image": recode_image}
                    return JsonResponse(message, safe=False)
                else:
                    send_email_verify_record(email, "forget")       # 发送重置密码的邮件激活码
                    return JsonResponse({"status": "success"})

        # 表单验证失败
        recode_image = create_numbers(request)
        message = {"status": "fail", "fail_type": "form", "recode_image": recode_image}
        return JsonResponse(message, safe=False)


class ResetPasswordCodeView(View):
    """用户重置密码的邮件链接响应的视图函数"""

    def get(self, request, reset_password_code):
        verify_code = EmailVerifyCode.objects.filter(code=reset_password_code)
        if verify_code:
            reset_code = verify_code[0]
            email = reset_code.email
            request.session["email"] = email                      # 将邮箱保存在 session 中
            request.session["reset_password_code"] = reset_password_code
            return redirect("user:reset_password")
        messages.add_message(request, messages.INFO, "连接失效，页面已重置，请重新获取")
        return redirect("user:forget_password")


class ResetPasswordView(View):
    """重置密码视图类"""
    def get(self, request):
        return render(request, 'user/reset_password.html')

    def post(self, request):
        reset_password_form = ResetPasswordForm(request.POST)
        if reset_password_form.is_valid():
            password = request.POST.get("password")
            password2 = request.POST.get("password2")

            # 从 session 中获取 email 和 reset_password_code 信息，如果无法获取，表示无效
            try:
                email = request.session["email"]                 # 从 session 中获取 email
                code = request.session["reset_password_code"]    # 获取 reset_password_code
            except:
                return JsonResponse({"status": "fail", "fail_type": "email"})

            # 验证两次密码输入是否一致
            if password != password2:
                return JsonResponse({"status": "fail", "fail_type": "not_equal"})

            # 密码一致性验证成功
            user = UserProfiles.objects.get(email=email)          # 根据 email 从用户数据库中提取用户
            user.password = make_password(password)               # 修改密码
            user.save()                                           # 数据更新

            # 完成密码的修改，从数据库中删除验证码
            verify_cord = EmailVerifyCode.objects.get(code=code)
            verify_cord.delete()
            del request.session["email"]                          # 删除 session 中的 email
            del request.session["reset_password_code"]            # 删除 session 中的 reset_password_code
            # return redirect("user:login")                       # 重定向至登录页面
            # 这里出现了一个问题，ajax 的请求，不会执行重定向操作
            # 需要在 ajax 中执行操作
            return JsonResponse({"status": "success"})

        # 表单验证失败
        return JsonResponse({"status": "fail", "fail_type": "form"})


class HomePageView(View):
    """主页视图"""

    def get(self, request):

        # 随机从数据库中获取 6 张图片
        random_image = FoodImage.objects.order_by("?")[:6]

        # 随机从 mysql 数据库中提取 6 个数据
        random_food = FoodArticle.objects.order_by("?")[:6]

        # 热门食物--做过的人最多
        popular_food = FoodArticle.objects.order_by("-fav")[:3]

        return render(request, "home_page.html", {
            "random_food": random_food,
            "popular_food": popular_food,
            "random_image": random_image,
            "focus": "home",                      # 选中状态标志
        })


class FlushRecodeImage(View):
    """刷新图片验证码"""

    def post(self, request):
        recode_image = create_numbers(request).to_json()
        message = {"status": "success", "recode_image": recode_image}
        return JsonResponse(message, safe=False)


def about(request):
    return render(request, 'about.html', {'focus': 'about'})