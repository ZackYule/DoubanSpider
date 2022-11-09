from email import contentmanager
import scrapy
from scrapy.utils.project import get_project_settings
from scrapy.selector import Selector
from DoubanSpider.items import DoubanNoteItem
import json

class NoteSpider(scrapy.Spider):
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
        self.logger.debug(f'请求头为：{response.request.headers}')
        self.logger.debug(f'cookies为：{response.request.cookies}')
        # 获取笔记链接
        note_result_list = response.xpath("//div[@class='title']").getall()
        
        if len(note_result_list) > 0:
            for note_result in note_result_list:
                self.logger.debug(f'note_result{note_result},{type(note_result)}')
                note_id_list = Selector(text=note_result).xpath("//a/@onclick").re(r'sid: (\d+),')
                note_id = 0 if len(note_id_list)==0 else note_id_list[0]
                like_num_list = Selector(text=note_result).xpath("//div[@class='info']//text()").re(r'(\d+)')
                like_num = 0 if len(like_num_list)==0 else like_num_list[0]
                self.logger.debug(f'note_id是：{note_id}')
                self.logger.debug(f'like_num是：{like_num}')
                url = f'https://www.douban.com/note/{note_id}/'
                self.logger.debug(f'网址是：{url}')
                yield scrapy.Request(url=url, callback=self.parse_note_page, cb_kwargs=dict(like_num=like_num))

        # 获取更多列表
        if len(response.xpath("//div[@class='result-list-ft']").getall()) > 0:
            self.logger.debug(f'还有下一页，目前页数为第{self.list_count}页')
            url = f'https://www.douban.com/j/search?q={self.keyword}&start={20*self.list_count}&cat=1015'
            yield scrapy.Request(url=url, callback=self.parse_more_note_page_data)

    def parse_more_note_page_data(self, response):
        self.list_count += 1
        self.logger.debug(f'目前页数为第{self.list_count}页')

        response_dict = json.loads(response.text)
        # 获取笔记链接
        for item_html_string in response_dict['items']:
            response_selector =Selector(text=item_html_string)
            note_id_list = response_selector.xpath("//div[@class='title']//a/@onclick").re(r'sid: (\d+),')
            like_num_list = response_selector.xpath("//div[@class='title']//div[@class='info']//text()").re(r'(\d+)')
            like_num = 0 if len(like_num_list)==0 else like_num_list[0]
            self.logger.debug(f'like_num_in_json是：{like_num}')
            if len(note_id_list) > 0:
                for note_id in note_id_list:
                    url = f'https://www.douban.com/note/{note_id}/'
                    self.logger.debug(f'网址是：{url}')
                    yield scrapy.Request(url=url, callback=self.parse_note_page, cb_kwargs=dict(like_num=like_num))
        
        # 获取更多列表
        if response_dict['more']:
            self.logger.info(f'还有下一页，目前页数为第{self.list_count}页')
            url = f'https://www.douban.com/j/search?q={self.keyword}&start={20*self.list_count}&cat=1015'
            yield scrapy.Request(url=url, callback=self.parse_more_note_page_data)
    
    def parse_note_page(self, response, like_num):
        self.content_count += 1
        title = (' ').join(response.xpath("//div[@class='note-header note-header-container']/h1").re(r'<h1>\s*(\S*)\s*</h1>'))
        content = ('\n').join(response.xpath("//div[@id='link-report']//div[@class='note']//text()").getall())
        author_name = response.xpath("//a[@class='note-author']//text()").get()
        author_url = response.xpath("//a[@class='note-author']//@href").get()
        pub_time = response.xpath("//span[@class='pub-date']//text()").get()
        react_num = response.xpath("//div[@class='action-collect']//span[@class='react-num']//text()").get(default='0')
        rec_num = response.xpath("//span[@class='rec-num']//text()").get(default='0')
        self.logger.debug(f'标题是：{title}')
        self.logger.debug(f'内容是：{content}')
        self.logger.debug(f'作者是：{author_name}')
        self.logger.debug(f'作者主页是：{author_url}')
        self.logger.debug(f'发布时间是：{pub_time}')
        self.logger.debug(f'喜欢数是：{like_num}')
        self.logger.debug(f'转发数是：{react_num}')
        self.logger.debug(f'转发数是：{rec_num}')

        note_item = DoubanNoteItem()
        note_item['title'] = title
        note_item['content'] = content
        note_item['url'] = response.url
        note_item['author_name'] = author_name
        note_item['author_url'] = author_url
        note_item['pub_time'] = pub_time
        note_item['like_num'] = like_num
        note_item['react_num'] = react_num
        note_item['rec_num'] = rec_num
        note_item['keyword'] = self.keyword
        note_item['content_type'] = 'note'

        yield note_item