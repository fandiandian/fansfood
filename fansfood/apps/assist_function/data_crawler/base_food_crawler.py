# _*_ coding: utf-8 _*_
__author__ = 'nick'
__date__ = '2019/4/26 21:08'


"""
单个美食网页的数据解析
"""


from bs4 import BeautifulSoup
import time
import os
import json
import re
import random

from web_crawler_request.pytmongo_client import mongo_client
from web_crawler_request.get_html_text import get_html_text, HTMLGetError
from base_dir import base_dir


class DataWriteError(Exception):
    pass


class HTMLParserError(Exception):
    pass


class ERROR404(Exception):
    pass


class URLERROR(Exception):
    pass


def html_text_parse(text, random_id, food_id):
    """
    使用 bs4 来解析页面中的数据，获取想要的信息，并返回
    """

    soup = BeautifulSoup(text, "html.parser")

    # 获取食物名称, 图片
    food_info = soup.find('a', class_="J_photo")
    # 获取食物的名称
    title = food_info['title']
    # 获取食物的图片
    image_url = food_info.img['src']
    while True:
        try:
            image = get_html_text(url=image_url, tag=False)
        except Exception as e:
            print(e)
            if "404 Client Error" in str(e):
                print("404 错误，执行调过操作...")
                return
            else:
                print("详情图片获取失败，尝试再次获取")
                time.sleep(0.1)
                continue
        else:
            path = os.path.join(base_dir, "food_article", random_id)
            with open(os.path.join(path, 'full.jpg'), 'wb') as f:
                f.write(image)
            break
    image_path = os.path.join("food_article", random_id, 'full.jpg')
    # 获取描述
    try:
        desc = soup.find('div', id="block_txt1").text
    except:
        desc = ""
    # 获取食材信息  ingredient > 食材
    ingredients = soup.find_all("fieldset", class_="particulars")
    ingredients_list = []
    for ingredient in ingredients:
        name = ingredient.legend.text
        formulas = ingredient.find_all('li')
        ingredient_data = {}
        for formula in formulas:
            formula_name = formula.find('span', class_="category_s1").b.text
            formula_dosage = formula.find('span', class_="category_s2").text
            ingredient_data[formula_name] = formula_dosage
        ingredients_list.append({
            "name": name,
            "formulas": ingredient_data
        })
    # 获取步骤信息
    steps = soup.find('div', class_="recipeStep").find_all('li')
    steps_list = []
    for step in steps:
        step_number = step.find("div", class_="recipeStep_word").div.text
        step_info = step.find("div", class_="recipeStep_word").text
        step_info = step_info.replace(step_number, "")

        try:
            step_image_url = step.find("div", class_="recipeStep_img").img['src']
            if "blank.gif" in step_image_url:
                raise URLERROR
            while True:
                try:
                    image = get_html_text(url=step_image_url, tag=False)
                    step_path = os.path.join(base_dir, "food_article", random_id, 'step')
                    if not os.path.isdir(step_path):
                        os.makedirs(step_path)
                    with open(os.path.join(step_path, f'step_image_{step_number}.jpg'), 'wb') as f:
                        f.write(image)
                    break
                except HTMLGetError as e:
                    if "404 Client Error" in str(e):
                        raise ERROR404("步骤图片出现 404 错误")
                    print(e)
                    print("步骤图片获取失败，尝试再次获取")
                    time.sleep(0.1)
                    continue
            step_image_path = os.path.join("food_article", random_id, 'step', f'step_image_{step_number}.jpg')
        except Exception:
            step_image_path = ""

        step_image_url_info = str(step.find("div", class_="recipeStep_img").img)
        steps_list.append({
            'step_number': step_number,
            "step_info": step_info,
            "step_image_path": step_image_path,
            "step_image_url_info": step_image_url_info
        })

    # 获取小窍门
    tip = soup.find('div', class_='recipeTip')
    if tip:
        tip_info = tip.text
    else:
        tip_info = ""

    # 获取分类
    tags = soup.find_all('div', class_='recipeTip mt16')[-1].find_all('a')
    tags_list = []
    for tag in tags:
        tags_list.append(tag.text)

    # 获取评价，ajax 加载的数据
    ajax_url = "https://home.meishichina.com/ajax/ajax.php?ac=user&op=getrecipeloadinfo&id={}".format(food_id)
    try:
        evaluation = get_html_text(ajax_url)
        evaluation_data = json.loads(evaluation)
        like = evaluation_data["likenum"]
        fav = evaluation_data["ratnum"]
    except:
        print("ajax 数据获取失败，使用随机数据")
        like = random.randint(100, 600)
        fav = random.randint(600, 6000)

    # 数据汇总
    data = {
        "title": title,
        "image_path": image_path,
        "random_id": random_id,
        "desc": desc,
        "ingredients_list": ingredients_list,
        "steps_list": steps_list,
        "tip_info": tip_info,
        "tags_list": tags_list,
        "evaluation": {"like": like, 'fav': fav}
    }

    return data


def run():
    """主函数，进行调用"""

    # 获取 MongoDB 数据库中获取食物链接信息
    url_conn = mongo_client()
    food_data = url_conn.food.food_rank.find({}).batch_size(10)


    # 页面解析错误时，收集错误的 URL 信息
    error_list = []

    print("共计482条网页待获取...")
    all_urls = 482
    count = 1
    for food in food_data:
        url = food["food_detail_url"]
        random_id = food["random_id"]
        pattern = re.compile(r'.*-(\d*)\.html')
        food_id = pattern.search(url).group(1)

        print(f"开始获取第{count}个页面信息")
        print(f'页面 url > {url}')
        while True:
            try:
                text = get_html_text(url)
                time.sleep(0.1)
                data = html_text_parse(text, random_id, food_id)
            except HTMLGetError as e:
                print(e)
                print("尝试再次获取")
                continue
            except Exception as e:
                print(f"页面解析出现错误{e}")
                error_list.append({
                    "url": url,
                    "random_id": random_id,
                    "error_info": str(e)
                })
                count += 1
                break
            else:
                if data:
                    db_client = mongo_client()
                    db_client.food.food_data.insert_one(data)
                    db_client.close()
                    print(f"第{count}个页面信息获取完成..."
                          f"剩余{all_urls - count - len(error_list)}个页面，"
                          f"失败{len(error_list)}个页面")
                    count += 1
                    break
                else:
                    error_info = "页面出现 404 错误"
                    print(error_info)
                    error_list.append({
                        "url": url,
                        "random_id": random_id,
                        "error_info": error_info
                    })
                    count += 1
                    break

    url_conn.close()

    print("页面也全部获取完成...")
    if error_list:
        with open("error.txt", 'w') as f:
            json.dump(error_list, f)


if __name__ == '__main__':
    run()