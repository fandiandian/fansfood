# _*_ coding: utf-8 _*_

"""
food 的视图相关的类，包括排行榜，文章详情，所有图片，单张图片
从 MongoDB 转换数据到 MySQL 的函数
"""

import random
import os
from PIL import Image

from django.shortcuts import render
from django.views.generic.base import View
from pure_pagination import Paginator, PageNotAnInteger
from django_food.settings import BASE_DIR
from django.db.models import Q

from assist_function.mongodb.mongo_client import mongo_client
from .models import FoodArticle, Tags, FoodSteps, FoodImage, ImageTags, FoodIngredients


class FoodRankingView(View):
    """美食排行的请求响应视图类"""

    def get(self, request):
        """排行榜的 get 方法"""
        food_list = FoodArticle.objects.order_by("-like")

        # 热门食物--做过的人最多
        popular_food = FoodArticle.objects.order_by("-fav")[:3]

        # 无数据的情况
        if food_list:
            message = True
        else:
            message = False

        # 获取页面传回的分页数值，默认为 1（第一页）
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        # 对数据库中所取出的所有对象，进行分页，中间的参数为每页显示的对象个数，设置为 6 个
        paginator = Paginator(food_list, 12, request=request)
        # 取出对应页的数据
        food_list_page = paginator.page(page)

        return render(request, 'food/food_ranking.html', {
            "food_list": food_list_page,
            "popular_food": popular_food,
            "message": message,
            "focus": "article",                              # 选中状态标志
        })


class FoodArticleView(View):
    """获取美食文章请求的视图类"""

    def get(self, request, article_id):
        """ get 请求"""

        # 热门食物--做过的人最多
        popular_food = FoodArticle.objects.all() \
            .order_by("-fav")[:3]

        # 根据文章的 article_id 从 MySQL 数据库中提取文章数据
        food = FoodArticle.objects.get(article_id=article_id)
        # 点击量加1
        food.click_number += 1
        food.save()

        # 图片处理
        print(food.image.url)
        path = '/'.join(food.image.url.split("/")[2:-1])
        # print(str(food.image))
        # print(path)
        # path = os.path.split(food.image.name)[0]
        food_image = os.path.join(path, 'full.jpg')
        food_image = food_image
        print(food_image)
        # 获取步骤数据
        food_steps = FoodSteps.objects.filter(article_id=article_id).order_by('step_number')

        # 数据从 MongoDB 中转储到 MySQL 中了，所以就不需要了
        # # 根据文章的 article_id 从 MongoDB 数据库中提取配料信息
        # conn = mongo_client()
        # food_info = conn.food.food_data.find_one({"random_id": article_id})
        # conn.close()
        # 食材配方信息
        food_info = FoodIngredients.objects.filter(article_id=article_id)
        # 主料
        food_info_1 = food_info.filter(classification='1')
        # 辅料
        food_info_2 = food_info.filter(classification='2')
        # 配料
        food_info_3 = food_info.filter(classification='3')

        # 判断用户是否登录, 用户获取用户的喜欢和收藏信息
        user = request.user
        if user.is_authenticated:
            like = user.userlike_set.filter(like_id=food.article_id)
            if like:
                like_status = 'yes'
            else:
                like_status = 'no'

            fav = user.userfav_set.filter(fav_id=food.article_id)
            if fav:
                fav_status = 'yes'
            else:
                fav_status = 'no'
        else:
            like_status = 'unsigned'
            fav_status = 'unsigned'

        return render(request, 'food/food_article.html', {
            "food": food,
            "food_image": food_image,
            "food_steps": food_steps,
            "food_info_1": food_info_1,
            "food_info_2": food_info_2,
            "food_info_3": food_info_3,
            "popular_food": popular_food,
            "like_status": like_status,
            "fav_status": fav_status,
            "focus": "article",                           # 选中状态标志
        })


class TagFoodView(View):
    """根据标签在数据库中查找文章数据，并返回"""

    def get(self, request, tag):
        """文章标签的 get 请求视图函数"""

        # 根据标签提取数据
        food_tag = Tags.objects.get(name=tag)
        food_articles = food_tag.foodarticle_set.order_by("-like")

        # 热门食物--做过的人最多
        popular_food = FoodArticle.objects.all().order_by("-fav")[:3]

        # 获取页面传回的分页数值，默认为 1（第一页）
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        # 对数据库中所取出的所有对象，进行分页，中间的参数为每页显示的对象个数，设置为 6 个
        paginator = Paginator(food_articles, 12, request=request)
        # 取出对应页的数据
        food_list_page = paginator.page(page)

        return render(request, 'food/food_ranking.html', {
            "food_list": food_list_page,
            "popular_food": popular_food,
            "message": True,
            "focus": "article",                              # 选中状态标志
        })


class FoodImageRankView(View):
    """图片请求的视图类， 返回所有的图片的缩略图"""

    def get(self, request):
        """所有图片的 get 请求的响应函数"""
        food_image = FoodImage.objects.order_by('-fav')

        # 热门食物--做过的人最多
        popular_food = FoodArticle.objects.all().order_by("-fav")[:3]

        # 无数据的情况
        if food_image:
            message = True
        else:
            message = False

        # 获取页面传回的分页数值，默认为 1（第一页）
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        # 对数据库中所取出的所有对象，进行分页，中间的参数为每页显示的对象个数，设置为 6 个
        paginator = Paginator(food_image, 20, request=request)
        # 取出对应页的数据
        image_list = paginator.page(page)

        return render(request, "food/food_image_rank.html", {
            "image_list": image_list,
            "popular_food": popular_food,
            "message": message,
            "focus": "image",                         # 选中状态标志
        })


class SingleFoodImageView(View):
    """图片请求的视图类， 返回图片的原始大小"""

    def get(self, request, image_id):

        image = FoodImage.objects.get(name=image_id)
        image.click_number += 1
        image.save()

        # path = os.path.split(str(image.image))[0]
        path = '/'.join(image.image.url.split('/')[2:-1])
        image.image = os.path.join(path, f'{image.name}-full.jpg')

        # 热门食物--做过的人最多
        popular_food = FoodArticle.objects.all()\
            .order_by("-fav")[:3]

        # 判断用户是否登录, 用户获取用户的喜欢和收藏信息
        user = request.user
        if user.is_authenticated:
            like = user.userlike_set.filter(like_id=image.name)
            if like:
                like_status = 'yes'
            else:
                like_status = 'no'

            fav = user.userfav_set.filter(fav_id=image.name)
            if fav:
                fav_status = 'yes'
            else:
                fav_status = 'no'
        else:
            like_status = 'unsigned'
            fav_status = 'unsigned'

        return render(request, "food/food_image.html", {
            'image': image,
            "popular_food": popular_food,
            "like_status": like_status,
            "fav_status": fav_status,
            "focus": "image",                         # 选中状态标志
        })


class TagImageView(View):
    """根据标图片签在数据库中查找图片数据，并返回"""

    def get(self, request, tag):
        """图片标签的 get 请求视图函数"""

        # 根据标签提取数据
        image_tag = ImageTags.objects.get(name=tag)
        images = image_tag.foodimage_set.order_by("-like")

        # 热门食物--做过的人最多
        popular_food = FoodArticle.objects.order_by("-fav")[:3]

        # 获取页面传回的分页数值，默认为 1（第一页）
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        # 对数据库中所取出的所有对象，进行分页，中间的参数为每页显示的对象个数，设置为 6 个
        paginator = Paginator(images, 12, request=request)
        # 取出对应页的数据
        image_list = paginator.page(page)

        return render(request, 'food/food_image_rank.html', {
            "image_list": image_list,
            "popular_food": popular_food,
            "message": True,
            "focus": "image",                              # 选中状态标志
        })


class SearchView(View):
    """搜索视图类"""

    def get(self, request):
        """使用 post 请求"""
        keyword = request.GET.get('keyword', "")
        search_type = request.GET.get('type', "")

        if search_type == "美食文章":
            # 食物文章的搜索
            search_food_article = FoodArticle.objects.filter(
                Q(tags__name__icontains=keyword) |
                Q(ingredient_list__icontains=keyword) |
                Q(name__icontains=keyword)
            ).distinct().order_by('-fav')

            # 热门食物--做过的人最多
            popular_food = FoodArticle.objects.all().order_by("-fav")[:3]

            # 无搜索结果
            if search_food_article:
                message = True
            else:
                message = False

            # 获取页面传回的分页数值，默认为 1（第一页）
            try:
                page = request.GET.get('page', 1)
            except PageNotAnInteger:
                page = 1
            # 对数据库中所取出的所有对象，进行分页，中间的参数为每页显示的对象个数，设置为 6 个
            paginator = Paginator(search_food_article, 20, request=request)
            # 取出对应页的数据
            food_article_list = paginator.page(page)

            return render(request, "food/food_ranking.html", {
                "food_list": food_article_list,
                "popular_food": popular_food,
                "message": message,
                "focus": "article",                                   # 选中状态标志
            })

        else:
            # 美食图片的搜索
            search_food_image = FoodImage.objects.filter(
                tags__name__icontains=keyword
            ).distinct().order_by('-fav')

            # 热门食物--做过的人最多
            popular_food = FoodArticle.objects.all().order_by("-fav")[:3]

            # 无搜索结果
            if search_food_image:
                message = True
            else:
                message = False

            # 获取页面传回的分页数值，默认为 1（第一页）
            try:
                page = request.GET.get('page', 1)
            except PageNotAnInteger:
                page = 1
            # 对数据库中所取出的所有对象，进行分页，中间的参数为每页显示的对象个数，设置为 6 个
            paginator = Paginator(search_food_image, 20, request=request)
            # 取出对应页的数据
            image_list = paginator.page(page)

            return render(request, "food/food_image_rank.html", {
                "image_list": image_list,
                "popular_food": popular_food,
                "message": message,
                "focus": "image",  # 选中状态标志
            })


# 数据转储函数
def data_transform():
    """
    将 mongodb 中的数据转储到 mysql 数据库中
    主要是将排行榜中的数据进行转储，因为没有爬取到食物的点赞数和收藏数，通转转储随机生成
    """
    conn = mongo_client()
    # 从 food_rank 集合中提取文档
    data = conn.food.food_rank.find({}).batch_size(30)
    for item in data:
        food_article = FoodArticle()
        food_article.article_id = item["random_id"]
        food_article.name = item["name"]
        food_article.image = item["image_path"]
        food_article.author = item["author"]
        food_article.ingredient_list = item["ingredient_list"]
        food_article.count = item["count"]
        # 获取文章的评分， 从 food_data 集合中提取文档
        evaluation_tag_conn = mongo_client()
        evaluation_tag = evaluation_tag_conn.food.food_data.find_one({
            "random_id": item["random_id"]
        })
        # 文章的评分
        food_article.like = evaluation_tag["evaluation"]['like']
        food_article.fav = evaluation_tag["evaluation"]['fav']
        food_article.click_number = random.randint(2000, 5000)
        food_article.save()
    conn.close()


# 建立文章与标签的关联表 ManyToMany
def add_article_tags():
    """
    无法在一个函数内实现，只能在写一个函数来单独添加文章的标签
    """
    conn = mongo_client()
    # 从 food_data 集合中提取文档
    data = conn.food.food_data.find({}).batch_size(30)
    for item in data:
        food_article = FoodArticle.objects.get(article_id=item['random_id'])
        for tag in item['tags_list']:
            food_tag = Tags.objects.get(name=tag)
            food_article.tags.add(food_tag)
        food_article.save()
    conn.close()


# 标签数据的提取
def get_tags():
    """从 MongoDB 中提取美食文章的标签"""
    conn = mongo_client()
    data = conn.food.food_data.find({}).batch_size(30)
    for item in data:
        for tag in item["tags_list"]:
            if not Tags.objects.filter(name=tag):
                Tags.objects.create(name=tag)
    conn.close()


# 制作步骤的提取
def get_steps():
    """从 MongoDB 中提取美食文章的制作步骤"""
    conn = mongo_client()
    # 从 food_data 集合中提取
    data = conn.food.food_data.find({}).batch_size(30)
    for item in data:
        for step in item["steps_list"]:
            food_step = FoodSteps()
            article = FoodArticle.objects.get(article_id=item["random_id"])
            # 这里必须是 FoodArticle 的实例才能建立起一对多的关联
            # 直接使用 item["random_id"] 会报错
            food_step.article_id = article
            food_step.step_number = step["step_number"]
            food_step.image = step['step_image_path']
            food_step.description = step['step_info']
            food_step.save()


# 缩减图片尺寸，并保存到 MySQL 数据库中
def resize_image():
    """食物图片处理函数"""
    conn = mongo_client()
    data = conn.food.food_image.find({}).batch_size(30)
    for item in data:
        path = os.path.join(BASE_DIR, "media", 'food_image', item['random_id'])
        full_image = Image.open(os.path.join(path, f'{item["random_id"]}-full.jpg'))
        (x, y) = full_image.size
        new_x = 480
        new_y = int(y * new_x / x)
        small_image = full_image.resize((new_x, new_y), Image.ANTIALIAS)
        if small_image.mode != "RGB":
            small_image = small_image.convert("RGB")
        small_image.save(os.path.join(path, f'{item["random_id"]}-small.jpg'))
        full_image.close()
    conn.close()


# 图片数据转储到 MySQL
def image_transform():
    """将 MongoDB 中的图片数据转储到 MySQL"""
    conn = mongo_client()
    data = conn.food.food_image.find({}).batch_size(30)
    for item in data:
        for tag in item["tags_list"]:
            if not ImageTags.objects.filter(name=tag):
                ImageTags.objects.create(name=tag)
        image = FoodImage()
        image.name = item["random_id"]
        image.image = os.path.join('food_image', item['random_id'], f'{item["random_id"]}-small.jpg')
        image.save()
    conn.close()


def add_image_tags():
    """为图片添加标签数据"""
    conn = mongo_client()
    data = conn.food.food_image.find({}).batch_size(30)
    for item in data:
        image = FoodImage.objects.get(name=item['random_id'])
        for tag in item["tags_list"]:
            image_tag = ImageTags.objects.get(name=tag)
            image.tags.add(image_tag)
        image.save()
    conn.close()


def delete_error_image():
    """删除错误图片数据"""
    import shutil

    path = os.path.join(BASE_DIR, 'media', 'food_image')
    wrong_set = {name for name in os.listdir(path)}
    right_set = set()
    conn = mongo_client()
    data = conn.food.food_image.find({}).batch_size(30)
    for item in data:
        right_set.add(item["random_id"])
    conn.close()
    diff = wrong_set - right_set
    print(len(diff))
    for name in diff:
        shutil.rmtree(os.path.join(path, name))


# 修改图片的喜欢数，收藏数和点击数
def image_like():
    """随机数据不能定义在模型中，程序在运行时会直接编译，导致所有的随机数据都是一样的"""
    conn = mongo_client()
    data = conn.food.food_image.find({}).batch_size(30)
    for item in data:
        image = FoodImage.objects.get(name=item["random_id"])
        image.like = random.randint(200, 500)
        image.fav = random.randint(500, 2000)
        image.click_number = random.randint(2000, 5000)
        image.save()
    conn.close()


# 图片数据转储到 MySQL
def image_transform_1():
    """将 MongoDB 中的图片数据转储到 MySQL"""
    conn = mongo_client()
    data = conn.food.food_image.find({}).batch_size(30)
    for item in data:
        image = FoodImage.objects.get(name=item["random_id"])
        image.image = os.path.join('food_image', item['random_id'], f'{item["random_id"]}-small.jpg')
        image.save()
    conn.close()


# 为了实现用户上传文章数据，需要将原来存储在 MongoDB 中的数据库
# 的数据转储到 MySQL 中
def food_data_transform():
    conn = mongo_client()
    data = conn.food.food_data.find({}).batch_size(30)
    for item in data:
        for ingredient in item['ingredients_list']:
            for key, value in ingredient['formulas'].items():
                food = FoodArticle.objects.get(article_id=item['random_id'])
                food_in = FoodIngredients()
                food_in.article_id = food
                if ingredient['name'] == '主料':
                    key_name = '1'
                elif ingredient['name'] == '辅料':
                    key_name = '2'
                else:
                    key_name = '3'
                food_in.name = key
                food_in.dosage = value
                food_in.classification = key_name
                food_in.save()
    conn.close()


def food_data_transform_1():
    conn = mongo_client()
    data = conn.food.food_data.find({}).batch_size(30)
    for item in data:
        food = FoodArticle.objects.get(article_id=item['random_id'])
        food.description = item['desc']
        food.tips = item['tip_info']
        food.save()
    conn.close()





