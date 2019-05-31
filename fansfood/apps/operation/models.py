# _*_ coding: utf-8 _*_
from django.db import models
from django.utils import timezone

from user.models import UserProfiles


# 用户喜欢的模型类
class UserLike(models.Model):
    user = models.ForeignKey(
        UserProfiles,
        on_delete=models.CASCADE,
        to_field='username',
        db_column='username',
        verbose_name='用户'
    )
    like_id = models.CharField(max_length=30, verbose_name='喜欢的作品id', db_index=True, unique=True)
    like_type = models.CharField(
        choices=(('food_article', '美食文章'), ('food_image', '美食图片'), ('food_author', '美食作者')),
        max_length=20,
        verbose_name='喜欢的类型',
        default='food_article'
    )
    add_time = models.DateTimeField(default=timezone.now, verbose_name='添加时间')

    class Meta:
        db_table = 'user_like'
        verbose_name = '用户喜欢'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.like_id


# 用户收藏的模型类
class UserFav(models.Model):
    user = models.ForeignKey(
        UserProfiles,
        on_delete=models.CASCADE,
        to_field='username',
        db_column='username',
        verbose_name='用户'
    )
    fav_id = models.CharField(max_length=30, verbose_name='收藏的作品id', db_index=True, unique=True)
    fav_type = models.CharField(
        choices=(('food_article', '美食文章'), ('food_image', '美食图片'), ('food_author', '美食作者')),
        max_length=20,
        verbose_name='喜欢的类型',
        default='food_article'
    )
    add_time = models.DateTimeField(default=timezone.now, verbose_name='添加时间')

    class Meta:
        db_table = 'user_fav'
        verbose_name = '用户收藏'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.fav_id


# 用户消息的模型类
class UserMessage(models.Model):
    user = models.ForeignKey(
        UserProfiles,
        on_delete=models.CASCADE,
        to_field='username',
        db_column='username',
        verbose_name='用户'
    )
    readable = models.CharField(
        choices=(('unread', '未读消息'), ('read', '已读消息')),
        max_length=10,
        verbose_name='是否已读',
        default='unread'
    )
    message_title = models.CharField(max_length=80, verbose_name='消息主题')
    message_content = models.TextField(default='', verbose_name='消息内容')
    add_time = models.DateTimeField(default=timezone.now, verbose_name='添加时间')

    class Meta:
        db_table = 'user_message'
        verbose_name = '用户消息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.message_title


# 留言消息模型
class MessageBoard(models.Model):
    name = models.CharField(max_length=20, verbose_name='留言昵称')
    email = models.EmailField(max_length=245, verbose_name='留言邮箱')
    is_user = models.CharField(
        max_length=10,
        choices=(('yes', '是'), ('no', '不是')),
        default='yes',
        verbose_name='是否是注册用户')
    message = models.TextField(verbose_name='留言内容')
    add_time = models.DateTimeField(default=timezone.now, verbose_name='添加时间')

    class Meta:
        db_table = 'visitor_message'
        verbose_name = '留言消息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name