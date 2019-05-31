from django.apps import AppConfig


class FoodConfig(AppConfig):
    name = 'food'
    # 为模型定义别名
    verbose_name = u'美食与图片'
