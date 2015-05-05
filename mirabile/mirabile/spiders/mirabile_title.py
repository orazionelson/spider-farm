# -*- coding: utf-8 -*-
import scrapy
from scrapy.contrib.linkextractors import LinkExtractor

from mirabile.items import MirabileTitleItem


class MirabileTitleSpider(scrapy.Spider):
    name = 'mirabile-title'
    allowed_domains = ['http://www.mirabileweb.it']
    start_urls = [
        'http://www.mirabileweb.it/title/divisio-textus-summae-contra-gentiles-thomae-de-aq-title/129674',
        'http://www.mirabileweb.it/title/sermo-homo-quidam-fecit-coenam-magnam-thomas-de-aq-title/13794',
        'http://www.mirabileweb.it/title/adesto-supplicantibus-beate-pastor-title/181641',
        'http://www.mirabileweb.it/title/breve-epithoma-rerum-apud-malacam-gestarum-anno-14-title/132851',
        'http://www.mirabileweb.it/title/abreviatio-thomae-de-aquino-expositionis-evangelio-title/27755',
        'http://www.mirabileweb.it/title/acta-capitulorum-generalium-ordinis-praedicatorum--title/18402',
        'http://www.mirabileweb.it/title/abbreviatio-in-gestis-et-miraculis-sanctorum-iohan-title/1342',
        'http://www.mirabileweb.it/title/abbreviationes-librorum-naturalium-simon-de-favers-title/123382',
        'http://www.mirabileweb.it/title/ad-amicum-venturum-ad-festum-baculi-leonius-parisi-title/14537',
        'http://www.mirabileweb.it/title/adagia-gerhardus-listrius-n-1470-ca-m-1522-ca--title/130227',
        'http://www.mirabileweb.it/title/adoro-te-devote-thomas-de-aquino-n-1224-1225-m-7-3-title/6990',
        'http://www.mirabileweb.it/title/carmina-latina-varia-en-domus-andree-franciscus-pe-title/121315',
        'http://www.mirabileweb.it/title/supplicationes-ad-papam-clementem-vi-franciscus-pe-title/121438',
        'http://www.mirabileweb.it/title/catharinae-collaudemus-virtutum-insignia-title/171019'
        ]

    def get_field(self, field, xpath, sel, item):
        try:
            item[field] = map(unicode.strip, sel.xpath(xpath).extract())
 #           self.log("\nfield: %s\n$xpath: %s\nselector: %s\nitem: %s"%(field, xpath, sel, item[field]))
        except:
            scrapy.log.msg("Field %s not parsed correctly."%field)

    def extract_shelfmarks(self, sel, item):
        
        def extract_shelfmark(sel, stopword):
            '''
            Given a selector for a shelfmark it iterates its following until stopword.
            Returns all visited in a list.
            '''
            res = [sel.xpath('./text()')[0]]
            for x in sel.xpath('./following::text()'):
                if x.extract().startswith(stopword):
                    break
                else:
                    res.append(x)
            return u' '.join(map(lambda x: x.extract(), res)).strip()
            
        lastshelfmark = sel.xpath('.//a[starts-with(@href,"/manuscript")][last()]')
        if not lastshelfmark:
            return []
        tmp = [extract_shelfmark(lastshelfmark, 'Altri progetti collegati:')] # sometimes Notes get included here
        stopword = lastshelfmark.xpath('./text()')[0].extract()
        shelfmarks = sel.xpath('.//a[starts-with(@href,"/manuscript")]')[:-1]
        shelfmarks.reverse()
        for shelfmark in shelfmarks:
            res = extract_shelfmark(shelfmark, stopword)
            tmp.append([res])
            stopword = res[0]
        tmp.reverse()
        item['shelfmarks'] = tmp

    def parse(self, response):
        scrapy.log.msg("Our starting URL is %s"%self.start_urls)
        item = MirabileTitleItem()
        sel = response.selector.xpath('//td[@class="scheda_view"]')
        self.get_field('author', './p[1]/a/b/text()', sel, item)
        self.get_field('title', './p[2]/b/i/text()', sel, item)
        self.get_field('title_note', './p[2]/font[1]/text()', sel, item)        
        self.get_field('related_works' , './/p[2]/a/text()', sel, item)

        oar_xpath = '//font[starts-with(text(),"Autori di riferimento")]/following-sibling::a//text()'

        item['other_author_related'] = ' '.join(response.selector.xpath(oar_xpath).extract()).strip()

        inc_excp = "//p[starts-with(text(),'inc.')]/text()"
        inc_excp = response.selector.xpath(inc_excp).extract() #throws XPath error for selector sel, why?
        if inc_excp:
            item['incipit'] = inc_excp[0]
            try:
                item['explicit'] = inc_excp[1]
            except:
                scrapy.log.msg('Incipit/explicit field may be parsed incorrectly.')

        try:
            tmp = response.selector.xpath('//p[starts-with(font,"Riferimenti")]//text()')
            item['references'] = ' '.join(map(unicode.strip, tmp.extract())[2:]).strip()
        except:
            scrapy.log.msg('Field references is not parsed correctly.')

        self.get_field('references_note', '//p[starts-with(font,"Riferimenti")]/following::text()[position()<3]', response.selector, item)
        first_shelfmark = response.selector.xpath('.//a[starts-with(@href,"/manuscript")]/text()[1]').extract()
        if item['references_note'][1] == first_shelfmark:
            item['references_note'] = u''
        item['references_note'] = [u' '.join(item['references_note']).strip()]

        #self.get_field('shelfmarks', './/a[starts-with(@href,"/manuscript")]/text()', sel, item)
        self.extract_shelfmarks(sel, item)        

        try:
            rel_proj_xpath = '//div[@class="altri_progetti"]/following-sibling::a/text()'
            item['related_projects'] = sel.xpath(rel_proj_xpath).extract()
        except:
            scrapy.log.msg('Field related_projects is not parsed correctly.')

        self.get_field('permalink' , './/span[@class="permalink"]/text()', sel, item)
        yield item