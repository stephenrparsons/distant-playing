
# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class MobyItem(scrapy.Item):
    title = scrapy.Field()
    link = scrapy.Field()
    description = scrapy.Field()
    publishedBy = scrapy.Field()
    developedBy = scrapy.Field()
    released = scrapy.Field()
    platforms = scrapy.Field()
    genre = scrapy.Field()
    perspective = scrapy.Field()
    theme = scrapy.Field()
    misc = scrapy.Field()
    body = scrapy.Field()
    ratings = scrapy.Field()

class SteamItem(scrapy.Item):
    title = scrapy.Field()
    link = scrapy.Field()
    description = scrapy.Field()
    shortDescription = scrapy.Field()
    userReviews = scrapy.Field()
    released = scrapy.Field()
    tags = scrapy.Field()
    price = scrapy.Field()
    misc = scrapy.Field()
    genre = scrapy.Field()
    developedBy = scrapy.Field()
    publishedBy = scrapy.Field()
    body = scrapy.Field()
    windowsSysRequirements = scrapy.Field()
