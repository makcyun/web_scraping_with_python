#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-11-13 10:02:11
# @Author  : suke1900 (johnny824lee@gmail.com)
# @Link    : http://www.makcyun.top
# @Version : $Id$


"""
遍历 stopwords 生成中文词云图

"""

import os
from os import path
import numpy as np
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
from PIL import Image
from matplotlib import pyplot as plt
from scipy.misc import imread
import random
import chardet
import jieba

# 获取当前文件路径
d = path.dirname(__file__) if "__file__" in locals() else os.getcwd()


# 对原文本分词
def cut_words():
    # 获取当前文件路径
    d = path.dirname(__file__) if "__file__" in locals() else os.getcwd()
    text = open(path.join(d, r'langchao.txt'), encoding='UTF-8-SIG').read()
    text = jieba.cut(text, cut_all=False)
    content = ''
    for i in text:
        content += i
        content += " "
    return content

# 加载stopwords
def load_stopwords():
    filepath = path.join(d, r'stopwords_cn.txt')
    stopwords = [line.strip() for line in open(
        filepath, encoding='utf-8').readlines()]
    # print(stopwords) # ok
    return stopwords

# 去除原文stopwords,并生成新的文本
def move_stopwwords(content, stopwords):
    content_after = ''
    for word in content:
        if word not in stopwords:
            if word != '\t'and'\n':
                content_after += word

    content_after = content_after.replace("   ", " ").replace("  ", " ")
    # print(content_after)
    # 写入去停止词后生成的新文本
    with open('langchao.txt', 'w', encoding='UTF-8-SIG') as f:
        f.write(content_after)


def wc_chinese():
    text = open(path.join(d, 'langchao2.txt'), encoding='UTF-8-SIG').read()
    # 设置中文字体
    font_path = 'C:\Windows\Fonts\SourceHanSansCN-Regular.otf'  # 思源黑体
    # 读取背景图片
    background_Image = np.array(Image.open(path.join(d, "wave.png")))
    # 提取背景图片颜色
    img_colors = ImageColorGenerator(background_Image)

    # 设置自定义词典
    jieba.load_userdict("userdict.txt")
    jieba.add_word('英特尔')
    # 设置中文停止词
    stopwords = set('')

    wc = WordCloud(
        font_path=font_path,  # 中文需设置路径
        margin=2,  # 页面边缘
        mask=background_Image,
        scale=2,
        max_words=200,  # 最多词个数
        min_font_size=4,
        stopwords=stopwords,
        random_state=42,
        background_color='white',  # 背景颜色
        # background_color = '#C3481A', # 背景颜色
        max_font_size=100,

    )
    # 生成词云
    wc.generate_from_text(text)
    # 等价于
    # wc.generate(text)

    # 获取文本词排序，可调整 stopwords
    process_word = WordCloud.process_text(wc, text)
    sort = sorted(process_word.items(), key=lambda e: e[1], reverse=True)
    print(sort[:50])  # 获取文本词频最高的前50个词

    # 设置为背景色，若不想要背景图片颜色，就注释掉
    wc.recolor(color_func=img_colors)

    # 存储图像
    wc.to_file('浪潮之巅2.png')

    # 显示图像
    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    content = cut_words()
    stopwords = load_stopwords()
    move_stopwwords(content, stopwords)
    wc_chinese()
