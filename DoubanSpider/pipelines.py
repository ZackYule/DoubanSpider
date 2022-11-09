# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from DoubanSpider.items import DoubanNoteItem, DoubanUserItem
import os
import csv

class DoubanspiderPipeline:

    def csv_pipeline(self, item:dict, keyword:str, content_type:str, header:list[str]):
        base_dir = '结果文件' + os.sep + keyword
        file_path = base_dir + os.sep + keyword + content_type + '.csv'

        if not os.path.isdir(base_dir):
            os.makedirs(base_dir)
        if not os.path.isfile(file_path):
            is_first_write = 1
        else:
            is_first_write = 0
            
        if item:
            with open(file_path, 'a', encoding='utf-8-sig', newline='') as f:
                writer = csv.writer(f)
                if is_first_write:
                    if header:
                        writer.writerow(header)
                writer.writerow([str(item[key]).strip() for key in item.keys()])

    def process_item(self, item, spider):
        if isinstance(item, DoubanNoteItem):
            self.csv_pipeline(item, item['keyword'],'日记内容',['标题','内容','发布地址','作者','作者主页','发布时间','喜欢数','收藏数','转发数', '关键字', '内容类型'])
        elif isinstance(item, DoubanUserItem):
            self.csv_pipeline(item, item['keyword'],'用户信息',['昵称','认证','简介','ip属地','创建时间','关注数','粉丝数','小组数','主页地址', '关键字', '完整信息'])
        
        return item
