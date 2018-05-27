# -*- coding:utf-8 -*-
import sys
import re
import requests
from bs4 import BeautifulSoup
import json
import demjson
import time
from config.news_crawler.souhu_news.souhu_news_conf import sub_site_dict
from model.news_crawler.html2article.html2article import Html2Article
from model.sentiment_calc.dict_based_demo.senti_calc_dict import SentiCalc
reload(sys)
sys.setdefaultencoding('utf-8')


class SouhuNewsExtractor():
    """
    搜狐新闻页解析类,主要是获取标题与链接列表
    """

    @classmethod
    def legal_url(cls, url):
        """
        判断链接地址是否为搜狐新闻站内链接
        :param url:
        :return: 返回对应子站即文章分类,不合法返回None
        """
        for sub_site in sub_site_dict:
            if sub_site in url:
                return sub_site_dict[sub_site]
        return None



    @classmethod
    def extract_link(cls, page_content):
        try:
            link_pattern_1 = re.compile(u'href="(.*?)"')
            link_list_large = []
            link_list_href = re.findall(link_pattern_1, page_content)
            link_list_large.extend(link_list_href)
            article_link = []  # 疑似文章链接
            site_link = []  # 非文章,站内链接
            for link in link_list_large:
                if 'http://' not in link and 'https://' not in link:
                    link = 'http://' + link.strip('/')
                num_star_str = re.sub('\d', '0', link)  # 将数字全部替换为0,用于判断是否包含搜狐特色的编号串
                # print num_star_str
                if cls.legal_url(link):
                    if ('/a/' in link) and ('/000000000_000000' in num_star_str):
                        article_link.append(link.split('?')[0].strip('/'))
                    # 弃掉一种格式的新闻
                    # elif ('html' in link or 'shtml' in link) and ('/00000000/' in num_star_str and '/20' in link):
                    #     article_link.append(link.split('?')[0].strip('/'))
                    else:
                        site_link.append(link.split('?')[0].strip('/'))
            return {"article_link": article_link, "site_link": site_link}
        except Exception, e:
            print e
        return {"article_link": [], "site_link": []}


    @classmethod
    def news_info_by_url(cls, url):
        """
        抽取整理一篇文章的信息,通过他的地址
        :param url:
        :return:
        """
        try:
            res = requests.get(url)
            page_content = res.text
            title_pattern = re.compile(u'<title>(.*?)</title>')
            time_pattern = re.compile(u'(20\d\d-\d\d-\d\d \d\d:\d\d)')
            title = re.findall(title_pattern, page_content)[0].split('_')[0]
            pub_time = re.findall(time_pattern, page_content)[0]
            article_content = Html2Article.url2article(url)
            category = re.findall(title_pattern, page_content)[0].split('_')[1].replace(u'搜狐', '')
            polarity = SentiCalc.score_calc(title)

            news_info = {"title": title, "time": pub_time, 'url': url, "content": article_content, "category": category, "polarity": polarity}
            return news_info
        except Exception, e:
            print e
            return None




# page_content = requests.get('http://news.sohu.com/').content
# print SouhuNewsExtractor.extract_link(page_content)




