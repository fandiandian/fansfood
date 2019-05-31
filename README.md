# fansfood
一个美食制作教程和美食图片网站

前端使用：Bootstrap 搭建<br>
后端开发环境：python3.6.2 + django2.2 + xadmin2(xadmin需独立安装）<br>
部署：Nginx + uWSGI<br>
网址：www.ifansfood.cc<br>

## 数据来源
数据获取：使用 requests + bs4 + re<br>
代理ip使用的是阿布云动态版<br><br>
网站数据来源：制作教程（美食天下 <https://www.meishichina.com/>）+ 图片（<https://www.pexels.com/>）<br>
爬虫代码的位置：/apps/assist_function/data_crawler, 文件保存路径相关的需要自己修改<br>
所爬取的数据以上传 onedive，可通过链接：https://1drv.ms/u/s!Aty_si880w59l3oJvMOTb8EcyVlW 下载<br>

## xadmin 的适配 Django2.2 存在一些问题，需要作出一些函数修改
安装：
    pip install https://codeload.github.com/sshwsfc/xadmin/zip/django2 <br>
这个是最快的的，git 的方式安装太慢了<br>
