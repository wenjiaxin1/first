# -*- coding: utf-8 -*-
import scrapy
import requests
from lxml import etree
import time
from QSBK.items import QsbkItem
class QsbkSpider(scrapy.Spider):
    name = 'qsbk'
    allowed_domains = ['qsbk.com']
    start_urls = ['https://www.qiushibaike.com/']

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"}
    def parse(self, response):
        # 获取各个频道的链接
        self.keylist = response.xpath("//div[@id='menu']/a/@href").extract()

        # 获取各个频道的标题，链接与标题在各自的列表中的下标一一对应
        self.keylist_zh = response.xpath("//div[@id='menu']/a/text()").extract()
        # 有多少个链接就代表有多少个频道，取出一个频道
        for j in range(0, len(self.keylist)):
            url = 'https://www.qiushibaike.com' + self.keylist[j] + 'page/1'
            #爬取该频道的第一页，主要目的是获取该频道的总页数，并传入该频道在列表中对应的下标
            yield scrapy.Request(url,meta={"key":j},callback=self.channel,dont_filter=True)

    def channel(self,response):

        j = response.meta["key"]
        #获取该频道的总页数
        self.pagenum = response.xpath("//ul[@class='pagination']//span[@class='page-numbers']/text()").extract()[-1].strip()

        for i in range(1,int(self.pagenum)+1):

            url = 'https://www.qiushibaike.com'+self.keylist[j]+'page/'+str(i)

            response = requests.get("http://127.0.0.1:5555/random")
            proxy = {'http':response.text}

            # 获取这页的响应
            response = requests.get(url, headers=self.headers,proxies = proxy)

            html = etree.HTML(response.text)

            try:
                # 获取这页的所有段子
                items = html.xpath("//div[@class='col1']/div")
                # 如果为空，要输入验证码了
                if len(items) == 0:
                    print("*" * 100)
                    print("请去糗事百科输入验证码")
                    print("https://www.qiushibaike.com/")
                    # 等待输入验证码
                    while True:

                        # 输入完验证码后，重新爬取该页的段子
                        url = 'https://www.qiushibaike.com' +self.keylist[j] + 'page/' + str(i)



                        response = requests.get(url, headers=self.headers)

                        html = etree.HTML(response.text)
                        items = html.xpath("//div[@class='col1']/div")
                        if len(items) > 0:
                            for k in range(1, len(items) + 1):
                                item = QsbkItem()
                                item["title"] = self.keylist_zh[j] + ": 第" + str(i) + "页第" + str(k) + "个段子"
                                item["content"] = items[k - 1].xpath(".//div[@class='content']/span/text()")
                                print(item["title"])
                                print(item["content"])
                                yield item
                            time.sleep(1)
                            break
                    continue
                # 遍历每个段子，取出内容
                for k in range(1, len(items) + 1):
                    item = QsbkItem()

                    item["title"] = self.keylist_zh[j] + ": 第" + str(i) + "页第" + str(k) + "个段子"
                    item["content"] = items[k - 1].xpath(".//div[@class='content']/span/text()")
                    print(item["title"])
                    print(item["content"])

                    yield item
                time.sleep(1)
            except:
                print("出现异常！")