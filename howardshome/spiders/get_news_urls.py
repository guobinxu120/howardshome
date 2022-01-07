# -*- coding: utf-8 -*-
import sys
import re, os, requests, json
from collections import OrderedDict
import xml.etree.ElementTree as ET
import datetime
from bs4 import BeautifulSoup

def final_parse(response):
    xml_total = ET.fromstring(response)
    total_list = []
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
    return total_list


def get_urls():
    headers = {
                'Cache-Control': 'max-age=0',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'en-US,en;q=0.9',
                'upgrade-insecure-requests': '1',
                'referer': 'https://nmt.howardshome.com/news.aspx'
            }
    username = 'kevin.haver@pon.com'
    password = 'WRvY3zhNyosZ'
    formdata = {}
    formdata['ctl00$ContentPlaceHolder$LoginComponent1$txtUserName']= username
    formdata['ctl00$ContentPlaceHolder$LoginComponent1$txtPassword'] =password
    with requests.Session() as s:
        page = s.get('https://nmt.howardshome.com/Register/Login.aspx?ReturnUrl=%2fnews.aspx')
        soup = BeautifulSoup(page.content)
        formdata["___VIEWSTATE"] = soup.select_one("#__VIEWSTATE")["value"]
        formdata["__VIEWSTATEGENERATOR"] = soup.select_one("#__VIEWSTATEGENERATOR")["value"]
        formdata["__EVENTVALIDATION"] = soup.select_one("#__EVENTVALIDATION")["value"]

        r = s.post('https://nmt.howardshome.com/Register/Login.aspx?ReturnUrl=%2fnews.aspx', data=formdata)
        if r.status_code == 200:
            # page = s.get('https://nmt.howardshome.com/news.aspx')
            current_date = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
            s.headers.update(headers)
            news_data = s.get('https://secure.api.howardshome.com/News/PortalRelated2/112633/0/2018-7-12/{}/0/p1F09kqhJ8HP/3?callback=jQuery1102046063234977811196_1532595509360&_=1532595509361'.format(current_date)).text
            total_list = final_parse(news_data.encode('utf-8'))
            print(total_list)
            return total_list
# get_urls()