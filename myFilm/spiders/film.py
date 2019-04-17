import scrapy
from scrapy import Request
import json
from myFilm.items import MyFilmItem
import re
import os
from fontTools.ttLib import TTFont
import requests

class MyFileSpider(scrapy.Spider):
    name = 'myFilm'
    allowed_domains = ['maoyan.com']
    start_urls = ['https://maoyan.com/films?showType=3']

    custom_settings = {
        "ITEM_PIPELINES": {
            'myFilm.pipelines.MyfilmPipeline': 300,
            'myFilm.pipelines.MycommentPipeline': 300
        },
        "DEFAULT_REQUEST_HEADERS": {
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-encoding': 'gzip, deflate',
            'accept-language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4',
            'referer': 'https://mm.taobao.com/search_tstar_model.htm?spm=719.1001036.1998606017.2.KDdsmP',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.97 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
        },
        "ROBOTSTXT_OBEY": False  # 需要忽略ROBOTS.TXT文件
    }

    def start_requests(self):
        url = '''https://maoyan.com/films?showType=3&offset={start}'''
        requests = []
        for i in range(2):
            request = Request(url.format(start=i * 30), callback=self.parse)
            requests.append(request)
        return requests

    # 发送请求获得响应
    def get_html(self, url):
        response = requests.get(url, headers=self.custom_settings[1])
        #request = Request(filmUrl, callback=self.parseDetail)
        return response.content

    # 创建 self.font 属性
    def create_font(self, font_file):
        # 列出已下载文件
        file_list = os.listdir('./fonts')
        #判断是否已下载
        if font_file not in file_list:
            # 未下载则下载新库
            print('不在字体库中, 下载:', font_file)
            url = 'http://vfile.meituan.net/colorstone/' + font_file
            new_file = self.get_html(url)
            with open('./fonts/' + font_file, 'wb') as f:
                f.write(new_file)

        # 打开字体文件，创建 self.font属性
        self.font = TTFont('./fonts/' + font_file)

    # 把获取到的数据用字体对应起来，得到真实数据
    def modify_data(self, data):
        # 获取 GlyphOrder 节点
        gly_list = self.font.getGlyphOrder()
        # 前两个不是需要的值，截掉
        gly_list = gly_list[2:]
        # 枚举, number是下标，正好对应真实的数字，gly是乱码
        for number, gly in enumerate(gly_list):
            # 把 gly 改成网页中的格式
            gly = gly.replace('uni', '&#x').lower() + ';'
            # 如果 gly 在字符串中，用对应数字替换
            if gly in data:
                data = data.replace(gly, str(number))
        # 返回替换后的字符串
        return data

    def parseDetail(self, response):
        item = response.meta['item'] 

        # tag country length
        item['tags'] = response.xpath('//div[@class="movie-brief-container"]/ul/li[1]/text()').extract()[0]
        countryTime = response.xpath('//div[@class="movie-brief-container"]/ul/li[2]/text()').extract()[0]
        item['country'] = countryTime.split()[0]
        item['length'] = re.sub(r"\D", "", countryTime.split()[1]) #TODO '\n        中国香港,中国台湾\n          / 100分钟\n        '
        
        # releaseTime releaseTimeOnlyYear
        releaseTime = response.xpath('//div[@class="movie-brief-container"]/ul/li[3]/text()').extract()[0]
        item['releaseTime'] = re.sub("[^0-9-]", "", releaseTime)
        if('-' not in releaseTime):
            item['releaseTimeOnlyYear'] = 1
        else:
            item['releaseTimeOnlyYear'] = 0
        
        # 正则匹配字体文件
        html = response.xpath('//html/text()').extract()[0]#self.get_html(self.url).decode('utf-8')
        font_file = re.findall(r'vfile\.meituan\.net\/colorstone\/(\w+\.woff)', html)[0]
        self.create_font(font_file)

        # scorePeople scorePeopleUnit
        scorePeople = response.xpath('//div[@class="movie-stats-container"]/div[@class="movie-index"]/\
            div[@class="movie-index-content score normal-score"]/div[@class="index-right"]/span[@class="score-num"]/span[@class="stonefont"]/text()').extract()[0]
        if("万" in scorePeople):
            item['scorePeopleNumUnit'] = 1
        else:
            item['scorePeopleNumUnit'] = 0

        scorePeople = re.sub(r"[^0-9\.]", "", scorePeople)
        item['scorePeopleNum'] = self.modify_data(scorePeople)
        
        item['scorePeopleNumUnit']

        boxOffice = response.xpath('//div[@class="movie-index-content box"]/span[@class="stonefont"]').extract()[0]
        unit = response.xpath('//div[@class="movie-index-content box"]/span[@class="unit"]').extract()[0]
        noinfo = response.xpath('//div[@class="movie-index-content box"]/span[@class="no-info"]').extract()[0]
        if(noinfo == None):
            if(unit == '亿'):
                item['boxOffice'] = boxOffice*10000
            else:
                item['boxOffice'] = boxOffice
        else:
            item['boxOffice'] = None
        
        #item['actors'] = response.xpath()

        yield item #yield

    def parse(self, response):
        movies = response.xpath('//div[@class="movies-list"]/dl[@class="movie-list"]')
        for movie in movies:
            item = MyFilmItem()
            item['name'] = movie.xpath('./dd/div[@class="channel-detail movie-item-title"]/@title').extract()[0]
            filmUrl = movie.xpath('./dd/div[@class="channel-detail movie-item-title"]/a/@href').extract()[0]
            item['fid'] = filmUrl[7:] #/films/12504341
            integer = movie.xpath('./dd/div[@class="channel-detail channel-detail-orange"]/i[@class="integer"]/text()').extract()[0]
            fraction = movie.xpath('./dd/div[@class="channel-detail channel-detail-orange"]/i[@class="fraction"]/text()').extract()[0]
            item['score'] = float(integer[:-1]) + 0.1*float(fraction)

            posterURL = movie.xpath('./dd/div[@class="movie-item"]/a/div[@class="movie-poster"]/img/@data-src').extract()[0]
            src = r'https://.*?.jpg' 
            pattern = re.compile(src)     #re.compile()，可以把正则表达式编译成一个正则表达式对象
            imglist = re.findall(pattern, posterURL) 
            item['poster'] = imglist[0]

            filmUrl = "https://maoyan.com" + filmUrl
            request = Request(filmUrl, callback=self.parseDetail)
            request.meta['item'] = item
            yield request

