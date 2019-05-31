#!/usr/bin/env python3
# _*_ coding: utf-8 _*_

# 这里导入 python 内建库
import os
import json

# 这里导入 python 第三方库
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser
import time


# 定义动态文件的上传路径-用户图片
def upload_user_image_path(instance, filename):
    return os.path.join(
        'user',
        instance.username + "_" + str(instance.id),
        'head_portrait',
        filename
    )


# 定义验证码图片的上传路径
def recode_image_path(filename):
    return os.path.join(
        'recode_image',
        filename
    )


# 通过数字从数据库中提取图片验证码
def get_recode_image(number):
    return RecodeImage.objects.get(recode_number=number)


# 定义获取地址信息
def get_provinces():
    province_list = [(item.pid, item.name) for item in Provinces.objects.all()]
    return province_list


def get_cities(pid):
    city_list = [(item.cid, item.name) for item in Cities.objects.filter(pid=pid)]
    return city_list


def get_regions(pid, cid):
    region_list = [(item.cid, item.name) for item in Regions.objects.filter(pid=pid, cid=cid)]
    return region_list


class UserProfiles(AbstractUser):
    """
    扩展 django 自带的用户模型，继承自 AbstractUser
    AbstractUser 自带的属性如下：
    (id, password, last_login, first_name, last_name,
    username, email, is_superuser, is_staff, date_joined, is_alive)
    """

    nick_name = models.CharField(max_length=30, verbose_name="昵称", default="")
    head_portrait = models.ImageField(
        upload_to=upload_user_image_path,
        default='user/default_head_portrait/default.png',
        blank=True,
        verbose_name="头像"
    )
    gender = models.CharField(
        choices=(("male", "男"),("female", "女")),
        default="male",
        verbose_name="性别",
        max_length=6
    )
    is_author = models.CharField(
        choices=(("yes", "是"),("no", "否")),
        default="no",
        verbose_name="是否是美食作者",
        max_length=6
    )
    birthday = models.DateField(null=True, blank=True, verbose_name="生日")
    address = models.CharField(max_length=50, verbose_name="地区", blank=True, default="")
    signature = models.CharField(max_length=80, verbose_name="个性签名", blank=True, default="")

    class Meta:
        verbose_name = "用户信息"
        verbose_name_plural = verbose_name
        db_table = "user_profiles"

    def __str__(self):
        return self.username

    def get_head_portrait_json(self):
        d = {"head_portrait": str(getattr(self, 'head_portrait'))}
        return json.dumps(d)


# 省：Provinces, 市：cities， 区：regions
class Provinces(models.Model):
    pid = models.IntegerField(verbose_name="城市编号", default=0)
    name = models.CharField(max_length=10, verbose_name="省份", default="")
    add_time = models.DateTimeField(default=timezone.now, verbose_name="添加时间")

    class Meta:
        verbose_name = "省份"
        verbose_name_plural = verbose_name
        db_table = "address_provinces"

    def __str__(self):
        return self.name


class Cities(models.Model):
    pid = models.IntegerField(verbose_name="省份编号", default=0)
    cid = models.IntegerField(verbose_name="城市编号", default=0)
    name = models.CharField(max_length=20, verbose_name="城市", default="")
    add_time = models.DateTimeField(default=timezone.now, verbose_name="添加时间")

    class Meta:
        verbose_name = "城市"
        verbose_name_plural = verbose_name
        db_table = "address_cities"

    def __str__(self):
        return self.name


class Regions(models.Model):
    """对于不设去的城市，直接将下级的镇向上调整到县区级"""
    pid = models.IntegerField(verbose_name="省份编号", default=0)
    cid = models.IntegerField(verbose_name="城市编号", default=0)
    rid = models.IntegerField(verbose_name="区县编号", default=0)
    name = models.CharField(max_length=20, verbose_name="区县", default="")
    add_time = models.DateTimeField(default=timezone.now, verbose_name="添加时间")

    class Meta:
        verbose_name = "区县"
        verbose_name_plural = verbose_name
        db_table = "address_regions"

    def __str__(self):
        return self.name


class EmailVerifyCode(models.Model):
    """
    邮箱验证码
    设定可激活的次数为 1
    可根据发送的时间来设定验证码的时间有效性
    添加日期是 datetime.datetime.now(), 可以使用 timedelta(seconds=600) 作为时间差
    if (timezone.now() - send_time).total_seconds() > 0: 所还在有效期内
    """
    code = models.CharField(max_length=20, verbose_name="邮箱验证码")
    email = models.EmailField(max_length=245, verbose_name="邮箱")
    send_type = models.CharField(
        choices=(('register', u'注册'), ('forget', u'找回密码'), ('reset_email', u'重置邮箱')),
        max_length=20,
        verbose_name=u'验证码类型'
    )
    verify_times = models.IntegerField(default=1, verbose_name="可验证次数")
    send_time = models.DateTimeField(default=timezone.now, verbose_name=u'发送时间')

    class Meta:
        verbose_name = u'邮件验证码'
        verbose_name_plural = verbose_name
        db_table = "email_verify_coder"

    def __str__(self):
        return '{0} > ({1})'.format(self.email, self.code)

    def remove_invalid_code(self):
        if self.send_time.timestamp() - time.time() > 600:
            self.delete()


class RecodeImage(models.Model):
    """图片验证码"""
    recode_image_name = models.CharField(max_length=10, default="", verbose_name="验证码图片名称")
    recode_number_a = models.IntegerField(default=0, verbose_name="验证码数字a")
    recode_number_b = models.IntegerField(default=0, verbose_name="验证码数字b")
    recode_image_path = models.ImageField(
        upload_to=recode_image_path,
        verbose_name="验证码图片"
    )
    add_time = models.DateTimeField(default=timezone.now, verbose_name="添加时间")

    class Meta:
        verbose_name = u'图片验证码'
        verbose_name_plural = verbose_name
        db_table = "recode_image"

    def __str__(self):
        return self.recode_image_name

    def to_json(self):
        """
        序列模型实例，让具体的模型实例可以 json 化

        属性说明：
        a = RecodeImage.objects.get(recode_number="5+8")
        a._meta --> (<django.db.models.fields.AutoField: id>,
                    <django.db.models.fields.CharField: recode_number>,
                    <django.db.models.fields.files.ImageField: recode_image_path>,
                    <django.db.models.fields.DateTimeField: add_time>)
                    这是一个可迭代的对象，通过遍历，取得每个字段的名字（field.name）
        getattr(self, attr) -->  获取模型实例的字段值
        ImageField 字段使用 str() 字符串化
        """

        fields = []
        for field in self._meta.fields:
            fields.append(field.name)

        d = {}
        for attr in fields:
            d[attr] = str(getattr(self, attr))

        return json.dumps(d)

