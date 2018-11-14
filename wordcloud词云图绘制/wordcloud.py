#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-11-13 10:02:11
# @Author  : suke1900 (johnny824lee@gmail.com)
# @Link    : http://www.makcyun.top
# @Version : $Id$


"""
wordcloud 词云绘制

1 英文词云 text
2 中文词云 text
3 根据词频绘图

"""

import os
from os import path
import numpy as np
from wordcloud import WordCloud,STOPWORDS,ImageColorGenerator
from PIL import Image
from matplotlib import pyplot as plt
from scipy.misc import imread
import random
import chardet
import jieba
import pandas as pd

# 获取当前文件路径
d = path.dirname(__file__) if "__file__" in locals() else os.getcwd()
# 获取文本text
text = open(path.join(d,'legend1900.txt')).read()

def wc_english_basic():
    # 生成词云
    wc = WordCloud(
        scale=2,
        max_font_size = 100,
        # background_color = 'white',
        background_color = '#383838',
        colormap = 'Blues')
    wc.generate_from_text(text)
    # 显示图像
    plt.imshow(wc,interpolation='bilinear')
    plt.axis('off')
    plt.tight_layout()
    #存储图像
    wc.to_file('1900_basic2.png')
    # or
    # plt.savefig('1900_basic2.png',dpi=200)
    plt.show()

def wc_english_improve1():
    # 读取背景图片
    background_Image = np.array(Image.open(path.join(d, "mask1900.jpg")))
    # or
    # background_Image = imread(path.join(d, "mask1900.jpg"))
    # 提取背景图片颜色
    img_colors = ImageColorGenerator(background_Image)
    # 设置英文停止词
    stopwords = set(STOPWORDS)
    stopwords.add('one')
    wc = WordCloud(
        # font_path = font_path,
        margin = 2, # 设置页面边缘
        mask = background_Image,
        scale = 2,
        max_words = 200, # 最多词个数
        min_font_size = 4, # 最小字体大小
        stopwords = stopwords,
        random_state = 42,
        background_color = 'white', # 背景颜色
        max_font_size = 150, # 最大字体大小
        )
    # 生成词云
    wc.generate_from_text(text)
    # 等价于
    # wc.generate(text)

    # # 获取文本词排序，可调整 stopwords
    # process_word = WordCloud.process_text(wc,text)
    # sort = sorted(process_word.items(),key=lambda e:e[1],reverse=True)
    # print(sort[:50]) # 获取文本词频最高的前50个词

    # 根据图片色设置背景色
    wc.recolor(color_func=img_colors)
    #存储图像
    wc.to_file('1900pro.png')
    # 显示图像
    plt.imshow(wc,interpolation='bilinear')
    plt.axis('off')
    plt.tight_layout()
    plt.show()


def wc_english_improve2():
    # 读取背景图片
    background_Image = np.array(Image.open(path.join(d, "mask1900.jpg")))
    img_colors = ImageColorGenerator(background_Image)
    # 设置英文停止词
    stopwords = set(STOPWORDS)
    stopwords.add('one')
    wc = WordCloud(
        margin = 2, # 设置页面边缘
        mask = background_Image,
        scale = 2,
        max_words = 200, # 最多词个数
        min_font_size = 4, # 最小字体大小
        stopwords = stopwords,
        random_state = 42,
        background_color = 'white', # 背景颜色
        max_font_size = 150, # 最大字体大小
        )
    # 生成词云
    wc.generate_from_text(text)
    # 等价于
    # wc.generate(text)

    # or 还可选择设置为渐变灰色
    def grey_color_func(word, font_size, position, orientation, random_state=None,
                    **kwargs):
        return "hsl(0, 0%%, %d%%)" % random.randint(50, 100)

    wc.recolor(color_func=grey_color_func)

    #存储图像
    wc.to_file('1900pro2.png')
    # 显示图像
    plt.imshow(wc,interpolation='bilinear')
    plt.axis('off')
    plt.tight_layout()
    plt.show()



def wc_chinese():
    # 获取文本text,确定编码格式
    # text = open(path.join(d,'langchao.txt'),'rb').read()
    # text_charInfo = chardet.detect(text)
    # print(text_charInfo)

    text = open(path.join(d,'langchao.txt'),encoding='UTF-8-SIG').read()
    text =' '.join(jieba.cut(text,cut_all=False))

    # 设置中文字体
    font_path = 'C:\Windows\Fonts\SourceHanSansCN-Regular.otf'  # 思源黑体
    # 读取背景图片
    background_Image = np.array(Image.open(path.join(d, "wave.png")))
    # 提取背景图片颜色
    img_colors = ImageColorGenerator(background_Image)

    # 设置自定义词典
    jieba.load_userdict("userdict.txt")
    jieba.add_word('英特尔')


    # # 设置中文停止词
    stopwords = set('')
    stopwords.update(['但是','一个','自己','因此','没有','很多','可以','这个','虽然','因为','这样','已经','现在','一些','比如','不是','当然','可能','如果','就是','同时','比如','这些','必须','由于','而且','并且','他们'])

    wc = WordCloud(
        font_path = font_path, # 中文需设置路径
        margin = 2, # 页面边缘
        mask = background_Image,
        scale = 2,
        max_words = 200, # 最多词个数
        min_font_size = 4, #
        stopwords = stopwords,
        random_state = 42,
        background_color = 'white', # 背景颜色
        max_font_size = 100,

        )
    # 生成词云
    # wc.generate_from_text(text)
    # 等价于
    wc.generate(text)

    # # 获取文本词排序，可调整 stopwords
    # process_word = WordCloud.process_text(wc,text)
    # sort = sorted(process_word.items(),key=lambda e:e[1],reverse=True)
    # print(sort[:50]) # 获取文本词频最高的前50个词

    # 设置为背景色，若不想要背景图片颜色，就注释掉
    wc.recolor(color_func=img_colors)

    #存储图像
    # wc.to_file('浪潮之巅basic3.png')
    # or
    # plt.savefig('1900.png',dpi=200)

    # 显示图像
    plt.imshow(wc,interpolation='bilinear')
    plt.axis('off')
    plt.tight_layout()
    plt.show()

def wc_dataframe():
    df = pd.read_csv('university.csv',encoding = 'utf-8')
    df = df.groupby(by = 'country').count()
    df = df['world_rank'].sort_values(ascending = False)
    # df = dict(df) # 可选
    font_path='C:\Windows\Fonts\SourceHanSansCN-Regular.otf'  # 思源黑，黑体simhei.ttf

    wordcloud = WordCloud(
        background_color = '#F3F3F3',
        font_path = font_path,
        width = 500,height = 300,
        margin = 2,
        max_font_size = 200,
        random_state = 42,
        scale = 2,
        colormap = 'viridis',
    )

    wordcloud.generate_from_frequencies(df)
    # or
    # wordcloud.fit_words(df)
    # # 保存
    wordcloud.to_file('university.png')
    plt.imshow(wordcloud,interpolation = 'bilinear')
    plt.axis('off')
    plt.show()



if __name__ == '__main__':
    # wc_english_basic()
    # wc_english_improve()
    # wc_chinese()
    wc_dataframe()