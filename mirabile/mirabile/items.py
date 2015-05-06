# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.org/en/latest/topics/items.html

from scrapy import Item, Field

class  MirabileTitleItem(Item):
    author = Field()
    title = Field()
    title_note = Field()
#    secondary_note = Field() #not enough examples
    other_attributions = Field()
    other_author_related = Field()
    related_works = Field()
    incipit = Field()
    explicit = Field()
    references = Field()
    references_note = Field()
    editorial_note = Field()
    shelfmarks = Field()
    shelfmarks_note = Field()
    related_projects = Field()
    permalink = Field()

class  MirabileDemoItem(Item):
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
