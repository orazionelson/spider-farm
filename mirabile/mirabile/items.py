# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.org/en/latest/topics/items.html

from scrapy import Item, Field

class  MirabileItem(Item):
    # define the fields for your item here like:
    # name = Field()
    author = Field()
    title = Field()
    related_works = Field()
    incipit = Field()
    explicit = Field()
    references = Field()
    shelfmark = Field()
    related_projects = Field()
    permalink = Field()
    html = Field()
