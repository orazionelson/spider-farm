# -*- coding: utf-8 -*-
import scrapy
from scrapy.contrib.linkextractors import LinkExtractor

from mirabile.items import MirabileDemoItem


class MirabileDemoSpider(scrapy.Spider):
    name = 'mirabile-demo'
    allowed_domains = ['http://www.mirabileweb.it']
    start_urls = ['http://www.mirabileweb.it/title/acta-capitulorum-generalium-ordinis-praedicatorum--title/18402']
    #start_urls = []


    def get_field(self, field, xpath, sel, item):
        try:
            item[field] = sel.xpath(xpath).extract()[0]
        except:
            self.log("Field %s not parsed correctly."%field)

    def parse(self, response):
        self.log("Our starting URL is %s"%self.start_urls)
        item = MirabileDemoItem()
        sel = response.selector.xpath('//td[@class="scheda_view"]')
        self.get_field('author', './/p/a/b/text()', sel, item)
        self.get_field('title', './/p[2]/b/i/text()', sel, item)
        self.get_field('related_works' , './/p[2]/a/text()', sel, item)
        self.get_field('incipit' , './/p[3]/text()', sel, item)
        self.get_field('explicit' , './/p[3]/text()', sel, item)
        self.get_field('permalink' , './/span[@class="permalink"]/text()', sel, item)
        try:
            item['references'] = sel.xpath('.//p[4]/a/text()').extract()[0] + sel.xpath('.//p[4]/text()').extract()[-1]
        except:
            self.log('Field references is not parsed correctly.')
        try:
            item['shelfmark'] = sel.xpath('./a/text()').extract()[0] + sel.xpath('./text()').extract()[-1] + ' ' + sel.xpath('./i/text()').extract()[-1]
        except:
            self.log('Field shelfmark is not parsed correctly.')
        try:
            item['related_projects'] = sel.xpath('./a/text()').extract()[-1]
        except:
            self.log('Field related_projects is not parsed correctly.')

        #item['html'] = response.body_as_unicode()
        yield item
