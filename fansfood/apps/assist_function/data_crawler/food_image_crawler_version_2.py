# _*_ coding: utf-8 _*_
__author__ = 'nick'
__date__ = '2019/5/14 17:52'


"""
从图片网站： https://www.pexels.com/ 爬取图片
由于图片是动态加载的，返回的响应是 js 函数，因此通过 re 来匹配图片的 url
然后再使用匹配的 url 来获取图片
"""

import re
import os
import time
import threading
from queue import Queue

from bs4 import BeautifulSoup as bs
import requests
# 图片的标签是繁体汉字，使用一个第三方库来完成繁体转简体
from hanziconv import HanziConv

from .base_dir import base_dir
from .food_rank_crawler import create_random_string
from .get_html_text import get_html_text, create_headers
from ..mongodb.mongo_client import mongo_client


class DataIncomplete(Exception):
    pass


def get_image_url(text):
    """解析网页动态加载的图片 url"""
    low_pattern = re.compile('<a (.*?)>')
    high_pattern = re.compile(r'(/zh-cn/photo/\d*/)')
    all_url = low_pattern.findall(text)[2:-2]
    url_list = []
    for url in all_url:
        try:
            short_url = high_pattern.search(url)
            if short_url:
                long_url = "https://www.pexels.com" + short_url.group(1)
                url_list.append(long_url)
        except Exception as e:
            print("正则表达式匹配出错, 执行下一条匹配...")
            print(f"错误原因: {e}")
            continue
    return url_list


def image_parser(text, refer_page):
    """解析图片网页，并保存到本地和 MongoDB 数据库"""
    soup = bs(text, 'html.parser')

    # 获取图片
    image_url = soup.find(
        'div', class_="photo-page__photo"
    ).find('a', class_="js-photo-page-image-download-link").find(
        'img', class_="js-photo-page-image-img"
    )['data-zoom-src']
    random_id = create_random_string()
    count = 1
    while True:
        try:
            head = create_headers()
            with requests.get(url=image_url, headers=head[0], proxies=head[1], timeout=30, stream=True) as image:
                path = os.path.join(base_dir, "food_image", random_id)
                if not os.path.isdir(path):
                    os.makedirs(path)
                with open(os.path.join(path, f'{random_id}-full.jpg'), 'wb') as f:
                    image_data = b''
                    for chunk in image.iter_content(chunk_size=1024):
                        image_data += chunk
                    # 强制获取完整的数据，如果响应体的内容长度小于头部给定的长度，将会出现错误，重新获取图片
                    if len(image_data) < int(image.headers['content-length']):
                        raise DataIncomplete("图片响应体数据不完整，重新获取...")
                    f.write(image_data)
                    print("响应体数据读取完成...")
            break
        except Exception as e:
            print(e)
            if "404 Client Error" in str(e):
                print("full-image 获取出现 404 错误，执行跳过操作...")
                return
            else:
                print("full-image 获取失败，尝试再次获取")
                time.sleep(0.1)
                count += 1
                if count > 20:
                    print("重试操作20次，执行跳过过操作...")
                    return
                else:
                    continue

    # 获取图片标签
    tags_list = []
    tags = soup.find("div", class_="photo-page__related-tags").find_all('li')
    if tags:
        for tag in tags:
            tags_list.append(HanziConv.toSimplified(tag.a.text))

    data = {
        "random_id": random_id,
        "image_path": os.path.join("food_image", random_id, f'{random_id}-full.jpg'),
        "tags_list": tags_list,
    }

    return data


def run(url, i):
    """给定url, 爬取图片列表页，获取单张图片的地址并爬取"""
    data = []

    print(f"开始爬取第{i}页图片...")
    while True:
        try:
            js_text = get_html_text(url)
        except Exception as e:
            print(e)
            if "404 Client Error" in str(e):
                print("动态的 js 文件获取出现 404 错误，执行跳过操作...")
                return
            else:
                print("动态的 js 文件获取失败，尝试再次获取")
                time.sleep(0.1)
                continue
        else:
            image_url_list = get_image_url(js_text)
            if image_url_list:
                count = 1
                for image_url in image_url_list:
                    while True:
                        try:
                            image_text = get_html_text(image_url)
                        except Exception as e:
                            print(e)
                            if "404 Client Error" in str(e):
                                print(f"第{i}页图片，第{count}张图片爬取失败，失败原因：图片获取出现 404 错误，执行跳过操作......")
                                count += 1
                                break
                            else:
                                print("图片获取失败，尝试再次获取")
                                time.sleep(0.1)
                                continue
                        else:
                            image_data = image_parser(image_text, image_url)
                            if image_data:
                                data.append(image_data)
                                print(f"第{i}页图片，第{count}张图片爬取完成...")
                                count += 1
                                break
                            else:
                                print(f"经过多次尝试，未能成功获取第{i}页图片，第{count}张图片...")
                                count += 1
                                break

            break

    conn = mongo_client()
    for item in data:
        conn.food.food_image.insert_one(item)
    conn.close()
    print(f"第{i}页图片爬取完成...")


class GetImage(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            item = self.queue.get()
            print(item)
            run(item[0], item[1])
            self.queue.task_done()


def main():
    url_queue = Queue()
    for i in range(30, 60):
        url = f"https://www.pexels.com/zh-cn/search/%E9%A3%9F%E7%89%A9/?format=js&seed=2019-05-14%2009%3A28%3A46%20%2B0000&page={i}&type="
        url_queue.put((url, i))
    t1 = GetImage(url_queue)
    t2 = GetImage(url_queue)
    t3 = GetImage(url_queue)
    t4 = GetImage(url_queue)
    t1.start()
    time.sleep(0.2)
    t2.start()
    time.sleep(0.2)
    t3.start()
    time.sleep(0.2)
    t4.start()
    t1.join()
    t2.join()
    t3.join()
    t4.join()


if __name__ == '__main__':
    main()


