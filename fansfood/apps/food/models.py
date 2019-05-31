# _*_ coding: utf-8 _*_

"""美食 app 相关的模型"""


import os
import random
import time

from django.db import models
from django.utils import timezone


# Create your models here.
def food_article_image_upload_path(instance, filename):
    """缩略图片上传路径"""
    return os.path.join(
        "food_article",
        instance.article_id,
        filename
    )


def food_article_step_image_upload_path(instance, filename):
    """步骤图片上传路径"""
    return os.path.join(
        "food_article",
        instance.article_id,
        'step',
        filename
    )


def food_image_upload_path(filename):
    """美食图片上传路径"""
    return os.path.join(
        "food_image",
        "%Y/%m",
        filename
    )


def create_random_id():
    """产生文章或图片的随机id"""
    stings = "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890abcdefghijklmnopqrstuvwxyz"
    random_string = "".join(random.sample(stings, 8))
    return f'{int(time.time())}-{random_string}'


class Tags(models.Model):
    """美食类型标签"""
    name = models.CharField(max_length=20, default="", verbose_name="标签")
    add_time = models.DateTimeField(default=timezone.now, verbose_name="添加时间")

    class Meta:
        db_table = "food_tags"
        verbose_name = "美食标签"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class FoodArticle(models.Model):
    """美食文章模型"""
    article_id = models.CharField(
        max_length=24,
        default=create_random_id,
        verbose_name="文章的id",
        unique=True                                  # 唯一约束
    )
    name = models.CharField(
        max_length=100,
        default="",
        verbose_name="食物名称",
        db_index=True                                # 创建文章名称的索引
    )
    description = models.TextField(verbose_name='食物描述', default='')
    ingredient_list = models.CharField(
        max_length=200,
        default="",
        verbose_name="原料表"
    )
    image = models.ImageField(
        upload_to=food_article_image_upload_path,
        null=True,
        blank=True,
        verbose_name="封面图"
    )
    author = models.CharField(
        max_length=100,
        default="",
        verbose_name="作者",
        db_index=True                                # 创建文章作者的索引
    )
    like = models.IntegerField(default=0, verbose_name="喜欢人数")
    fav = models.IntegerField(default=0, verbose_name="收藏人数")
    click_number = models.IntegerField(default=0, verbose_name="点击数")
    tags = models.ManyToManyField(
        Tags, blank=True, verbose_name="内容标签", db_index=True
    )
    tips = models.TextField(verbose_name='小贴士', default='')
    add_time = models.DateTimeField(default=timezone.now, verbose_name="添加时间")

    class Meta:
        db_table = "food_article"
        verbose_name = "美食文章"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class FoodIngredients(models.Model):
    """食物制作需要的食材"""
    article_id = models.ForeignKey(
        FoodArticle,
        on_delete=models.CASCADE,
        to_field="article_id",  # 指定外键关联主表的字段
        db_column="article_id",  # 为外键设定别名
        verbose_name='文章名称'
    )
    name = models.CharField(max_length=50, verbose_name='食材名称')
    dosage = models.CharField(max_length=20, verbose_name='食材用量')
    classification = models.CharField(
        choices=(('1', '主料'), ('2', '辅料'), ('3', '配料')),
        max_length=10,
        verbose_name='食材分类',
        default='1'
    )
    add_time = models.DateTimeField(default=timezone.now, verbose_name="添加时间")

    class Meta:
        db_table = 'food_ingredients'
        verbose_name = '食材'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class FoodSteps(models.Model):
    """食物的制作步骤"""
    article_id = models.ForeignKey(
        FoodArticle,
        on_delete=models.CASCADE,
        to_field="article_id",                        # 指定外键关联主表的字段
        db_column="article_id",                       # 为外键设定别名
        verbose_name='文章名称'
    )
    step_number = models.IntegerField(
        default=0, verbose_name="制作步骤序号"
    )
    description = models.TextField(
        default='',
        verbose_name="制作步骤描述"
    )
    image = models.ImageField(
        verbose_name="制作步骤图片",
        upload_to=food_article_step_image_upload_path,
        null=True,
        blank=True
    )
    add_time = models.DateTimeField(default=timezone.now, verbose_name="添加时间")

    class Meta:
        db_table = "food_steps"
        verbose_name = "美食制作步骤"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.description


# 发现可以直接在后台模型中进行筛选，故不需要此模型了
# class UserFoodArticle(FoodArticle):
#     """此模型仅是用于后台数据模型的注册和筛选，并不会在数据库中生成新的数据表"""
#
#     class Meta:
#         verbose_name = '用户上传的文章'
#         verbose_name_plural = verbose_name
#         # 此参数控制模型是否在数据库中生成数据表，默认为 False
#         # 设置为 True 时数据库中不会生成数据表
#         proxy = True


class ImageTags(models.Model):
    """美食图片类型标签"""
    name = models.CharField(max_length=20, default="", verbose_name="图片标签", db_index=True)
    add_time = models.DateTimeField(default=timezone.now, verbose_name="添加时间")

    class Meta:
        db_table = "food_imagestags"
        verbose_name = "图片标签"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class FoodImage(models.Model):
    """美食图片的模型"""
    name = models.CharField(max_length=50, verbose_name='图片名称', default=create_random_id, db_index=True)
    image = models.ImageField(
        upload_to=food_image_upload_path,
        blank=True,
        verbose_name="美食图片"
    )
    # 未能爬取到喜欢数和收藏数，使用随机数

    like = models.IntegerField(default=0, verbose_name="喜欢人数")
    fav = models.IntegerField(default=0, verbose_name="收藏人数")
    click_number = models.IntegerField(default=0, verbose_name="点击数")
    tags = models.ManyToManyField(ImageTags, blank=True, verbose_name="图片标签", db_index=True)
    add_time = models.DateTimeField(auto_now_add=True, verbose_name="添加时间")

    class Meta:
        db_table = "food_images"
        verbose_name = "美食图片"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name
