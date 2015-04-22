# -*- coding: utf-8 -*-

# Scrapy settings for mirabile project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'mirabile'

SPIDER_MODULES = ['mirabile.spiders']
NEWSPIDER_MODULE = 'mirabile.spiders'


SPIDER_MIDDLEWARES = {
    'scrapy.contrib.spidermiddleware.itemsextender.ItemsExtenderMiddleware': 500,
}

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'mirabile (+http://www.yourdomain.com)'
