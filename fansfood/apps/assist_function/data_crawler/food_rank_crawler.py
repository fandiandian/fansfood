# _*_ coding: utf-8 _*_
__author__ = 'nick'
__date__ = '2019/4/27 11:35'


"""
爬取美食天下的食神菜谱排行榜
"""


from bs4 import BeautifulSoup as bs
import random
import time
import os

from web_crawler_request.pytmongo_client import mongo_client
from web_crawler_request.get_html_text import get_html_text, HTMLGetError
from base_dir import base_dir
from web_crawler_request.ip_dynamic import get_ip


# 产生随机字符串
def create_random_string():
    stings = "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890abcdefghijklmnopqrstuvwxyz"
    random_string = "".join(random.sample(stings, 4))
    return f'{int(time.time())}-{random_string}'


def food_rank_parser(text):
    """
    使用 bs4 来解析页面中的数据，获取想要的信息，并返回
    """

    data = []
    soup = bs(text, "html.parser")
    # 获去所有的记录
    ranks = soup.find('div', attrs={'class': "ui_newlist_1 get_num"}).find_all('li')
    for rank in ranks:
        # 获取单条记录的数据
        description = rank.find('div', class_="pic")
        detail = rank.find('div', class_="detail")

        # 食物的随机 id
        random_id = create_random_string()

        # 描述图片链接, 以及图片数据
        if "blank.gif" in description.a.img["src"]:
            image_url = description.a.img["data-src"]
        else:
            image_url = description.a.img["src"]
        try:
            image = get_html_text(url=image_url, tag=False)
            time.sleep(0.1)                                   # 阿布云的代理每秒5次ip请求
        except HTMLGetError as e:
            print(e)
            print("图片获取失败，跳过该条记录")
            continue
        else:
            # 将图片写入本地
            path = os.path.join(base_dir, "food_article", random_id)
            if not os.path.isdir(path):
                os.makedirs(path)
            with open(os.path.join(path, 'sample.jpg'), 'wb') as f:
                f.write(image)

        # 获取食物名称
        name = detail.h2.a.text.strip()
        # 获取食物详情链接
        food_detail_url = detail.h2.a["href"]
        # 获取食物的作者
        author = detail.find('p', class_="subline").a.text
        # 获取食物的配料表
        ingredient_list = detail.find('p', class_="subcontent").text

        # 将数据以字典表的新式保存的列表中
        data.append({
            "name": name,
            "random_id": random_id,
            "image_path": os.path.join("food_article", random_id, 'sample.jpg'),
            "food_detail_url": food_detail_url,
            "author": author,
            "ingredient_list": ingredient_list,
        })

    return data


def run():
    rank_data = []
    for page in range(20, 51):
        print("正在获取第 {} 页数据 .... ".format(page))
        food_rank_url = f"https://home.meishichina.com/show-top-type-recipe-order-chef-page-{page}.html"

        # 前向页面，用于构建请求头部
        if page == 1:
            refer_url = 'https://home.meishichina.com/show-top-type-recipe.html'
        else:
            refer_url = f"https://home.meishichina.com/show-top-type-recipe-order-chef-page-{page - 1}.html"

        text = get_html_text(url=food_rank_url, refer_page=refer_url)
        data = food_rank_parser(text)
        rank_data.extend(data)
        print("第 {} 页数据获取完成！ ".format(page))

    print("数据获取完成, 开始写入数据...")

    client = mongo_client()
    for data in rank_data:
        client.food.food_rank.insert_one(data)
    # 如果需要修改序号，则可以直接调用 insert_many(rank_data)
    # 传入的参数是一个列表，列表中的元素是字典表
    # client.food.food_rank.insert_many(rank_data)

    print("数据写入完成")


if __name__ == '__main__':
    run()
