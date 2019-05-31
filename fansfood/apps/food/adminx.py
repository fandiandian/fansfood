# _*_ coding: utf-8 _*_
__author__ = 'nick'
__date__ = '2019/5/23 16:30'

import os
from PIL import Image
import shutil

import xadmin
from xadmin import views
from django_food.settings import BASE_DIR

from .models import FoodImage, FoodArticle, FoodSteps, Tags, ImageTags, FoodIngredients


# 关联 FoodSteps 模型，以便 FoodArticle 模型中可以控制 FoodSteps 模型
class FoodStepsInline:
    model = FoodSteps
    extra = 1


# 关联 FoodIngredients 模型，以便 FoodArticle 模型中可以控制 FoodIngredients 模型
class FoodIngredientsLine:
    model = FoodIngredients
    extra = 1


# 创建后台模型
class TagsAdmin:
    # 模型字段的后台显示
    list_display = ['name', 'add_time']
    # 字段的后台搜索功能（搜索依据的字段），时间不要做为搜索的条件，显示会有问题
    search_fields = ['name']
    # 字段的筛选功能，用于数据的显示
    list_filter = ['name', 'add_time']
    # 后台图标
    model_icon = "fa fa-tags"
    # 列表页可编辑字段
    list_editable = ['name']

    # 筛选出登录用户上传的美食文章相关的标签
    def queryset(self):
        qs = super().queryset()
        if self.request.user.is_superuser:
            return qs
        else:
            qs = qs.filter(foodarticle__author=self.request.user.username)
            return qs


class FoodIngredientsAdmin:
    # 模型字段的后台显示
    list_display = ['article_id', 'classification', 'name', 'dosage', 'add_time']
    # 字段的后台搜索功能（搜索依据的字段），时间不要做为搜索的条件，显示会有问题
    search_fields = ['article_id', 'classification', 'name', 'dosage']
    # 字段的筛选功能，用于数据的显示
    list_filter = ['article_id', 'classification', 'name', 'dosage', 'add_time']
    # 列表页可编辑字段
    list_editable = ['classification', 'name', 'dosage']
    exclude = ['add_time']
    # 后台图标
    model_icon = "fa fa-ellipsis-h"
    ordering = ['article_id', 'classification']

    # 筛选出登录用户上传的美食文章相关的制作步骤
    def queryset(self):
        qs = super().queryset()
        if self.request.user.is_superuser:
            return qs
        else:
            qs = qs.filter(article_id__author=self.request.user.username)
            return qs


class FoodArticleAdmin:
    # 模型字段的后台显示
    list_display = ['article_id', 'name', 'ingredient_list',
                    'image', 'author', 'like',
                    'fav', 'click_number', 'tags', 'add_time']
    # 字段的后台搜索功能（搜索依据的字段），时间不要做为搜索的条件，显示会有问题
    search_fields = ['article_id', 'name', 'ingredient_list',
                     'image', 'author', 'like',
                     'fav', 'click_number', 'tags']
    # 字段的筛选功能，用于数据的显示
    list_filter = ['article_id', 'name', 'ingredient_list',
                   'image', 'author', 'like',
                   'fav', 'click_number', 'tags', 'add_time']
    # 后台图标
    model_icon = "fa fa-lemon-o"
    # 动态的数据，可读不可写（后台无法更改数据）
    # readonly_fields = ['like', 'fav', 'click_number']
    # 后台控制字段的显示，添加到下面的列表中则可以使其不再后台显示
    # readonly_fields 和 exclude 中的字段是冲突的，不可以同时出现在两个列表中
    exclude = ['ingredient_list', 'author', 'like', 'fav', 'click_number']
    # 后台外键的数据加载方式，使用ajax加载，使用搜索功能
    relfield_style = 'fk-ajax'
    fk_fields = ['name']
    # 字段的后台显示风格，呈现的是左右结构，左边是所有的标签，右边是已选择的标签
    style_fields = {'tags': 'm2m_transfer'}
    # 用于一个模块管理另一个模块，实现可以在增加美食制作不走的时候，可以直接添加制作步骤，但是只能够做到一层嵌套
    inlines = [FoodIngredientsLine, FoodStepsInline]
    # 列表页可编辑字段
    list_editable = ['name']

    # 筛选出登录用户上传的美食文章(如果是超级用户，则显示所有的文章）
    def queryset(self):
        qs = super().queryset()
        if self.user.is_superuser:
            return qs
        else:
            qs = qs.filter(author=self.user.username)
            return qs

    def save_models(self):
        obj = self.new_obj

        # 修改图片数据，这是一个类是 python file 的文件对象
        image = self.request.FILES.get('image').read()
        path = os.path.join(BASE_DIR, 'media', 'food_article', f'{obj.article_id}')
        if not os.path.isdir(path):
            os.makedirs(path)
        # 保存完整的图片
        with open(os.path.join(path, 'full.jpg'), 'wb') as f:
            f.write(image)
        # 缩减图片尺寸
        with Image.open(os.path.join(path, 'full.jpg')) as img:
            img = img.convert("RGB")
            x, y = img.size
            new_x = 320
            new_y = int(y * new_x / x)
            small_image = img.resize((new_x, new_y), Image. ANTIALIAS)
            small_image.save(os.path.join(path, 'small.jpg'))

        # 获取文章的作者，原料数据和图片数据
        obj.author = self.user.username
        obj.image = os.path.join('food_article', f'{obj.article_id}', 'small.jpg')
        in_list = []
        food_in_length = int(self.request.POST.get('foodingredients_set-TOTAL_FORMS', 0))
        for i in range(0, food_in_length):
            in_list.append(self.request.POST.get(f"foodingredients_set-{i}-name"))
        if in_list:
            obj.ingredient_list = "原料：" + ','.join(in_list)
        # 保存数据
        obj.save()

    def delete_models(self, obj):
        remove_list = (
            os.path.join(BASE_DIR, 'media', 'food_article', f'{item.article_id}')
            for item in obj
        )
        for item in remove_list:
            shutil.rmtree(item)
        obj.delete()


    # # 根据登录用户的类型来选择文章模型显示的数据
    # def get_model_form(self, **kwargs):
    #     user = self.request.user
    #     if user.is_superuser:
    #         self.readonly_fields = ['like', 'fav', 'click_number']
    #         self.exclude = []
    #     else:
    #         self.readonly_fields = []
    #         self.exclude = ['ingredient_list', 'author', 'like', 'fav', 'click_number']
    #     return super().author_display()


# # 这个后台模型适用于用户（作者）的相关的数据显示
# # 他只能看到他自己的文章数据
# class UserFoodArticleAdmin:
#     # 模型字段的后台显示
#     list_display = ['article_id', 'name', 'ingredient_list',
#                     'image', 'author', 'like',
#                     'fav', 'click_number', 'tags', 'add_time']
#     # 字段的后台搜索功能（搜索依据的字段），时间不要做为搜索的条件，显示会有问题
#     search_fields = ['article_id', 'name', 'ingredient_list',
#                      'image', 'author', 'like',
#                      'fav', 'click_number', 'tags']
#     # 字段的筛选功能，用于数据的显示
#     list_filter = ['article_id', 'name', 'ingredient_list',
#                    'image', 'author', 'like',
#                    'fav', 'click_number', 'tags', 'add_time']
#     # 后台图标
#     model_icon = "fa fa-lemon-o"
#     # 动态的数据，可读不可写（后台无法更改数据）
#     readonly_fields = ['like', 'fav', 'click_number']
#     # 后台控制字段的显示，添加到下面的列表中则可以使其不再后台显示
#     # readonly_fields 和 exclude 中的字段是冲突的，不可以同时出现在两个列表中
#     # exclude = []
#     # 后台外键的数据加载方式，使用ajax加载，使用搜索功能
#     relfield_style = 'fk-ajax'
#     # 字段的后台显示风格，呈现的是左右结构，左边是所有的标签，右边是已选择的标签
#     style_fields = {'tags': 'm2m_transfer'}
#     # 用于一个模块管理另一个模块，实现可以在增加美食制作不走的时候，可以直接添加制作步骤，但是只能够做到一层嵌套
#     inlines = [FoodStepsInline]


class FoodStepsAdmin:
    # 模型字段的后台显示
    list_display = ['article_id', 'step_number', 'description',
                    'image', 'add_time']
    # 字段的后台搜索功能（搜索依据的字段），时间不要做为搜索的条件，显示会有问题
    search_fields = ['article_id', 'step_number', 'description',
                     'image']
    # 字段的筛选功能，用于数据的显示
    list_filter = ['article_id', 'step_number', 'description',
                   'image', 'add_time']
    # 后台图标
    model_icon = "fa fa-spinner"
    # 后台排序
    ordering = ['-article_id', 'step_number']
    # 列表页可编辑字段
    list_editable = ['description']
    exclude = ['add_time']

    # 筛选出登录用户上传的美食文章相关的制作步骤
    def queryset(self):
        qs = super().queryset()
        if self.request.user.is_superuser:
            return qs
        else:
            qs = qs.filter(article_id__author=self.request.user.username)
            return qs


class ImageTagsAdmin:
    # 模型字段的后台显示
    list_display = ['name', 'add_time']
    # 字段的后台搜索功能（搜索依据的字段），时间不要做为搜索的条件，显示会有问题
    search_fields = ['name']
    # 字段的筛选功能，用于数据的显示
    list_filter = ['name', 'add_time']
    # 后台图标
    model_icon = "fa fa-tags"
    # 列表页可编辑字段
    list_editable = ['name']


class FoodImageAdmin:
    # 模型字段的后台显示
    list_display = ['name', 'image', 'like', 'fav',
                    'click_number', 'tags', 'add_time']
    # 字段的后台搜索功能（搜索依据的字段），时间不要做为搜索的条件，显示会有问题
    search_fields = ['name', 'image', 'like', 'fav',
                     'click_number', 'tags', 'add_time']
    # 字段的筛选功能，用于数据的显示
    list_filter = ['name', 'image', 'like', 'fav',
                   'click_number', 'tags', 'add_time']
    # 后台图标
    model_icon = "fa fa-picture-o"
    # 动态的数据，可读不可写（后台无法更改数据）
    readonly_fields = ['like', 'fav', 'click_number']
    # 字段的后台显示风格，呈现的是左右结构，左边是所有的标签，右边是已选择的标签
    style_fields = {'tags': 'm2m_transfer'}
    # 列表页可编辑字段
    list_editable = ['tags']


# 注册到后台，参数：数据模型, 后台模型
xadmin.site.register(FoodArticle, FoodArticleAdmin)
xadmin.site.register(FoodIngredients, FoodIngredientsAdmin)
xadmin.site.register(FoodSteps, FoodStepsAdmin)
xadmin.site.register(Tags, TagsAdmin)
xadmin.site.register(FoodImage, FoodImageAdmin)
xadmin.site.register(ImageTags, ImageTagsAdmin)



