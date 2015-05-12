# -*- coding: utf-8 -*-
import scrapy

import re
from urlparse import urljoin
from scrapy.contrib.loader import ItemLoader
from scrapy.contrib.loader.processor import MapCompose
from jonas.items import JonasManuscriptItem, extract_text

class JonasManuscriptSpider(scrapy.Spider):
    name = "jonas-manuscript"
    allowed_domains = ["jonas.irht.cnrs.fr"]
    start_urls = (
        'http://jonas.irht.cnrs.fr/manuscrit/75191',
    )

    def parse(self, response):
        self.log("Our starting URL is %s"%self.start_urls)

        def absolutize_url(rel_url):
            return urljoin(response.url, rel_url)
            
        l = ItemLoader(item=JonasManuscriptItem(), response=response)
        
        l.add_xpath('signature', '/html/body/div[1]/div[3]/fieldset[1]/a[2]/p/span/text()')
        l.add_xpath('permalink', '/html/body/div[1]/div[3]/fieldset[2]/p/a/text()')

        l.add_xpath('main_dating', '/html/body/div[1]/div[3]/div[2]/div[2]/table[1]/tr[4]/td[2]/text()')
        l.add_xpath('language', '/html/body/div[1]/div[3]/div[2]/div[2]/table[1]/tr[5]/td[2]/text()')
        l.add_xpath('input_status', '/html/body/div[1]/div[3]/div[2]/div[2]/table[1]/tr[7]/td[2]/text()')
        
        r = re.compile(u'(\d*) œuvre\(s\) :')
        number_text = response.xpath('//div[@class="titre_contenu_bloc"]/text()').extract()[0]
        res = r.search(number_text)
        if res:
            number = res.group(1)
        else:
            number = u''
        l.add_value('number', number)
        
        l.add_xpath('author', '//span[@class="auteur"]/text()')
        l.add_xpath('title', '//span[@class="titre"]/text()')
        l.add_xpath('incipit', '//span[@class="incipit"]/text()')
        #'foliation' # no foliation on the testpage
        
        l.add_xpath('state_of_witness', '//div[@class="contenu_temoin"]/table/tr[1]/td[2]/text()')
        r = re.compile(u'(.*) (?:\((.*)\))')
        com_text = response.xpath('//div[@class="contenu_temoin"]/table/tr[2]/td[2]/text()').extract()[0]
        res = r.search(com_text)
        if res:
            res = map(lambda x: x if x else u'', res.groups()) # replace None with u''
            composition_period = res[0]
            known_work = res[1]
        else:
            composition_period = u''
            known_work = u''
            self.log('Error while parsing composition period.\n%s'%com_text)
        l.add_value('composition_period', composition_period)
        l.add_value('known_work', known_work)
        l.add_xpath('acronym', '//div[@class="contenu_temoin"]/table/tr[8]/td[2]/text()')
        
        bib = []
        for x in response.xpath('//div[@class="bibliolink"]').extract():
            bib.append(extract_text(x)[0].replace(u'\xa0', u' ')) # u'\xa0' is nonbreaking space
        l.add_value('bibliography', bib)

        return l.load_item()
