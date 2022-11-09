# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class DoubanNoteItem(scrapy.Item):
    # define the fields for your item here like:
    title = scrapy.Field()
    content = scrapy.Field()
    url =scrapy.Field()
    author_name = scrapy.Field()
    author_url = scrapy.Field()
    pub_time = scrapy.Field()
    like_num = scrapy.Field()
    react_num = scrapy.Field()
    rec_num = scrapy.Field()
    keyword = scrapy.Field()
    content_type = scrapy.Field()

class DoubanUserItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    user_verify = scrapy.Field()
    user_intro = scrapy.Field()
    ip_location = scrapy.Field()
    create_time = scrapy.Field()
    person_concerned_num = scrapy.Field()
    follow_num = scrapy.Field()
    group_number = scrapy.Field()
    author_url = scrapy.Field()
    keyword = scrapy.Field()
    user_complete_info = scrapy.Field()