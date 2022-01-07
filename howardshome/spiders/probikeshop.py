# -*- coding: utf-8 -*-

######################### Hi!!! Please check this part ######################################
# I very hope you pay 155 EURO to my PayPal(PP) directly. So we can save fee. Please help me.
# my PayPal id : "shui1319@sina.com"
# Pls don't mention PayPal(PP) on freelancer.com. it is not rule of freelancer.
# If it is impossible, pls pay to freelancer.
# my email: bbanzzakji@gmail.com
# I am looking forward to working with you always :)
#############################################################################


from scrapy import Spider, Request, FormRequest
import sys
import re, os, requests
from collections import OrderedDict
import time
import json, csv
from scrapy.crawler import CrawlerProcess

total_list = []
def writeCsv(items):
    f1 = open("reviews.csv","wb")
    writer = csv.writer(f1, delimiter=',',quoting=csv.QUOTE_ALL)
    writer.writerow(items[0].keys())
    for item in items:
        writer.writerow(item.values())
    f1.close()


class probikeshopSpider(Spider):
    name = "probikeshop"
    start_url = 'https://www.probikeshop.fr/bbb/m/303.html'

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
        urls1 = response.xpath('//ul[@class="subMenuList"]/li/a[not(contains(@class, "has-submenu"))]/@href').extract()
        cat_urls = []
        for url in urls1:
            if 'bbb' in url:
                cat_urls.append(url)

        urls = response.xpath('//li[contains(@class, "off-canvas-submenu")]/ul/li/a/@href').extract()
        for url in urls:
            cat_urls.append(url)

        for cat_url in cat_urls:
            yield Request(response.urljoin(cat_url), self.parse_urls)

    def parse_urls(self, response):
        product_urls = response.xpath('//*[@class="productTop"]//a[@class="product_link"]/@href').extract()
        product_urls1 = response.xpath('//*[@class="productBest"]//a[@class="product_link"]/@href').extract()
        product_urls2 = response.xpath('//*[@class="row listingProduct"]//a[@class="product_link"]/@href').extract()
        urls = []
        for url in product_urls:
            urls.append(url)
        for url in product_urls1:
            urls.append(url)
        for url in product_urls2:
            urls.append(url)

        for url in urls:
            yield Request(response.urljoin(url), callback=self.final_parse)


    def final_parse(self, response):
        productid= response.url.split('/')[-1].replace('.html', '')
        reviews = response.xpath('//*[@class="productPageDetailsBlock_nbComments"]/text()').re(r'[\d.,]+')
        review = 0
        if reviews:
            review = reviews[0]
        url = 'https://api.bazaarvoice.com/data/batch.json?passkey=lmqa9la9apq1i9h1uz1xlzw8e&apiversion=5.5&displaycode=15938-fr_fr&resource.q0=reviews&filter.q0=isratingsonly%3Aeq%3Afalse&filter.q0=productid%3Aeq%3A{}&filter.q0=contentlocale%3Aeq%3Ade_CH%2Cde_DE%2Cen_GB%2Ces_ES%2Cfr_CH%2Cfr_FR%2Cit_CH%2Cit_IT%2Cpt_PT&sort.q0=submissiontime%3Adesc&stats.q0=reviews&filteredstats.q0=reviews&include.q0=authors%2Cproducts%2Ccomments&filter_reviews.q0=contentlocale%3Aeq%3Ade_CH%2Cde_DE%2Cen_GB%2Ces_ES%2Cfr_CH%2Cfr_FR%2Cit_CH%2Cit_IT%2Cpt_PT&filter_reviewcomments.q0=contentlocale%3Aeq%3Ade_CH%2Cde_DE%2Cen_GB%2Ces_ES%2Cfr_CH%2Cfr_FR%2Cit_CH%2Cit_IT%2Cpt_PT&filter_comments.q0=contentlocale%3Aeq%3Ade_CH%2Cde_DE%2Cen_GB%2Ces_ES%2Cfr_CH%2Cfr_FR%2Cit_CH%2Cit_IT%2Cpt_PT&limit.q0={}&offset.q0=0&limit_comments.q0=3'.format(productid, review)
        reviews = response.xpath('//ol[contains(@class, "bv-content-list-Reviews")]/li')

        review_data = requests.get(url).text
        review_json = json.loads(review_data)
        try:
            for review in review_json['BatchedResults']['q0']['Results']:
                item = OrderedDict()
                item['website'] = 'probikeshop.fr'
                item['product_name'] = response.xpath('//*[@class="productPage_top row"]/h1/text()').extract_first()
                item['product_url'] = response.url
                item['review_header'] = review['Title']
                item['review_text'] = review['ReviewText']
                item['review_rating'] = review['Rating']
                total_list.append(item)
                yield item

        except Exception as e:
            print e



def runspider():
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
    })
    process.crawl(probikeshopSpider)
    process.start() #
    writeCsv(total_list)
    return total_list


dd = runspider()
