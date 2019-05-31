# _*_ coding: utf-8 _*_
__author__ = 'nick'
__date__ = '2019/5/1 23:32'


from PIL import Image, ImageDraw, ImageFont, ImageColor
import os, re
from django_food.settings import BASE_DIR
import random

# 生成图片验证码，产生sql文件，执行数据插入，简单的数学加法验证图片
def create_image_recode(number_a, number_b):
    """
    这段代码是搬运自 https://blog.csdn.net/jinixin/article/details/79248842
    目前没有接触过 pillow 库，自能先借用一下
    """

    font_color = '#FFFFFF'

    image = Image.new(mode='RGBA', size=(52, 27))  # RGBA模式下没有color参数便是透明图片
    draw_table = ImageDraw.Draw(im=image)
    text = "{} + {}".format(number_a, number_b)
    draw_table.text(xy=(0, 0), text=text, fill=font_color, font=ImageFont.truetype('./msyh.ttc', 20))

    f_color_channel = ImageColor.getrgb(font_color)
    r, g, b, a = image.split()  # 将图像分成三个单通道图像

    r = r.point(lambda x: f_color_channel[0])  # 迭代处理R通道图像的所有像素，将它们设成字体颜色的R值
    g = g.point(lambda x: f_color_channel[1])
    b = b.point(lambda x: f_color_channel[2])

    image = Image.merge('RGBA', (r, g, b, a))  # 合并多个通道图像成一个新图像

    # 生成 SQL 语句
    # 生成随机图片名称
    name_str = 'ABCDEFGHIJKLMNOPQRETUVWXYZabcedfghijklmnopqrstuvwxyz0123456789_-'
    name = "".join(random.sample(name_str, 10))
    sql_info = "INSERT INTO recode_image VALUES " \
               "(<>, '{name}', {a}, {b}, 'recode_image/{name}.png'," \
               " '2019-05-01 16:58:14.840294');\n".format(name=name, a=number_a, b=number_b)

    path = os.path.join(BASE_DIR, "media", "recode_image", "{}.png".format(name))
    image.save(path)
    image.close()

    return sql_info


if __name__ == '__main__':
    pattern = re.compile('<>')
    path_list = []
    for i in range(1, 10):
        for j in range(1, 10):
            path = create_image_recode(i, j)
            path_list.append(path)

    with open("recode_image.txt", "w") as f:
        count = 1
        for item in path_list:
            f.write(pattern.sub(str(count), item))
            count += 1