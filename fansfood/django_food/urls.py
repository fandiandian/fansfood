"""django_food URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

# from django.contrib import admin
from django.urls import path, include
import xadmin
# 静态文件服务器模块
from django.views.static import serve
# 导入配置文件
from django_food import settings
# 导入主页视图类
from user.views import HomePageView, about
from operation import views as operation_views


urlpatterns = [

    # 原生的后台管理 admin 模块
    # path('admin/', admin.site.urls),
    # 使用 xadmin 做为后台管理系统
    path("center/", xadmin.site.urls),

    # 主页
    path("", HomePageView.as_view(), name="home_page"),

    # 美食文章
    path("food/", include("food.urls")),

    # 用户相关， include 参数要注意：不要带有 apps，否者或报错
    path("user/", include("user.urls")),

    # 用户中心
    path("user_center/", include("operation.urls")),

    # 配置图片请求
    path('media/<path:path>/', serve, {'document_root': settings.MEDIA_ROOT}),

    # 验证码插件
    path('captcha/', include('captcha.urls')),

    # 用户留言
    path('message/', operation_views.MessageBoardView.as_view(), name="message"),

    # 关于
    path('about/', about, name='about'),

    # 配置静态文件路径，用于调试 404 等错误页面
    # path('static/<path:path>/', serve, {'document_root': settings.STATIC_ROOT}),
]


# 404 错误页面 （一般是错误的 url 导致的)
handler400 = "operation.views.handler_400_error"
handler403 = "operation.views.handler_403_error"
handler404 = "operation.views.handler_404_error"
handler500 = "operation.views.handler_500_error"
