# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class WoolItem(scrapy.Item):
    # define the fields for every wool yarn fetched
    brand = scrapy.Field()
    name = scrapy.Field()
    price = scrapy.Field()
    delivery_time = scrapy.Field()
    needle_size = scrapy.Field()
    composition = scrapy.Field()
    site = scrapy.Field()
