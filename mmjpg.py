#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys

import requests
from bs4 import BeautifulSoup


class Test:

    def __init__(self):
        self.site_url = 'http://www.mmjpg.com/'
        self.root_folder = '/Users/wangzheng/Downloads/mmJPG/'

        # 指明解码方式
        reload(sys)
        sys.setdefaultencoding('utf-8')

        # 创建根目录
        print('创建根目录 {0}'.format(self.createFolder(self.root_folder)))

    # 获取beautifulSoup实例
    @staticmethod
    def get_beautiful_soup(url):
        r = requests.get(url)
        if r.status_code == 200:
            html = r.content
            # print(html)
            soup = BeautifulSoup(html, 'html.parser')
            # print(soup.prettify)
            return soup

    # 创建文件夹
    def createFolder(self, folder_path):
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            # print('创建文件目录成功 ' + folder_path)
        else:
            # print('文件目录已存在 ' + folder_path)
            pass
        return folder_path

    # 获取二级目录名称
    def get_two_level_directory(self):
        soup = self.get_beautiful_soup(self.site_url)
        item = soup.find_all('div', class_='subnav')[0]
        all_string = item.find('span').string
        # 声明一个数组保存文件目录路径,创建名称为 all_folder 的文件目录
        folders = [all_string]
        hrefs = [self.site_url]

        all_a = item.find_all('a')
        for a in all_a:
            folders.append(a.string)
            hrefs.append(a.get('href'))
        return folders, hrefs

    # 获取三级目录
    def get_three_level_directory(self, url_path):
        soup = self.get_beautiful_soup(url_path)
        items = soup.find_all('div', class_='pic')[0].find('ul').find_all('li')

        # 声明一个数组保存文件目录路径
        folders3 = []
        hrefs3 = []
        for item in items:
            title = item.find('a').find('img').get('alt')
            href_url = item.find('a').get('href')
            folders3.append(title)
            hrefs3.append(href_url)
        return folders3, hrefs3

    # 获取总页码
    def get_page(self, url):
        soup = self.get_beautiful_soup(url)
        a_list = soup.find_all('div', class_='page')[0].find_all('a')
        max_page = 1
        for a in a_list:
            pages = re.findall('\d+', a.string)
            pages = [int(pages) for pages in pages if pages]
            for page in pages:
                max_page = max(max_page, page)
        return max_page

    # 抓取图片地址
    def get_crawl_data(self, url, max_page, folder_path3):
        for i in range(max_page + 1):
            site_url = url + '/' + str(i)
            soup = self.get_beautiful_soup(site_url)
            item = soup.find_all('div', class_='content')[0].find('a').find('img')
            title = item.get('alt')
            pic_url = item.get('src')
            folder_path = folder_path3 + title + '.jpg'
            # print('{0}  {1}'.format(pic_url, folder_path))
            self.download_pic(pic_url, folder_path)

    # 保存图片到本地
    @staticmethod
    def download_pic(pic_url, pic_path):
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
            'Referer': "http://www.mmjpg.com"
        }
        try:
            # 设置绝对路径，文件夹路径 + 图片路径
            if os.path.isfile(pic_path):
                print('该图片已存在  ' + pic_path)
                return
            print('文件路径：' + pic_path + ' 图片地址：' + pic_url)
            try:
                img = requests.get(pic_url, headers=headers, timeout=10)
                with open(pic_path, 'ab') as f:
                    f.write(img.content)
                    print(pic_path)
            except Exception as e:
                print(e)
            print "保存图片完成"
        except Exception, e:
            print e
            print "保存图片失败: " + pic_url


mm = Test()

# 获取二级目录
folder_list, href_list = mm.get_two_level_directory()
for folder, href in zip(folder_list, href_list):
    # 创建二级目录
    folder_path2 = mm.createFolder(mm.root_folder + folder + '/')
    # print('文件目录 {0}  {1}'.format(folder_path2, href))

    # 获取三级目录
    folders3, href3 = mm.get_three_level_directory(href)
    for folder3, href3 in zip(folders3, href3):
        # 创建三级目录
        folder_path3 = mm.createFolder(folder_path2 + folder3 + '/')
        # print('三级目录 {0}  {1}'.format(folder_path3, href3))
        max_page = mm.get_page(href3)
        mm.get_crawl_data(href3, max_page, folder_path3)

print('爬取完成')
