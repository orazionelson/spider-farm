# -*- coding: utf-8 -*-
import scrapy, re
from urlparse import urljoin

from mirabile.items import MirabileManuscriptItem

from scrapy.contrib.loader.processor import TakeFirst, Join, MapCompose
from w3lib.html import remove_tags, replace_entities, replace_escape_chars

extract_text = MapCompose(remove_tags, replace_entities, replace_escape_chars)
def name_role_pair(x):
    y = x.split(',')
    return [y[0].strip(), y[1].strip()]

class MirabileManuscriptSpider(scrapy.Spider):
    name = "mirabile-manuscript"
    allowed_domains = ["www.mirabileweb.it"]
    start_urls = (
        'http://www.mirabileweb.it/manuscript/oxford-bodleian-library-tanner-116-(s-c-9942)-manuscript/6743',
    )

    def parse(self, response):
        
        def absolutize_url(rel_url):
            return urljoin(response.url, rel_url)
            
        item = MirabileManuscriptItem()
        item['signature'] = response.selector.xpath('//td[@class="scheda_view"]/p[2]/b/text()').extract()[0]
        text = extract_text(response.selector.xpath('//td[@class="scheda_view"]').extract())[0]
        r = re.compile('Nomi (.*)Bibliografia')
        res = r.search(text)
        item['name_role'] = map(name_role_pair,res.group(1).split(';'))

        title_auth = []
        titles_sel = response.selector.xpath("//a[contains(@href, 'title')]")
        for title in titles_sel:
            auth = title.xpath("following-sibling::a[contains(@href,'author') and position()=1]/text()").extract()
            if auth != []:
                auth = auth[0]
            else:
                auth = u''
            tit = title.xpath("text()").extract()
            if tit != []:
                tit = tit[0]
            else:
                tit = u''
            title_auth.append([tit, auth])
        item['title_author'] = title_auth
        item['titles'] = [] #in the next step we will append to this list informations from the titles found on the current manuscript page

        urls = map(absolutize_url, response.selector.xpath("//a[contains(@href, 'title')]/@href").extract())
        if urls:
            url = urls.pop()
            req = scrapy.Request(url, callback=self.parse_title)
            req.meta['item'] = item
            req.meta['urls'] = urls
            yield req
        else: # there are no titles link with incipit information
            yield item
        
    def parse_title(self, response):
        item = response.meta['item']
        inc_excp = u"//p[starts-with(text(),'inc.')]/text()"
        inc_excp = response.selector.xpath(inc_excp).extract() 
        if inc_excp:
            ie = {}
            ie['incipit'] = inc_excp[0]
            try:
                ie['explicit'] = inc_excp[1]
            except:
                self.log('Incipit/explicit field may be parsed incorrectly.')
            ie['title'] = response.selector.xpath('//td[@class="scheda_view"]/p[2]/b/i/text()').extract()[0]
            item['titles'].append(ie)
            
        urls = response.meta['urls']
        if urls: #there are still some title urls to process for incipit extraction
            url = urls.pop()
            req = scrapy.Request(url, callback=self.parse_title)
            req.meta['item'] = item
            req.meta['urls'] = urls
            yield req
        else:
            yield item