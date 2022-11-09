from email import contentmanager
import scrapy
from scrapy.utils.project import get_project_settings
from scrapy.selector import Selector
from DoubanSpider.items import DoubanUserItem
import json, os, csv

class UserSpider(scrapy.Spider):
    settings = get_project_settings()
    keyword = settings.get('KEYWORD')

    name = 'douban_user'
    allowed_domains = ['douban.com']
    user_count = 0
    total_num = 0

    def get_text_safely(self, response, xpath):
        info_list = response.xpath(xpath).getall()
        info = '\n'.join(filter(lambda content: content.strip(), info_list))
        return info

    def get_column_info_info_from_csv(self, column_num:int)->list[dict]:
        file_path = f'结果文件/{self.keyword}/{self.keyword}日记内容.csv'

        if not os.path.isfile(file_path):
            self.logger.debug(file_path)
            self.logger.info('没有找到读取文件')
            return []
        
        items_set = set()
        with open(file_path, 'r', encoding='utf-8-sig', newline='') as f:
            reader = csv.reader(f)
            is_first_read = True
            for row in reader:
                if is_first_read:
                    is_first_read = False
                    continue
                items_set.add(row[column_num])
        return list(items_set)

    def start_requests(self):
        urls = self.get_column_info_info_from_csv(4)
        self.total_num = len(urls)
        self.logger.debug(urls)
        for url in urls:
            if url:
                yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        self.user_count += 1
        self.logger.info(f'🚀正在爬取第{self.user_count}个用户，共{self.total_num}个用户，已完成{round(self.user_count/self.total_num*100, 2)}%的进度，网址是：{response.url}')
        self.logger.debug(f'请求头为：{response.request.headers}')
        self.logger.debug(f'cookies为：{response.request.cookies}')
        
        # body = response.xpath("//div[@class='info']//text()").get()
        # self.logger.debug(body)
        user_name = response.xpath("//div[@class='info']//h1//text()").get()
        self.logger.debug(f'user_name:{user_name}')
        user_info = self.get_text_safely(response, "//div[@class='user-info']//text()")
        self.logger.debug(user_info)
        user_verify = self.get_text_safely(response, "//div[@class='user-verify pl']//text()")
        self.logger.debug(user_verify)
        user_intro = self.get_text_safely(response, "//div[@class='user-intro']//span//text()")
        self.logger.debug(user_intro)
        ip_location = response.xpath("//div[@class='user-info']//span[@class='ip-location']//text()").get()
        self.logger.debug(f'ip_location:{ip_location}')
        create_time = response.xpath("//div[@class='user-info']//div[@class='pl']//text()[preceding-sibling::br]").get()
        self.logger.debug(f'create_time:{create_time}')
        person_concerned_num = response.xpath("//div[@id='friend']//a//text()").get()
        self.logger.debug(f'person_concerned_num:{person_concerned_num}')
        follow_num = response.xpath("//p[@class='rev-link']//a//text()").get()
        self.logger.debug(f'follow_num:{follow_num}')
        group_number = response.xpath("//div[@id='group']//h2//text()").get()
        self.logger.debug(f'group_number:{group_number}')

        user_item = DoubanUserItem()
        user_item['name'] = user_name
        user_item['user_verify'] = user_verify
        user_item['user_intro'] = user_intro
        user_item['ip_location'] = ip_location
        user_item['create_time'] = create_time
        user_item['person_concerned_num'] = person_concerned_num
        user_item['follow_num'] = follow_num
        user_item['group_number'] = group_number
        user_item['author_url'] = response.url
        user_item['keyword'] = self.keyword
        user_item['user_complete_info'] = user_info

        yield user_item