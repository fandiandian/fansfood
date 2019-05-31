# _*_ coding: utf-8 _*_
__author__ = 'nick'
__date__ = '2019/5/4 22:51'


from django.urls import path

from . import views

app_name = "food"

urlpatterns = [
    # 美食文章
    path("food_article/<slug:article_id>/", views.FoodArticleView.as_view(), name="food_article"),
    # 美食排行榜
    path("food_ranking/", views.FoodRankingView.as_view(), name="food_ranking"),
    # 食物标签
    path("tag_food/<path:tag>", views.TagFoodView.as_view(), name="tag_food"),
    # 全部美食图片
    path("food_image_rank/", views.FoodImageRankView.as_view(), name="food_image_rank"),
    # 美食大图
    path("food_image/<slug:image_id>/", views.SingleFoodImageView.as_view(), name="food_image"),
    # 图片标签
    path("tag_image/<path:tag>", views.TagImageView.as_view(), name="tag_image"),
    # 搜索功能
    path("search/", views.SearchView.as_view(), name="search"),

]