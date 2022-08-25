from email import contentmanager
import scrapy
from scrapy.utils.project import get_project_settings
from scrapy.selector import Selector
import json

class QuotesSpider(scrapy.Spider):
    settings = get_project_settings()
    keyword = settings.get('KEYWORD')

    name = 'douban'
    allowed_domains = ['douban.com']
    list_count = 0
    content_count = 0

    def start_requests(self):
        urls = [
            f'https://www.douban.com/search?cat=1015&q={self.keyword}', ]
        yield scrapy.Request(url=urls[0], callback=self.parse)

    def parse(self, response):
        self.list_count += 1
        self.logger.debug(f'目前页数为第{self.list_count}页')
        # 获取笔记链接
        note_id_list = response.xpath("//div[@class='title']//a/@onclick").re(r'sid: (\d+),')
        if len(note_id_list) > 0:
            for note_id in note_id_list:
                url = f'https://www.douban.com/note/{note_id}/'
                self.logger.debug(f'网址是：{url}')
                yield scrapy.Request(url=url, callback=self.parse_note_page)

        # 获取更多列表
        if len(response.xpath("//div[@class='result-list-ft']").getall()) > 0:
            self.logger.debug(f'还有下一页，目前页数为第{self.list_count}页')
            url = f'https://www.douban.com/j/search?q={self.keyword}&start={20*self.list_count}&cat=1015'
            yield scrapy.Request(url=url, callback=self.parse_json_data)

    def parse_json_data(self, response):
        self.list_count += 1
        self.logger.debug(f'目前页数为第{self.list_count}页')

        response_dict = json.loads(response.text)
        # 获取笔记链接
        for item_html_string in response_dict['items']:
            response_selector =Selector(text=item_html_string)
            note_id_list = response_selector.xpath("//div[@class='title']//a/@onclick").re(r'sid: (\d+),')
            if len(note_id_list) > 0:
                for note_id in note_id_list:
                    url = f'https://www.douban.com/note/{note_id}/'
                    self.logger.debug(f'网址是：{url}')
                    yield scrapy.Request(url=url, callback=self.parse_note_page)
        
        # 获取更多列表
        if response_dict['more']:
            self.logger.debug(f'还有下一页，目前页数为第{self.list_count}页')
            url = f'https://www.douban.com/j/search?q={self.keyword}&start={20*self.list_count}&cat=1015'
            yield scrapy.Request(url=url, callback=self.parse_json_data)
    
    def parse_note_page(self, response):
        self.content_count += 1
        title = (' ').join(response.xpath("//div[@class='note-header note-header-container']/h1").re(r'<h1>\s*(\S*)\s*</h1>'))
        content = ('\n').join(response.xpath("//div[@id='link-report']//div[@class='note']//text()").getall())
        author_name = response.xpath("//a[@class='note-author']//text()").get()
        author_url = response.xpath("//a[@class='note-author']//@href").get()
        pub_time = response.xpath("//span[@class='pub-date']//text()").get()
        self.logger.debug(f'标题是：{title}')
        self.logger.debug(f'内容是：{content}')
        self.logger.debug(f'作者是：{author_name}')
        self.logger.debug(f'作者主页是：{author_url}')
        self.logger.debug(f'发布时间是：{pub_time}')

        yield {
            'keyword': self.keyword,
            'class':'note',
            'note_item': {
                'title': title,
                'content': content,
                'author_name': author_name,
                'author_url': author_url,
                'pub_time': pub_time,
            },
        }