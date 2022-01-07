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
    f1 = open("gebiz.csv","wb")
    writer = csv.writer(f1, delimiter=',',quoting=csv.QUOTE_ALL)
    writer.writerow(items[0].keys())
    for item in items:
        writer.writerow(item.values())
    f1.close()


class gebizSpider(Spider):
    name = "gebiz"
    start_url = 'https://www.gebiz.gov.sg/ptn/opportunity/BOListing.xhtml?origin=search'

    use_selenium = False
    count = 0
    pageIndex = 1
    reload(sys)
    sys.setdefaultencoding('utf-8')
    total_page = None
    headers = {
            'Cookie': '',
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
        }
    # custom_settings = {
	#     # 'CRAWLERA_ENABLED' : False,
     #    'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
     #    'CONCURRENT_REQUESTS': 1,
     #    'DOWNLOAD_DELAY': 3.5,
     #    'COOKIES_ENABLED' : 'False'
	# }
    def start_requests(self):
        yield Request(self.start_url, callback= self.parse, dont_filter=True, meta={'page':1, 'index': 1, 'start_page':1})
    def parse(self, response):
        tables = response.xpath('//table[@class="formColumns_ROW-TABLE"]')
        print "table count:{}".format(len(tables))
        url = 'https://www.gebiz.gov.sg/ptn/opportunity/BOListing.xhtml'
        viewstate = response.xpath('//input[@name="javax.faces.ViewState"]/@value').extract_first()
        cookies = response.headers.getlist('Set-Cookie')
        str_cookie = ''
        for cook in cookies:
            str_cookie = str_cookie + cook.split(';')[0] +'; '
        if str_cookie != '':
            self.headers['Cookie'] = str_cookie

        if not viewstate:
            viewstate = response.split('id="javax.faces.ViewState"><![CDATA[')[-1].split(']]>')[0]

        print viewstate
        k1 = response.xpath('//div[@id="listButton2_MAIN-DIV"]/input/@name').extract_first()
        k2 = response.xpath('//div[@class="form2_ROW-COMPONENT"]/input[2]/@name').extract_first()
        k3 = response.xpath('//input[contains(@name, "searchBarList_HIDDEN-SUBMITTED-VALUE")]/@name').extract_first()
        k4 = response.xpath('//select[contains(@class, "formSelectOneMenu_SELECTION")]/@name').extract_first()
        k5 = response.xpath('//select[contains(@title, "Published Date")]/@name').extract_first()

        index = response.meta['index']
        if response.meta['start_page'] ==1 :
            for i, table in enumerate(tables):
                if i == index:
                    # time.sleep(1)
                    id = table.xpath('.//input[contains(@name, "commandLink-HIDDEN-BUTTON")]/@name').extract_first()
                    # print id
                    formdata = {
                            'contentForm': 'contentForm',
                            k1:'',
                            k2: '',
                            k3:'',
                            k4: 'ON',
                            k5: '0',
                            'javax.faces.ViewState': viewstate,
                            'javax.faces.source': id,
                            'javax.faces.partial.event': 'click',
                            'javax.faces.partial.execute': '{} contentForm dialogForm'.format(id),
                            'javax.faces.behavior.event': 'action',
                            'javax.faces.partial.ajax': 'true'
                        }

                    yield FormRequest(url, self.final_parse, formdata=formdata, dont_filter=True, meta={'page':response.meta['page'], 'index': index, 'start_page':response.meta['start_page']}, headers=self.headers)
                        # break
                # break


        page = response.meta['page'] + 1
        if len(tables) < 2 and index < 11 and page < self.total_page:
            yield Request(self.start_url, callback= self.parse, dont_filter=True, meta={'page':1, 'index': 1, 'start_page':page-1})

        if page == 2 and not self.total_page:
            total = response.xpath('//input[@class="formTabBar_TAB-BUTTON-ACTIVE"]/@value').re(r'[\d.]+')
            if total:
                self.total_page = int(total[0])/10 + 1
        if index ==11:
            print page
            next_tag = response.xpath('//input[contains(@value, "Next")]')
            if next_tag:
                page = response.meta['page'] + 1
                next_id = next_tag.xpath('./@id').extract_first()
                click_str = next_tag.xpath('./@onclick').extract_first()
                vals = click_str.split("action\\',")[-1].split("',{")[0].replace('\\', '').replace("'", '').split(',')
                if len(vals) > 1:
                    formdata = {
                        'contentForm': 'contentForm',
                        k1:'',
                        k2: '',
                        k3:'',
                        k4: 'ON',
                        k5: '0',
                        'javax.faces.ViewState': viewstate,
                        'javax.faces.source': next_id,
                        'javax.faces.partial.event': 'click',
                        'javax.faces.partial.execute': '{} {}'.format(next_id, vals[0]),
                        'javax.faces.partial.render': vals[1],
                        'javax.faces.behavior.event': 'action',
                        'javax.faces.partial.ajax': 'true'
                    }
                    url = 'https://www.gebiz.gov.sg/ptn/opportunity/BOListing.xhtml'
                    header1 = {}
                    # for key in self.headers.keys():
                    #     header1[key] = self.headers[key]
                    # header1['Faces-Request'] = 'partial/ajax'
                    header1['Host'] = 'www.gebiz.gov.sg'
                    header1['Origin'] = 'https://www.gebiz.gov.sg'
                    header1['Referer'] = 'https://www.gebiz.gov.sg/ptn/opportunity/BOListing.xhtml'
                    header1['Content-type'] = 'application/x-www-form-urlencoded;charset=UTF-8'
                    header1['Accept'] = '*/*'
                    header1['Cookie'] = self.headers['Cookie']
                    header1['User-Agent'] = self.headers['User-Agent']
                    # header1['Content-Length'] = '647'
                    yield FormRequest(url, self.parse, formdata=formdata, meta={'page':page, 'index': 1, 'start_page': response.meta['start_page']}, dont_filter=True, headers=header1)
                elif page < self.total_page:
                    page = response.meta['page'] + 1
                    vals = next_id.split(':')
                    val1= vals[0]+':'+vals[1]
                    val2= next_id.split('_Next')[0]

                    formdata = {
                        'contentForm': 'contentForm',
                        k1:'',
                        k2: '',
                        k3:'',
                        k4: 'ON',
                        k5: '0',
                        'javax.faces.ViewState': viewstate,
                        'javax.faces.source': next_id,
                        'javax.faces.partial.event': 'click',
                        'javax.faces.partial.execute': '{} {}'.format(next_id, val1),
                        'javax.faces.partial.render': '{} contentForm dialogForm'.format(val2),
                        'javax.faces.behavior.event': 'action',
                        'javax.faces.partial.ajax': 'true'
                    }
                    url = 'https://www.gebiz.gov.sg/ptn/opportunity/BOListing.xhtml'
                    header1 = {}
                    for key in self.headers.keys():
                        header1[key] = self.headers[key]
                    header1['Host'] = 'www.gebiz.gov.sg'
                    header1['Origin'] = 'https://www.gebiz.gov.sg'
                    header1['Referer'] = 'https://www.gebiz.gov.sg/ptn/opportunity/BOListing.xhtml'
                    header1['Content-Type'] = 'application/x-www-form-urlencoded;charset=UTF-8'
                    header1['Accept'] = '*/*'
                    yield FormRequest(url, self.parse, formdata=formdata, meta={'page':page, 'index': 1, 'start_page':response.meta['start_page']}, dont_filter=True, headers=header1)

        if response.meta['start_page'] > 1:
            start_page = response.meta['start_page']
            next_tag = response.xpath('//input[contains(@value, "Next")]')
            if next_tag:
                page = response.meta['page'] + 1
                next_id = next_tag.xpath('./@id').extract_first()
                click_str = next_tag.xpath('./@onclick').extract_first()
                vals = click_str.split("action\\',")[-1].split("',{")[0].replace('\\', '').replace("'", '').split(',')
                if len(vals) > 1:
                    formdata = {
                        'contentForm': 'contentForm',
                        k1:'',
                        k2: '',
                        k3:'',
                        k4: 'ON',
                        k5: '0',
                        'javax.faces.ViewState': viewstate,
                        'javax.faces.source': next_id,
                        'javax.faces.partial.event': 'click',
                        'javax.faces.partial.execute': '{} {}'.format(next_id, vals[0]),
                        'javax.faces.partial.render': vals[1],
                        'javax.faces.behavior.event': 'action',
                        'javax.faces.partial.ajax': 'true'
                    }
                    url = 'https://www.gebiz.gov.sg/ptn/opportunity/BOListing.xhtml'
                    header1 = {}
                    # for key in self.headers.keys():
                    #     header1[key] = self.headers[key]
                    # header1['Faces-Request'] = 'partial/ajax'
                    header1['Host'] = 'www.gebiz.gov.sg'
                    header1['Origin'] = 'https://www.gebiz.gov.sg'
                    header1['Referer'] = 'https://www.gebiz.gov.sg/ptn/opportunity/BOListing.xhtml'
                    header1['Content-type'] = 'application/x-www-form-urlencoded;charset=UTF-8'
                    header1['Accept'] = '*/*'
                    header1['Cookie'] = self.headers['Cookie']
                    header1['User-Agent'] = self.headers['User-Agent']
                    # header1['Content-Length'] = '647'
                    if start_page ==page:
                        yield FormRequest(url, self.parse, formdata=formdata, meta={'page':page, 'index': 1, 'start_page':1}, dont_filter=True, headers=header1)
                    else:
                        yield FormRequest(url, self.parse, formdata=formdata, meta={'page':page, 'index': 1, 'start_page':start_page}, dont_filter=True, headers=header1)

                elif page < self.total_page:
                    page = response.meta['page'] + 1
                    vals = next_id.split(':')
                    val1= vals[0]+':'+vals[1]
                    val2= next_id.split('_Next')[0]

                    formdata = {
                        'contentForm': 'contentForm',
                        k1:'',
                        k2: '',
                        k3:'',
                        k4: 'ON',
                        k5: '0',
                        'javax.faces.ViewState': viewstate,
                        'javax.faces.source': next_id,
                        'javax.faces.partial.event': 'click',
                        'javax.faces.partial.execute': '{} {}'.format(next_id, val1),
                        'javax.faces.partial.render': '{} contentForm dialogForm'.format(val2),
                        'javax.faces.behavior.event': 'action',
                        'javax.faces.partial.ajax': 'true'
                    }
                    url = 'https://www.gebiz.gov.sg/ptn/opportunity/BOListing.xhtml'
                    header1 = {}
                    for key in self.headers.keys():
                        header1[key] = self.headers[key]
                    header1['Host'] = 'www.gebiz.gov.sg'
                    header1['Origin'] = 'https://www.gebiz.gov.sg'
                    header1['Referer'] = 'https://www.gebiz.gov.sg/ptn/opportunity/BOListing.xhtml'
                    header1['Content-Type'] = 'application/x-www-form-urlencoded;charset=UTF-8'
                    header1['Accept'] = '*/*'
                    if start_page ==page:
                        yield FormRequest(url, self.parse, formdata=formdata, meta={'page':page, 'index': 1, 'start_page':1}, dont_filter=True, headers=header1)
                    else:
                        yield FormRequest(url, self.parse, formdata=formdata, meta={'page':page, 'index': 1, 'start_page':start_page}, dont_filter=True, headers=header1)




    def final_parse(self, response):
        item= OrderedDict()
        item['id'] = ''
        item['title'] = response.xpath('//div[@class="formOutputText_HIDDEN-LABEL outputText_TITLE-BLACK"]/text()').extract_first()
        if item['title']:
            self.count += 1
            item['id'] = self.count

        item['description'] = response.xpath('//div[contains(text(), "The information contained")]/text()').extract_first()
        item['Quotation No.'] = response.xpath('//span[contains(text(), "Tender No")]/parent::div/parent::div/parent::td/following-sibling::td/div/text()').extract_first()
        if not item['Quotation No.']:
            item['Quotation No.'] = response.xpath('//span[contains(text(), "Quotation No")]/parent::div/parent::div/parent::td/following-sibling::td/div/text()').extract_first()
        # print("item: " +item['Quotation No.'])
        item['Reference No.'] = response.xpath('//span[contains(text(), "Reference No")]/parent::div/parent::div/parent::td/following-sibling::td/div/text()').extract_first()
        item['Agency'] = response.xpath('//span[contains(text(), "Agency")]/parent::div/parent::div/parent::td/following-sibling::td/div/text()').extract_first()
        item['Published'] = response.xpath('//span[contains(text(), "Published")]/parent::div/parent::div/parent::td/following-sibling::td/div/text()').extract_first()
        item['Offer Validity Duration'] = response.xpath('//span[contains(text(), "Offer Validity Duration")]/parent::div/parent::div/parent::td/following-sibling::td/div/text()').extract_first()
        item['Remarks'] = response.xpath('//span[contains(text(), "Remarks")]/parent::div/parent::div/parent::td/following-sibling::td/div/text()').extract_first()
        item['Procurement Type'] = response.xpath('//span[contains(text(), "Procurement Type")]/parent::div/parent::div/parent::td/following-sibling::td/div/text()').extract_first()
        # item['Two Envelope Bidding'] = response.xpath('//span[contains(text(), "Two Envelope Bidding")]/parent::div/parent::div/parent::td/following-sibling::td/div/text()').extract_first()
        item['Quotation Type'] = response.xpath('//span[contains(text(), "Tender Type")]/parent::div/parent::div/parent::td/following-sibling::td/div/text()').extract_first()
        if not item['Quotation Type']:
            item['Quotation Type'] = response.xpath('//span[contains(text(), "Quotation Type")]/parent::div/parent::div/parent::td/following-sibling::td/div/text()').extract_first()

        item['Procurement Nature'] = response.xpath('//span[contains(text(), "Procurement Nature")]/parent::div/parent::div/parent::td/following-sibling::td/div/text()').extract_first()
        item['Procurement Method'] = response.xpath('//span[contains(text(), "Procurement Method")]/parent::div/parent::div/parent::td/following-sibling::td/div/text()').extract_first()
        item['Quotation Box No.'] = response.xpath('//span[contains(text(), "Quotation Box No")]/parent::div/parent::div/parent::td/following-sibling::td/div/text()').extract_first()
        item['Procurement Category'] = response.xpath('//span[contains(text(), "Procurement Category")]/parent::div/parent::div/parent::td/following-sibling::td/div/text()').extract_first()
        try:
            item['Closing on'] = ' '.join(response.xpath('//tr[@class="shaded_BLUE"]')[1].xpath('.//div[@class="formOutputText_HIDDEN-LABEL outputText_NAME-BLACK"]/text()').extract())
        except:
            item['Closing on'] = ''
        briefing_date = response.xpath('//span[contains(text(), "Briefing Date")]/parent::div/parent::div/parent::td/following-sibling::td/div/text()').extract_first()
        if briefing_date:
            briefing_time = response.xpath('//span[contains(text(), "Briefing Time")]/parent::div/parent::div/parent::td/following-sibling::td/div/text()').extract_first()
            item['site briefing'] = briefing_date + ' ' + briefing_time
        else:
            item['site briefing'] = ''
        total_list.append(item)
        print(self.count)
        yield item

        formdata = {}
        formdata['contentForm'] = 'contentForm'
        k1 = response.xpath('//div[@id="listButton2_MAIN-DIV"]/input/@name').extract_first()
        formdata[k1] =''
        k2 = response.xpath('//input[@value="Back to Search Results"]/@name').extract_first()
        formdata[k2]= 'Back to Search Results'
        # keys = response.xpath('//input[contains(@name, "datatableNameLocation_inputHidden")]/@name').extract()
        # for key in keys:
        #     formdata[key] = ''
        # key3 = response.xpath('//select[contains(@name, "formRepeatPagination-SELECTONEMENU_select")]/@name').extract_first()
        # val = response.xpath('//select[contains(@name, "formRepeatPagination-SELECTONEMENU_select")]/option[@selected="selected"]/@value').extract_first()
        # if key3:
        #     formdata[key3] = val
        #
        # key4 = response.xpath('//input[contains(@name, "formRepeatPagination_GOTO-PAGE-INPUTTEXT")]/@name').extract_first()
        # val = response.xpath('//input[contains(@name, "formRepeatPagination_GOTO-PAGE-INPUTTEXT")]/@value').extract_first()
        # if key4:
        #     formdata[key4] = val
        #
        # key5 = response.xpath('//input[contains(@name, "formRepeatPagination_HIDDEN-INPUT")]/@name').extract_first()
        # val = response.xpath('//input[contains(@name, "formRepeatPagination_HIDDEN-INPUT")]/@value').extract_first()
        # if key5:
        #     formdata[key5] = val
        #
        viewstate = response.xpath('//input[@name="javax.faces.ViewState"]/@value').extract_first()
        if not viewstate:
            viewstate = response.split('id="javax.faces.ViewState"><![CDATA[')[-1].split(']]>')[0]
        formdata['javax.faces.ViewState'] = viewstate
        response.meta['index'] = response.meta['index'] + 1
        # time.sleep(1)
        # cookies = response.headers.getlist('Set-Cookie')
        # str_cookie = ''
        # for cook in cookies:
        #     str_cookie = str_cookie + cook.split(';')[0] +';'
        headers = {
            'Cookie': self.headers['Cookie'],
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
            'Host': 'www.gebiz.gov.sg',
            'Origin': 'https://www.gebiz.gov.sg',
            'Referer': 'https://www.gebiz.gov.sg/ptn/opportunity/opportunityDetails.xhtml',
            'Upgrade-Insecure-Requests': '1'
        }
        yield FormRequest(response.url, self.parse, formdata=formdata, meta=response.meta, dont_filter=True, headers=self.headers)



def runspider():
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1',
        'CONCURRENT_REQUESTS': 1,
        # 'DOWNLOAD_DELAY': 2,
        # 'COOKIES_ENABLED': False
    })

    process.crawl(gebizSpider)
    process.start() #
    writeCsv(total_list)
    return total_list

dd = runspider()
