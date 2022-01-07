# -*- coding: utf-8 -*-
from scrapy import Spider, Request, FormRequest, signals
from urlparse import urlparse
import sys
import re, os, requests, urllib
from collections import OrderedDict
import time
import json, re, csv
import xml.etree.ElementTree as ET
from scrapy.crawler import CrawlerProcess, Crawler
import multiprocessing as mp
from scrapy.settings import Settings
import datetime

total_list = []
class TradecarviewSpider(Spider):
    name = "howardshome1"
    start_url = 'https://nmt.howardshome.com/news.aspx'

    use_selenium = False
    count = 0
    pageIndex = 1
    reload(sys)
    sys.setdefaultencoding('utf-8')

   # //////// angel headers and cookies////////////
    headers = {
                'Cache-Control': 'max-age=0',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'en-US,en;q=0.9',
                'upgrade-insecure-requests': '1',
                'referer': 'https://www.tradecarview.com/my/favoritelist.aspx?list=1&sort=0&ps=25&&pn=0'
            }

    def start_requests(self):
        yield Request(self.start_url, callback= self.parse, dont_filter=True)
    def parse(self, response):

        username = 'kevin.haver@pon.com'
        password = 'WRvY3zhNyosZ'

        return FormRequest.from_response(response=response,
                                            formdata={'ctl00$ContentPlaceHolder$LoginComponent1$txtUserName': username, 'ctl00$ContentPlaceHolder$LoginComponent1$txtPassword': password},
                                            clickdata={'id': 'ctl00_ContentPlaceHolder_LoginComponent1_btnSubmit'},
                                            callback=self.parse_urls, dont_filter=True)

    def parse_urls(self, response):
        current_date = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        yield Request('https://secure.api.howardshome.com/News/PortalRelated2/112633/0/2018-7-11/{}/0/p1F09kqhJ8HP/3'.format(current_date), callback=self.final_parse)


    def final_parse(self, response):
        # list = response.xpath('//NewsId/text()').extract()
        xml_total = ET.fromstring(response.body)

        for news_item in xml_total:
            item = OrderedDict()
            item['news_id'] = ''
            item['title'] = ''
            item['news_url'] = ''
            item['summary'] = ''
            for child in news_item:
                if "NewsUrl" in child.tag:
                    item['news_url'] = child.text
                if "Title" in child.tag :
                    item['title'] = child.text
                if "NewsId" in child.tag :
                    item['news_id'] = child.text
                if "Summary" in child.tag :
                    item['summary'] = child.text
            total_list.append(item)
            yield item


class CustomCrawler(object):

    def crawl(self, spider):
        crawled_items = []

        def add_item(item):
            crawled_items.append(item)

        process = CrawlerProcess(
            # {
            #     'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
            # }
        )

        crawler = Crawler(spider)
        crawler.signals.connect(add_item, signals.item_scraped)
        process.crawl(crawler)

        process.start()

        return crawled_items
def _crawl(queue):
    crawler = CustomCrawler()
    # Assume we have a spider class called: WebSpider
    res = crawler.crawl(TradecarviewSpider)
    queue.put(res)

def crawl():


    q = mp.Queue()
    p = mp.Process(target=_crawl, args=(q,))
    p.start()
    res = q.get()
    p.join()

    return res

def get_urls():
    # process = CrawlerProcess({
    #     'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
    # })
    #
    # process.crawl(TradecarviewSpider)
    # process.start() #

    total_list = crawl()
    return total_list