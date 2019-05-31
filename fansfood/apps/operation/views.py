# _*_ coding: utf-8 _*_

import json
import time

from django.shortcuts import render, redirect
from django.views.generic import View
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.hashers import make_password
from django.urls import reverse
from django.contrib.auth.decorators import login_required
# django 后台的用户组
from django.contrib.auth.models import Group

from captcha.models import CaptchaStore
from captcha.helpers import captcha_image_url
from pure_pagination import Paginator, PageNotAnInteger

from assist_function.email.email import send_email_verify_record
from . import forms
from user.models import EmailVerifyCode, UserProfiles
from food.models import FoodImage, FoodArticle, FoodSteps, Tags
from .models import UserFav, UserLike, MessageBoard
from assist_function.authenticate.login_required import LoginRequiredMixin


# 返回用户中心的视图函数
@login_required
def user_center(request):
    return render(request, 'operation/user_center.html')


# 修改用户头像视图类
class ChangeHeaderPortraitView(LoginRequiredMixin, View):
    """修改用户头像响应视图"""

    def post(self, request):
        # request 对象中有一个 FILES 对象，相应中携带的文件保存在这里
        head_portrait_form = forms.ChangeUserHeaderPortraitForm(
            request.POST, request.FILES, instance=request.user
        )
        if head_portrait_form.is_valid():
            request.user.save()
            # 这里很重要，提取出图片的 url, 可以让页面根据新的 url 实时刷新页面
            image = request.user.head_portrait.url
            return JsonResponse({'status': 'success', 'image': image})
        else:
            return JsonResponse({'status': 'fail'})


# 修改用户信息视图类
class ChangeUserInfoView(LoginRequiredMixin, View):
    """修改用户信息视图"""

    def post(self, request):
        user_info_form = forms.ChangeUserInfoForm(
            request.POST, instance=request.user
        )
        if user_info_form.is_valid():
            request.user.save()
            return JsonResponse({"status": "success"})
        else:
            error_dict = user_info_form.errors
            error_str = json.dumps(error_dict)
            error_dict = json.loads(error_str)
            return JsonResponse({"status": "fail", "message": error_dict})


# 生成验证码函数
@login_required
def generate_captcha():
    captcha_dict = dict()
    captcha_dict['captcha_key'] = CaptchaStore.generate_key()
    captcha_dict['captcha_image'] = captcha_image_url(captcha_dict['captcha_key'])
    return captcha_dict


# 刷新验证码
@login_required
def refresh_captcha(request):
    if request.is_ajax():
        to_json_response = dict()
        to_json_response['status'] = 'success'
        to_json_response.update(generate_captcha())
        return HttpResponse(json.dumps(to_json_response), content_type='application/json')


# 修改密码视图类
class ChangePasswordView(LoginRequiredMixin, View):
    """修改用户密码"""

    def post(self, request):
        """ajax 的 post 的请求"""
        change_password_form = forms.ChangePasswordForm(request.POST)
        if change_password_form.is_valid():
            password = request.POST.get('password', '')
            password2 = request.POST.get('password2', '')
            if password == password2:
                user = request.user
                user.password = make_password(password)      # 两次密码一致且符合要求，保存结果
                user.save()
                # ajax 发起的请求，需要在 ajax 中重定向至登录页面，将登录页面返回
                return JsonResponse({"status": 'success', 'url': reverse('user:login')})
            else:                                            # 两次输入符合要求，但是输入不一致
                to_json_response = dict()
                to_json_response['status'] = 'fail'
                to_json_response['error'] = {'password2': '两次输入不一致'}
                to_json_response.update(generate_captcha())
                return HttpResponse(json.dumps(to_json_response), content_type='application/json')

        else:                                                # 输入不符合要求（密码或验证码）
            to_json_response = dict()
            to_json_response['status'] = 'fail'
            to_json_response.update(generate_captcha())

            error_dict = change_password_form.errors
            error_str = json.dumps(error_dict)
            error_dict = json.loads(error_str)
            to_json_response['error'] = error_dict

            return HttpResponse(json.dumps(to_json_response), content_type='application/json')


# 获取的邮箱验证码
@login_required
def get_change_email_code(request):

    if request.is_ajax():
        email_form = forms.ChangeEmailForm(request.POST)
        if email_form.is_valid():
            email = request.POST.get('email')
            user = UserProfiles.objects.filter(email=email)
            if not user:
                send_status = send_email_verify_record(email, send_type="reset_email")
                if send_status:
                    return JsonResponse({"status": 'success'})
                else:
                    # 验证码邮件发送失败
                    return JsonResponse({"status": 'fail', 'message': 'send'})
            else:
                # 填入的邮箱已被注册
                return JsonResponse({"status": 'fail', 'message': 'exist'})
        else:
            # 填入的邮箱不合规
            return JsonResponse({"status": 'fail', 'message': 'invalid'})


# 修改邮箱视图类
class ChangeEmailView(LoginRequiredMixin, View):
    """更换邮箱的视图类"""

    def post(self, request):
        """ajax post 函数"""
        email = request.POST.get('email')
        email_code = request.POST.get('email_code')
        email_verify_query = EmailVerifyCode.objects.filter(email=email, code=email_code)
        if email_verify_query:
            email_verify = email_verify_query[0]
            if email_verify.verify_times > 0 and \
                email_verify.send_time.timestamp() - time.time() < 600:
                user = request.user
                user.email = email
                user.save()
                email_verify.delete()
                return JsonResponse({'status': 'success', 'email': email})
            else:
                return JsonResponse({'status': 'fail', 'message': '验证码已过期，请重新获取'})
        else:
            return JsonResponse({'status': 'fail', 'message': '无效的验证码或验证码已过期，请确认'})


# 这一部分是用户喜欢相关的视图类和视图函数
class UserLikeView(LoginRequiredMixin, View):
    """用户中心用户喜欢视图"""

    def get(self, request):
        """根据用户从数据库中提取用户喜欢的数据"""
        user = request.user
        user_like_article = user.userlike_set.filter(like_type='food_article')
        user_like_image = user.userlike_set.filter(like_type='food_image')

        old_article_page = request.session.get('user_like_article_page', 1)
        old_image_page = request.session.get('user_like_image_page', 1)

        focus = 'food_article'
        if user_like_article:
            # 从匹配的数据中获取文章信息
            food_articles = FoodArticle.objects.filter(
                article_id__in=[like.like_id for like in user_like_article]
            )

            # 获取页面传回的分页数值，默认为 1（第一页）
            try:
                article_page = request.GET.get('article_page', 1)
                request.session['user_like_article_page'] = article_page
            except PageNotAnInteger:
                article_page = 1
            # 对数据库中所取出的所有对象，进行分页，中间的参数为每页显示的对象个数，设置为 6 个
            # 这里对 分页插件进行了改写，默认的下一页的查询时 page ,本视图中有两个分页，所以需要区分
            # 在 Paginator 中增加了一个默认参数 type, 需要时传参进行修改即可
            # 在 Page 类中对函数 _other_page_querystring 进行修改，使用 type 参数值，而不是写死的 'page' 字符串
            paginator = Paginator(food_articles, 6, request=request, page_type='article_page')
            # 取出对应页的数据
            user_like_article_page = paginator.page(article_page)

            if old_article_page != article_page:
                focus = 'food_article'
        else:
            user_like_article_page = []
            focus = 'food_image'
            article_page = 1

        if user_like_image:
            # 从匹配的数据中获取图片信息
            food_images = FoodImage.objects.filter(
                name__in=[like.like_id for like in user_like_image]
            )

            # 获取页面传回的分页数值，默认为 1（第一页）
            try:
                image_page = request.GET.get('image_page', 1)
                request.session['user_like_image_page'] = image_page
            except PageNotAnInteger:
                image_page = 1
            # 对数据库中所取出的所有对象，进行分页，中间的参数为每页显示的对象个数，设置为 6 个
            paginator = Paginator(food_images, 6, request=request, page_type='image_page')
            # 取出对应页的数据
            user_like_image_page = paginator.page(image_page)
            if old_image_page != image_page:
                focus = 'food_image'
        else:
            user_like_image_page = []
            focus = 'food_article'
            image_page = 1

        # 刷新页面后，二者的值都会成为以，此时不再以 session 中的结果为准
        if image_page == article_page == 1:
            focus = 'food_article'

        # 在用户中心执行取消喜欢后，保持取消的 focus 状态
        # 例如：如果取消的是文章，刷新页面后焦点在 喜欢的文章上
        del_type = request.session.get('delete_like_type', '')
        if del_type:
            focus = del_type
            del request.session['delete_like_type']

        return render(request, 'operation/user_like.html', {
            'user_like_article_page': user_like_article_page,
            'user_like_image_page': user_like_image_page,
            'focus': focus,
        })


class UserFavView(LoginRequiredMixin, View):
    """用户中心用户收藏视图"""

    def get(self, request):
        """根据用户从数据库中提取用户喜欢的数据"""
        user = request.user
        user_fav_article = user.userfav_set.filter(fav_type='food_article')
        user_fav_image = user.userfav_set.filter(fav_type='food_image')

        old_article_page = request.session.get('user_fav_article_page', 1)
        old_image_page = request.session.get('user_fav_image_page', 1)

        focus = 'food_article'
        if user_fav_article:
            # 从匹配的数据中获取文章信息
            food_articles = FoodArticle.objects.filter(
                article_id__in=[fav.fav_id for fav in user_fav_article]
            )

            # 获取页面传回的分页数值，默认为 1（第一页）
            try:
                article_page = request.GET.get('article_page', 1)
                request.session['user_fav_article_page'] = article_page
            except PageNotAnInteger:
                article_page = 1
            # 对数据库中所取出的所有对象，进行分页，中间的参数为每页显示的对象个数，设置为 6 个
            # 这里对 分页插件进行了改写，默认的下一页的查询时 page ,本视图中有两个分页，所以需要区分
            # 在 Paginator 中增加了一个默认参数 type, 需要时传参进行修改即可
            # 在 Page 类中对函数 _other_page_querystring 进行修改，使用 type 参数值，而不是写死的 'page' 字符串
            paginator = Paginator(food_articles, 6, request=request, page_type='article_page')
            # 取出对应页的数据
            user_fav_article_page = paginator.page(article_page)

            if old_article_page != article_page:
                focus = 'food_article'
        else:
            user_fav_article_page = []
            focus = 'food_image'
            article_page = 1

        if user_fav_image:
            # 从匹配的数据中获取图片信息
            food_images = FoodImage.objects.filter(
                name__in=[fav.fav_id for fav in user_fav_image]
            )

            # 获取页面传回的分页数值，默认为 1（第一页）
            try:
                image_page = request.GET.get('image_page', 1)
                request.session['user_fav_image_page'] = image_page
            except PageNotAnInteger:
                image_page = 1
            # 对数据库中所取出的所有对象，进行分页，中间的参数为每页显示的对象个数，设置为 6 个
            paginator = Paginator(food_images, 6, request=request, page_type='image_page')
            # 取出对应页的数据
            user_fav_image_page = paginator.page(image_page)
            if old_image_page != image_page:
                focus = 'food_image'
        else:
            user_fav_image_page = []
            focus = 'food_article'
            image_page = 1

        # 刷新页面后，二者的值都会成为以，此时不再以 session 中的结果为准
        if image_page == article_page == 1:
            focus = 'food_article'

        # 在用户中心执行取消收藏后，保持取消的 focus 状态
        # 例如：如果取消的是文章，刷新页面后焦点在 收藏的文章上
        del_type = request.session.get('delete_fav_type', '')
        if del_type:
            focus = del_type
            del request.session['delete_fav_type']

        return render(request, 'operation/user_fav.html', {
            'user_fav_article_page': user_fav_article_page,
            'user_fav_image_page': user_fav_image_page,
            'focus': focus,
        })


class UserMessageView(LoginRequiredMixin, View):
    """用户喜欢视图"""

    def get(self, request):
        """根据用户从数据库中提取用户喜欢的数据"""
        user = request.user
        unread_message = user.usermessage_set.filter(readable="unread")
        read_message = user.usermessage_set.filter(readable="read")
        old_unread_page = request.session.get('user_unread_page', 1)
        old_read_page = request.session.get('user_read_page', 1)

        focus = 'unread'
        if unread_message:

            # 获取页面传回的分页数值，默认为 1（第一页）
            try:
                unread_page = request.GET.get('unread_page', 1)
                request.session['user_unread_page'] = unread_page
            except PageNotAnInteger:
                unread_page = 1
            # 对数据库中所取出的所有对象，进行分页，中间的参数为每页显示的对象个数，设置为 6 个
            # 这里对 分页插件进行了改写，默认的下一页的查询时 page ,本视图中有两个分页，所以需要区分
            # 在 Paginator 中增加了一个默认参数 type, 需要时传参进行修改即可
            # 在 Page 类中对函数 _other_page_querystring 进行修改，使用 type 参数值，而不是写死的 'page' 字符串
            paginator = Paginator(unread_message, 6, request=request, page_type='unread_page')
            # 取出对应页的数据
            user_unread_page = paginator.page(unread_page)

            if old_unread_page != unread_page:
                focus = 'unread'
        else:
            user_unread_page = []
            focus = 'unread'
            unread_page = 1

        if read_message:

            # 获取页面传回的分页数值，默认为 1（第一页）
            try:
                read_page = request.GET.get('read_page', 1)
                request.session['user_read_page'] = read_page
            except PageNotAnInteger:
                read_page = 1
            # 对数据库中所取出的所有对象，进行分页，中间的参数为每页显示的对象个数，设置为 6 个
            paginator = Paginator(read_message, 6, request=request, page_type='read_page')
            # 取出对应页的数据
            user_read_page = paginator.page(read_page)
            if old_read_page != read_page:
                focus = 'read'
        else:
            user_read_page = []
            focus = 'read'
            read_page = 1

        # 刷新页面后，二者的值都会成为以，此时不再以 session 中的结果为准
        if read_page == unread_page == 1:
            focus = 'unread'

        # 在用户中心执行删除后，保持取消的 focus 状态
        # 例如：如果删除的是已读消息，刷新页面后焦点在 已读消息上上
        del_type = request.session.get('delete_read_type', '')
        if del_type:
            focus = del_type
            del request.session['delete_read_type']

        return render(request, 'operation/user_message.html', {
            'user_unread_page': user_unread_page,
            'user_read_page': user_read_page,
            'focus': focus,
        })


class AddLikeView(View):
    """用户添加或取消喜欢视图类 -- ajax"""

    def post(self, request):
        if request.user.is_authenticated:
            like_status = request.POST.get("status", '')
            like_id = request.POST.get("id", '')
            like_type = request.POST.get('type')
            user = request.user
            if like_status == 'no':     # 添加喜欢
                like = UserLike()
                like.user = user
                like.like_id = like_id
                like.like_type = like_type
                try:
                    # 修改文章或图片的喜欢数据，执行加一操作
                    if 'food_article' == like_type:
                        food = FoodArticle.objects.get(article_id=like_id)
                        food.like += 1
                        food.save()
                    elif 'food_image' == like_type:
                        image = FoodImage.objects.get(name=like_id)
                        image.like += 1
                        image.save()
                    # 保存喜欢数据
                    like.save()
                    return JsonResponse({'status': 'success', 'like_status': 'yes'})
                except:
                    # 如果出现无法 id 无法匹配的情况，给出失败提示
                    return JsonResponse({'status': 'fail', 'message': '操作失败，请稍后再试'})
            elif like_status == 'yes':    # 删除喜欢
                like = user.userlike_set.filter(like_id=like_id)
                if like:
                    like = like[0]
                    like.delete()
                    # 修改文章或图片的喜欢数据，执行减一操作
                    if 'food_article' == like_type:
                        food = FoodArticle.objects.get(article_id=like_id)
                        food.like -= 1
                        food.save()
                    elif 'food_image' == like_type:
                        image = FoodImage.objects.get(name=like_id)
                        image.like -= 1
                        image.save()
                    return JsonResponse({'status': 'success', 'like_status': 'no'})
                else:
                    return JsonResponse({'status': 'fail', 'message': '操作失败，请稍后再试'})
        else:
            return JsonResponse({'status': 'fail', 'message': '用户未登录，请前往登录'})


class AddFavView(View):
    """用户添加或取消喜欢视图类  -- ajax"""

    def post(self, request):
        if request.user.is_authenticated:
            fav_status = request.POST.get("status", '')
            fav_id = request.POST.get("id", '')
            fav_type = request.POST.get('type')
            user = request.user
            if fav_status == 'no':     # 添加喜欢
                fav = UserFav()
                fav.user = user
                fav.fav_id = fav_id
                fav.fav_type = fav_type
                try:
                    # 修改文章或图片的收藏数据，执行加一操作
                    if 'food_article' == fav_type:
                        food = FoodArticle.objects.get(article_id=fav_id)
                        food.like += 1
                        food.save()
                    elif 'food_image' == fav_type:
                        image = FoodImage.objects.get(name=fav_id)
                        image.like += 1
                        image.save()
                    fav.save()
                    return JsonResponse({'status': 'success', 'fav_status': 'yes'})
                except:
                    return JsonResponse({'status': 'fail', 'message': '操作失败，请稍后再试'})
            elif fav_status == 'yes':    # 删除喜欢
                fav = user.userfav_set.filter(fav_id=fav_id)
                if fav:
                    fav = fav[0]
                    fav.delete()
                    # 修改文章或图片的收藏数据，执行减一操作
                    if 'food_article' == fav_type:
                        food = FoodArticle.objects.get(article_id=fav_id)
                        food.like -= 1
                        food.save()
                    elif 'food_image' == fav_type:
                        image = FoodImage.objects.get(name=fav_id)
                        image.like -= 1
                        image.save()
                    return JsonResponse({'status': 'success', 'fav_status': 'no'})
                else:
                    return JsonResponse({'status': 'fail', 'message': '操作失败，请稍后再试'})
        else:
            return JsonResponse({'status': 'fail', 'message': '用户未登录，请前往登录'})


class DelLikeView(LoginRequiredMixin, View):
    """用户中心删除喜欢操作"""

    def get(self, request, like_id):
        user = request.user
        unlike = user.userlike_set.get(like_id=like_id)
        request.session['delete_like_type'] = unlike.like_type
        unlike.delete()
        # 文章或图片的喜欢数据修改，执行减一操作
        if 'food_article' == unlike.fav_type:
            food = FoodArticle.objects.get(article_id=like_id)
            food.fav -= 1
            food.save()
        elif 'food_image' == unlike.fav_type:
            image = FoodImage.objects.get(name=like_id)
            image.fav -= 1
            image.save()
        # 重定向用户中心 -- 用户喜欢页面
        return redirect(reverse('operator:user_like'))


class DelFavView(LoginRequiredMixin, View):
    """用户中心删除收藏操作"""

    def get(self, request, fav_id):
        user = request.user
        unfav = user.userfav_set.get(fav_id=fav_id)
        request.session['delete_fav_type'] = unfav.fav_type
        unfav.delete()
        # 文章或图片的收藏数据修改，执行减一操作
        if 'food_article' == unfav.fav_type:
            food = FoodArticle.objects.get(article_id=fav_id)
            food.fav -= 1
            food.save()
        elif 'food_image' == unfav.fav_type:
            image = FoodImage.objects.get(name=fav_id)
            image.fav -= 1
            image.save()
        # 重定向用户中心 -- 用户收藏页面
        return redirect(reverse('operator:user_fav'))


class DelMessageView(LoginRequiredMixin, View):
    """用户中心删除消息操作"""

    def get(self, request, message_id):
        user = request.user
        del_message = user.usermessage_set.get(id=message_id)
        request.session['delete_read_type'] = del_message.readable
        del_message.delete()
        # 重定向用户中心 -- 用户消息页面
        return redirect(reverse('operator:user_message'))


class ReadMessageView(LoginRequiredMixin, View):
    """对于未读消息，页面点击查看详情，表示消息以阅读，后台修改消息状态为已读"""

    def post(self, request, message_id):
        """前端通过 ajax 来传回未读消息点击了查看详情"""
        user = request.user
        id = request.POST.get('id', '')
        read_message = user.usermessage_set.get(id=message_id)
        read_message.readable = 'read'
        read_message.save()
        return JsonResponse({"status": "success"})


class MessageBoardView(View):
    """获取留言板的视图函数"""

    def get(self, request):
        message_board = MessageBoard.objects.order_by('-add_time')

        # 留言用户邮箱信息保密，将其中的部分字符转换成 * 号
        for message in message_board:
            name, addr = message.email.split('@')
            if len(name) > 5:
                name = name[0:3] + '*'*len(name[3:])
            else:
                addr = '*'*len(addr)
            message.email = name + '@' + addr

        # 用户留言分页
        old_message_page = request.session.get('message_board_page', 1)
        try:
            message_page = request.GET.get('message_page', 1)
            request.session['message_board_page'] = message_page
        except PageNotAnInteger:
            message_page = 1
        # 对数据库中所取出的所有对象，进行分页，中间的参数为每页显示的对象个数，设置为 6 个
        paginator = Paginator(message_board, 10, request=request, page_type='message_page')
        # 取出对应页的数据
        message_board_page = paginator.page(message_page)
        if old_message_page != message_page:
            message_focus = 'read'
        else:
            message_focus = 'add'
        return render(request, 'message.html', {
            'message': message_board_page,
            "focus": "message",
            "message_focus": message_focus
        })


class AddMessageView(View):
    """添加留言的视图类"""

    def post(self, request):
        """通过 ajax 提价留言"""
        message_board_form = forms.MessageBoardForm(request.POST)
        if message_board_form.is_valid():
            name = request.POST.get("name")
            email = request.POST.get("email")
            message = request.POST.get("message")
            message_board = MessageBoard()
            if request.user.is_authenticated:
                is_user = 'yes'
            else:
                is_user = 'no'
            message_board.name = name
            message_board.email = email
            message_board.message = message
            message_board.is_user = is_user
            message_board.save()
            return JsonResponse({"status": "success"})
        else:
            error_dict = message_board_form.errors
            error_str = json.dumps(error_dict)
            error_dict = json.loads(error_str)
            return JsonResponse({"status": "fail", 'message': error_dict})


class GetUserMessageView(View):
    """用户登录后，在右上角的状态栏中给出消息提示"""

    def get(self, request):
        """在页面加载完后，通过 ajax 来获取用户数据"""
        user = request.user
        # 最近的三条未读消息
        message_count = user.usermessage_set.filter(readable='unread').count()
        return JsonResponse({"status": "success", "counter": message_count})


class UploadFoodArticle(View):
    """用户上传文章请求的视图函数"""

    def post(self, request):
        """通过 ajax 来发送请求"""
        if request.user.is_authenticated:
            user = request.user
            if user.is_author == 'yes' and user.is_staff == True:
                url = reverse("xadmin:food_foodarticle_add")
                return JsonResponse({'status': 'success', "url": url})
            else:
                user.is_author = 'yes'
                user.is_staff = True
                user.save()
                authority = Group.objects.filter(name='美食作者').first()
                user.groups.add(authority)
                url = reverse("xadmin:food_foodarticle_add")
                return JsonResponse({'status':'success', "url": url})
        else:
            return JsonResponse({'status':'fail', "message": "用户未登录，无法执行此操作"})


# 官方文档链接：https://docs.djangoproject.com/en/2.0/ref/views/#error-views
# 全局 400 错误页面
def handler_400_error(request, exception, template_name='400_error_page.html'):
    from django.shortcuts import render_to_response
    response = render_to_response('400_error_page.html')
    response.status_code = 400
    return response


# 全局 403 错误页面
def handler_403_error(request, exception, template_name='403_error_page.html'):
    from django.shortcuts import render_to_response
    response = render_to_response('403_error_page.html')
    response.status_code = 403
    return response


# 全局 404 错误页面
def handler_404_error(request, exception, template_name='404_error_page.html'):
    from django.shortcuts import render_to_response
    response = render_to_response('404_error_page.html')
    response.status_code = 404
    return response


# 全局 500 错误页面， 这里注意，参数同其他3个的不一样，不需要 exception
def handler_500_error(request, template_name='500_error_page.html'):
    from django.shortcuts import render_to_response
    response = render_to_response('500_error_page.html')
    response.status_code = 500
    return response

