# -*- coding: utf-8 -*-
import scrapy

import re
from urlparse import urljoin
from scrapy.contrib.loader import ItemLoader
from scrapy.contrib.loader.processor import MapCompose
from jonas.items import JonasAuthorItem, extract_text

class JonasAuthorSpider(scrapy.Spider):
    name = "jonas-author"
    allowed_domains = ["jonas.irht.cnrs.fr"]
    start_urls = (
        'http://jonas.irht.cnrs.fr/consulter/intervenant/detail_intervenant.php?intervenant=136',
    )

    def parse(self, response):
        self.log("Our starting URL is %s"%self.start_urls)

        def absolutize_url(rel_url):
            return urljoin(response.url, rel_url)
            
        l = ItemLoader(item=JonasAuthorItem(), response=response)
        
        l.add_xpath('author', '/html/body/div[1]/div[3]/div[2]/div[2]/table[1]/tr/td[2]/text()')
        l.add_xpath('permalink', '/html/body/div[1]/div[3]/fieldset[2]/p/a/text()')
        l.add_xpath('born_after', '/html/body/div[1]/div[3]/div[2]/div[2]/table[2]/tr/td[2]/text()')
        l.add_xpath('born_before', '/html/body/div[1]/div[3]/div[2]/div[2]/table[3]/tr/td[2]/text()')
        l.add_xpath('dead_after', '/html/body/div[1]/div[3]/div[2]/div[2]/table[4]/tr/td[2]/text()')
        l.add_xpath('dead_before', '/html/body/div[1]/div[3]/div[2]/div[2]/table[5]/tr/td[2]/text()')

        l.add_xpath('oeuvres_link_detailed_works',
                    '//div[@id="blocAssociationsOeuvres"]/div/a/@href',
                    MapCompose(absolutize_url)
                    )
        oeuvres = '//div[@id="blocAssociationsOeuvres"]/div/span[@class="%s"]/text()'
        l.add_xpath('incipit', oeuvres % 'curincipitoeuvre')
        l.add_xpath('oeuvres_title', oeuvres % 'curtitreoeuvre')
        tmp = []
        sel = response.xpath('//div[@id="blocAssociationsOeuvres"]/div[@class="ed_com" or @class="association"]')
        for x in sel:
            if x.xpath('@class').extract()[0] == u'association':
                tmp.append(u'')
            else:
                tmp[-1] = x.xpath('text()').extract()[0]
        l.add_value('editorial_note', tmp)

        l.add_xpath('associated_link_detailed_works',
                    '//div[@id="blocAssociationsParutions"]/div/a/@href',
                    MapCompose(absolutize_url)
                    )
        l.add_xpath('associated_manuscripts', '//div[@id="blocAssociationsParutions"]/div[@class="association"]')

        l.add_xpath('bibliography_link_detailed_works',
                    '//div[@id="blocBibliographies"]/div/a/@href',
                    MapCompose(absolutize_url)
                    )
        l.add_xpath('author_date', '//div[@class="bibliolink"]/span[1]/text()')
        
        name, title, in_work, pages = [], [], [], []
        r = re.compile('(.*?), (.*?),(?: in : (.*),)? \d{4}(?: ?[:,] (.*))?\.')
        for x in response.xpath('//div[@class="bibliolink"]/span[2]').extract():
            extracted_text = extract_text(x)[0].replace(u'\xa0', u' ') # u'\xa0' is nonbreaking space
            res = r.search(extracted_text)
            if res:
                res = map(lambda x: x if x else u'', res.groups()) # replace None with u''
                name.append(res[0])
                title.append(res[1])
                in_work.append(res[2])
                pages.append(res[3])
            else:
                self.log('Bibliography not parsed correctly:\n\n%s\n'%extracted_text)                        
        #self.log('LENGTHS: name %s, title %s, in_work %s, pages %s'%tuple(map(len,[ name, title, in_work, pages])))        
        l.add_value('complete_name', name)
        l.add_value('bibliography_title', title)
        l.add_value('in_work', in_work)
        l.add_value('pages', pages)

        tmp = []
        for x in response.xpath('//div[@class="bibliolink"]'):
            addition = x.xpath('./div[@class="info"]/text()').extract()
            if addition:
                tmp.append(addition[0])
            else:
                tmp.append(u'')
        l.add_value('topic', tmp)
        
        l.add_xpath('signature', '//ul[@id="listeSignatures"]/li/text()', MapCompose(unicode.strip))
        
        return l.load_item()
