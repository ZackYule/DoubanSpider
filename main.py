from scrapy.cmdline import execute

print('🔥'*30)
# execute('scrapy crawl douban'.split())
execute('scrapy crawl douban_user'.split())
