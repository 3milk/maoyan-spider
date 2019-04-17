# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class MyFilmItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    fid = scrapy.Field()
    ename = scrapy.Field()
    score = scrapy.Field()
    releaseTime = scrapy.Field()
    releaseTimeOnlyYear = scrapy.Field()
    scorePeopleNum = scrapy.Field()
    scorePeopleNumUnit = scrapy.Field()
    boxOffice = scrapy.Field()
    monetaryUnit = scrapy.Field()
    actors = scrapy.Field()
    country = scrapy.Field()
    length = scrapy.Field()
    tags = scrapy.Field()
    poster = scrapy.Field() 
    pass  


class MyCommentItem(scrapy.Item):
    # define the fields for your item here like:
    cid = scrapy.Field()
    fid = scrapy.Field()
    score = scrapy.Field()
    comment = scrapy.Field()
    liked = scrapy.Field()
    commentTime = scrapy.Field()
    pass