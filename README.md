# fansfood
一个美食制作教程和美食图片网站

前端使用：Bootstrap 搭建<br>
后端开发环境：python3.6.2 + django2.2 + xadmin2(xadmin需独立安装）<br>
部署：Nginx + uWSGI<br>
网址：www.ifansfood.cc<br>

## 网站页面展示
登录页面<br>
![login](https://www.ifansfood.cc/media/temp/login.png)
首页<br>
![login](https://www.ifansfood.cc/media/temp/homepage.png)
用户中心<br>
![login](https://www.ifansfood.cc/media/temp/user_center.png)

## 数据来源
数据获取：使用 requests + bs4 + re<br>
代理ip使用的是阿布云动态版<br>
网站数据来源：制作教程（美食天下 <https://www.meishichina.com/>）+ 图片（<https://www.pexels.com/>）<br>
爬虫代码的位置：/apps/assist_function/data_crawler, 文件保存路径相关的需要自己修改<br>
爬取的数据是直接存储在 MongoDB 中，根据模型的设计，再进行分割转储到 MySQL 中<br>
由于数据分为图片和其他一些文字信息，太大所以未上传至github，如果需要可以联系我，我将图片和mysql的文件发给你
我的邮箱：yzliuyongfu@vip.qq.com

## xadmin 的适配 Django2.2 存在一些问题，需要作出一些函数修改
安装：这个是最快的，git 的方式安装太慢了<br>
    
    pip install https://codeload.github.com/sshwsfc/xadmin/zip/django2
    
适配性修改：参见 https://github.com/vip68/xadmin_bugfix  
我修改的地方主要是出现下面这种错误的地方：
    
    TypeError at /xadmin/xadmin/userwidget/add/ render() got an unexpected keyword argument 'renderer'  
    
参考 https://github.com/vip68/xadmin_bugfix/commit/344487d80e6ff830f39b3526ee024231921c074d 可以解决这个问题  

我每个xadmin模块都点开看了一下，保险起见把所有的 `render` 函数都增加一个`renderer=None` ，没有发送发生过这个bug<br>
如果集成了ueditor富文本编辑器也会报这个错误，原因是同样的
    
    找到UEditor/widgets.py，167行
    --- def render(self, name, value, attrs=None):
    +++ def render(self, name, value, attrs=None, renderer=None):
    参考：https://github.com/sshwsfc/xadmin/issues/621
    
还有一个就是后台自定义图标的修改：
    
    原来是用的font-awwsome的版本太低，改成4.7版的
    将目录中的 font-awesome-4.7.0 下的两个文件夹覆盖 
        venv/Lib/site-packages/xadmin/static/xadmin/vendor/font-awesome 下的目录即可
    然后根据自己的喜欢上 https://fontawesome.com/v4.7.0/icons/ 选择食用
    
## 翻页插件的修改
使用的是django第三方插件 pure-pagination
    
    项目主页：https://github.com/jamespacileo/django-pure-pagination
    
由于我的用户中心展示收藏的时候有两个页面分页，所以需要对页面分页的对应的键进行区分，修改如下：
    
    19行 
    --- def __init__(self, object_list, per_page, orphans=0, allow_empty_first_page=True, request=None):
    +++ def __init__(self, object_list, per_page, orphans=0, allow_empty_first_page=True, request=None, page_type='page'):
    26行
    +++ self.page_type = page_type
    206行 
    --- self.base_queryset['page'] = page_number
    +++ self.base_queryset[self.page_type] = page_number
    210行
    --- return 'page=%s' % page_number
    +++ return '{}={}'.format(self.page_type, page_number)
    
这样，在分页对象示例化的时候，通过设定`page_type`参数就可以区分不同的分页对象了

## mysql 字符编码的问题
如果是用通过`navicat`来创建数据库的化，一定要统一使用`utf8mb4`编码，默认的`utf`有些字符无法识别（比如`emoji图标`），导致字符编码错误<br>
部署的时候，在数据库数据转移才暴露出来，因为这个编码的问题，浪费了半天的时间
    
    
    
