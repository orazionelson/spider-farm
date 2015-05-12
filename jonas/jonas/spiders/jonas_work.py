# -*- coding: utf-8 -*-
import scrapy

import re
from urlparse import urljoin
from scrapy.contrib.loader import ItemLoader
from scrapy.contrib.loader.processor import MapCompose
from jonas.items import JonasWorkItem, extract_text

class JonasWorkSpider(scrapy.Spider):
    name = "jonas-work"
    allowed_domains = ["jonas.irht.cnrs.fr"]
    start_urls = (
        'http://jonas.irht.cnrs.fr/oeuvre/4139',
    )

    def parse(self, response):
        self.log("Our starting URL is %s"%self.start_urls)

        def absolutize_url(rel_url):
            return urljoin(response.url, rel_url)
            
        l = ItemLoader(item=JonasWorkItem(), response=response)
        
        l.add_xpath('permalink', '/html/body/div[1]/div[3]/fieldset[2]/p/a/text()')
        
        l.add_xpath('title', '//td[@class="titre"]/text()')
        l.add_xpath('author', '//td[@class="auteur"]/text()')
        l.add_xpath('incipit', '//td[@class="incipit"]/text()')
        l.add_xpath('shape', '//table[@class="table_identification"]/tr[8]/td[2]/text()')
        
        r = re.compile(u'(.*) (?:\((.*)\))')
        com_text = response.xpath('//table[@class="table_identification"]/tr[12]/td[2]/text()').extract()[0]
        res = r.search(com_text)
        if res:
            res = map(lambda x: x if x else u'', res.groups()) # replace None with u''
            composition_period = res[0]
            note_work = res[1]
        else:
            composition_period = u''
            note_work = u''
            self.log('Error while parsing composition period.\n%s'%com_text)
        l.add_value('composition_period', composition_period)
        l.add_value('note_work', note_work)
        
        l.add_xpath('language', '//table[@class="table_identification"]/tr[13]/td[2]/text()')
        l.add_xpath('other_authors', '//table[@class="table_autres"]/tr/td[2]/ul/li/a/span/text()')
        l.add_xpath('role', '//table[@class="table_autres"]/tr/td[2]/ul/li/span[1]/text()')
        l.add_xpath('hierarchy', '//ul[@class="thesaurus"]//text()')

        l.add_xpath('associated_link_detailed_works',
                    '//div[@class="association"]/a/@href',
                    MapCompose(absolutize_url)
                    )
        l.add_xpath('associated_author', '//div[@class="association"]/span[@class="curauteuroeuvre"]/text()')
        l.add_xpath('associated_title', '//div[@class="association"]/span[@class="curtitreoeuvre"]/text()')
        l.add_xpath('associated_incipit', '//div[@class="association"]/span[@class="curincipitoeuvre"]/text()')

        r = re.compile(u'(\d*) témoin')
        wit = response.xpath('//div[@id="temoins"]/div[2]/text()').extract()[0]
        wit = wit.replace(u'\xa0', u' ') # u'\xa0' is nonbreaking space
        res = r.search(wit)
        if res:
            num_wit = res.group(1)
        else:
            num_wit = u''
            self.log("Error parsing number of witnesses:\n%s"%wit)
        l.add_value('number_of_witnesses', num_wit)

        l.add_xpath('manuscripts', '//div[@class="un_temoin temoin"]')
        
        l.add_xpath('bibliography_link',
                    '//div[@id="blocBibliographies"]/div/a/@href',
                    MapCompose(absolutize_url)
                    )
        bib = []
        for x in response.xpath('//div[@class="bibliolink"]').extract():
            bib.append(extract_text(x)[0].replace(u'\xa0', u' ')) # u'\xa0' is nonbreaking space
        l.add_value('bibliography', bib)

        return l.load_item()
