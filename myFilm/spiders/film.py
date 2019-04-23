import scrapy
from scrapy import Request
import json
from ..items import MyFilmItem, MyCommentItem
import re
import os
from fontTools.ttLib import TTFont
import requests
from lxml.html import fromstring, tostring
import string

class MyFileSpider(scrapy.Spider):
    name = 'myFilm'
    allowed_domains = ['maoyan.com']
    start_urls = ['https://maoyan.com/films?showType=3']

    custom_settings = {
        "ITEM_PIPELINES": {
            'myFilm.pipelines.MyFilmPipeline': 300,
            'myFilm.pipelines.MyCommentPipeline': 301
        },
        "DEFAULT_REQUEST_HEADERS": {
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-encoding': 'gzip, deflate',
            'accept-language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4',
            'cookie':'uuid=4C55CBC0601D11E9A631B37CFB7F525898057B04D2874DBF91DEB5BE48270E96',
            'referer': 'https://mm.taobao.com/search_tstar_model.htm?spm=719.1001036.1998606017.2.KDdsmP',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.97 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
        },
        "ROBOTSTXT_OBEY": False  # 需要忽略ROBOTS.TXT文件
    }

    def start_requests(self):
        self.set_standar_font()
        url = '''https://maoyan.com/films?showType=3&offset={start}'''
        requests = []
        for i in range(2):
            request = Request(url.format(start=i * 30), callback=self.parse)
            requests.append(request)
        return requests
    
    # 建立标准字形库
    def set_standar_font(self):
        self.stdFont = TTFont('./fonts/std.woff') #deca.woff
        keys = []
        for number, gly in enumerate(self.stdFont.getGlyphOrder()):
            keys.insert(number, gly)
        #keys = self.stdFont['glyf'].keys()
        values = list(' .9243108567')#(' 4386275091.')
        # 构建基准 {name: num}
        self.stdDict = dict((k,v) for k,v in zip(keys, values))

    # 发送请求获得响应
    def get_html(self, url):
        response = requests.get(url, headers=self.custom_settings["DEFAULT_REQUEST_HEADERS"])
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

        # 打开字体文件，创建 self.curFont属性
        self.curFont = TTFont('./fonts/' + font_file)

        # 设置当前字体和字符对应关系
        self.curDict = {}
        for key in self.curFont['glyf'].keys():
            for k, v in self.stdDict.items():
                # 通过比较 字形定义 填充新的name和num映射关系
                if self.stdFont['glyf'][k] == self.curFont['glyf'][key]:
                    self.curDict[key] = v.strip()
                    break

    # 把获取到的数据用字体对应起来，得到真实数据
    def modify_data(self, data):
        # 获取 GlyphOrder 节点
        gly_list = self.curFont.getGlyphOrder()
        # 前两个不是需要的值，截掉
        gly_list = gly_list[2:]
        # 枚举, number是下标，正好对应真实的数字，gly是乱码
        for number, gly in enumerate(gly_list):
            # 把 gly 改成网页中的格式
            orgGly = gly
            gly = gly.replace("uni", r"\u").lower() # uniE30C ---> \\ue30c
            gly = gly.encode().decode('unicode_escape') # \\ue30c ---> \ue30c
            # 如果 gly 在字符串中，用对应数字替换
            if gly in data:
                data = data.replace(gly, self.curDict[orgGly]) #str(number)
        # 返回替换后的字符串
        return data

    # 解析电影热门评论列表
    def parseComment(self, response):
        item = response.meta['item'] 

        comments = response.xpath('//div[@class="comment-list-container"]/ul/li')
        for number, comment in enumerate(comments):
            commItem = MyCommentItem()
            commentID = comment.xpath('./@data-val').extract()
            commItem['cid'] = int(commentID[0].split(':')[1].replace("}",""))#json.loads(commentID[number])['commentid']
            commItem['fid'] = int(item['fid'])
            #score
            score = comment.xpath('//div[@class="main-header clearfix"]//ul[@class="score-star clearfix"]/@data-score').extract()
            if score:
                commItem['score'] = int(score[number]) 
            else: # drop this comment
                continue
            #comment
            commentContent = comment.xpath('//div[@class="comment-content"]/text()').extract()
            if commentContent:
                commItem['comment'] = commentContent[number]
            else: # drop this comment
                continue
            #liked
            liked = comment.xpath('//div[@class="main-header clearfix"]/div[@class="approve "]/span[@class="num"]/text()').extract()
            if liked:
                commItem['liked'] = int(liked[number])
            else:
                commItem['liked'] = 0
            #commentTime
            commentTime = comment.xpath('//div[@class="main-header clearfix"]/div[@class="time"]/@title').extract()
            if commentTime:
                commItem['commentTime'] = commentTime[number]
            else:
                commItem['commentTime'] = "1000-01-01"
            yield commItem


    # 解析电影详细信息
    def parseDetail(self, response):
        item = response.meta['item'] 

        # ename
        ename = response.xpath('//div[@class="movie-brief-container"]/div[@class="ename ellipsis"]/text()').extract()
        item['ename'] = ename[0] if ename else ''

        # tag country length
        tags = response.xpath('//div[@class="movie-brief-container"]/ul/li[1]/text()').extract()
        item['tags'] = tags[0] if tags else ''
        countryTime = response.xpath('//div[@class="movie-brief-container"]/ul/li[2]/text()').extract()[0]
        if countryTime:
            strs = countryTime.split()
            item['length'] = 0
            if strs:
                item['country'] = strs[0]
                for i in range(1, len(strs)): 
                    l = re.sub(r"\D", "", strs[i]) # '\n        中国香港,中国台湾\n          / 100分钟\n        '
                    if len(l) != 0:
                        item['length'] = int(l)
                        break
            else:
                item['country'] = ""
                print(countryTime)

        else:
            item['country'] = ''
            item['length'] = 0

        # releaseTime releaseTimeOnlyYear
        releaseTime = response.xpath('//div[@class="movie-brief-container"]/ul/li[3]/text()').extract()
        releaseTime = releaseTime[0].split()[0] if releaseTime else '1000-01-01' #2018-03-05 8:00大陆上映
        item['releaseTime'] = re.sub("[^0-9-]", "", releaseTime) #2018-03-05大陆上映
        if('-' not in item['releaseTime']):
            item['releaseTimeOnlyYear'] = 1
            item['releaseTime'] = item['releaseTime'] + "-01-01"
        else:
            item['releaseTimeOnlyYear'] = 0
        
        # 正则匹配字体文件
        html = response.xpath('//html').extract()[0]
        font_file = re.findall(r'vfile\.meituan\.net\/colorstone\/(\w+\.woff)', html)[0]
        self.create_font(font_file)

        # scorePeople scorePeopleUnit
        scorePeople = response.xpath('//div[@class="movie-stats-container"]/div[@class="movie-index"]/\
            div[@class="movie-index-content score normal-score"]/div[@class="index-right"]/span[@class="score-num"]/span[@class="stonefont"]/text()').extract()
        if scorePeople:
            if("万" in scorePeople[0]):
                item['scorePeopleNumUnit'] = 1
            else:
                item['scorePeopleNumUnit'] = 0
            scorePeople = re.sub(r"[\u4e00-\u9fa5]", "", scorePeople[0])
            item['scorePeopleNum'] = float(self.modify_data(scorePeople))
        else:
            item['scorePeopleNum'] = 0
            item['scorePeopleNumUnit'] = 0

        # boxOffice 
        noinfo = response.xpath('//div[@class="movie-index-content box"]/span[@class="no-info"]/text()').extract()
        if(noinfo): #empty
            item['boxOffice'] = 0
        else:
            boxOffice = response.xpath('//div[@class="movie-index-content box"]/span[@class="stonefont"]/text()').extract()[0]
            item['boxOffice'] = self.modify_data(boxOffice)
            unit = response.xpath('//div[@class="movie-index-content box"]/span[@class="unit"]/text()').extract()[0]
            if("亿" in unit):
                item['boxOffice'] = int(float(item['boxOffice'])*10000)
            else:
                item['boxOffice'] = int(item['boxOffice'])
        item['monetaryUnit'] = None
        
        item['actors'] = ''
        celebrityGroup = response.xpath('//div[@class="tab-content-container"]/div[@class="tab-celebrity tab-content"]/div[@class="celebrity-container"]//div[@class="celebrity-group"]')
        for number, group in enumerate(celebrityGroup):
            groupType = group.xpath('//div[@class="celebrity-type"]/text()').extract()
            if("演员" in groupType[number]):
                actorsInfo = group.xpath('//ul[@class="celebrity-list clearfix"]//li[@class="celebrity actor"]')
                cnt = 0
                for actorNum, actorInfo in enumerate(actorsInfo):
                    actualName = actorInfo.xpath('//div[@class="info"]/a/text()').extract()
                    if actualName:
                        actualName = actualName[actorNum].replace("\n","")
                        actualName = actualName.strip() 
                        item['actors'] = item['actors'] + actualName + ','
                    else: 
                        actualName = ''
                    if cnt < 9:
                        cnt = cnt+1
                    else:
                        break
                break
        item['actors'] = item['actors'].strip(string.punctuation)           
        yield item # film item

        # 解析评论信息
        #self.parseComment(response)
        #comment item
        comments = response.xpath('//div[@class="comment-list-container"]/ul/li')
        for number, comment in enumerate(comments):
            commItem = MyCommentItem()
            commentID = comment.xpath('./@data-val').extract()
            commItem['cid'] = int(commentID[0].split(':')[1].replace("}",""))#json.loads(commentID[number])['commentid']
            commItem['fid'] = int(item['fid'])
            #score
            score = comment.xpath('//div[@class="main-header clearfix"]//ul[@class="score-star clearfix"]/@data-score').extract()
            if score:
                commItem['score'] = int(score[number]) 
            else: # drop this comment
                continue
            #comment
            commentContent = comment.xpath('//div[@class="comment-content"]/text()').extract()
            if commentContent:
                commItem['comment'] = commentContent[number]
            else: # drop this comment
                continue
            #liked
            liked = comment.xpath('//div[@class="main-header clearfix"]/div[@class="approve "]/span[@class="num"]/text()').extract()
            if liked:
                commItem['liked'] = int(liked[number])
            else:
                commItem['liked'] = 0
            #commentTime
            commentTime = comment.xpath('//div[@class="main-header clearfix"]/div[@class="time"]/@title').extract()
            if commentTime:
                commItem['commentTime'] = commentTime[number]
            else:
                commItem['commentTime'] = "1000-01-01"
            yield commItem
        

    # 解析电影基础信息
    def parse(self, response):
        movies = response.xpath('//div[@class="movies-list"]/dl[@class="movie-list"]//dd')
        for movie in movies:
            item = MyFilmItem()
            item['name'] = movie.xpath('.//div[@class="channel-detail movie-item-title"]/@title').extract()[0]
            filmUrl = movie.xpath('.//div[@class="channel-detail movie-item-title"]/a/@href').extract()[0]
            item['fid'] = filmUrl[7:] #/films/12504341
            noScore = movie.xpath('.//div[@class="channel-detail channel-detail-orange"]/text()').extract()
            if noScore:
                item['score'] = 0.0
            else:
                integer = movie.xpath('.//div[@class="channel-detail channel-detail-orange"]/i[@class="integer"]/text()').extract()[0]
                fraction = movie.xpath('.//div[@class="channel-detail channel-detail-orange"]/i[@class="fraction"]/text()').extract()[0]
                item['score'] = float(integer[:-1]) + 0.1*float(fraction)

            posterURL = movie.xpath('.//div[@class="movie-item"]/a/div[@class="movie-poster"]/img/@data-src').extract()[0]
            src = r'https://.*?.jpg' 
            pattern = re.compile(src)     #re.compile()，可以把正则表达式编译成一个正则表达式对象
            imglist = re.findall(pattern, posterURL) 
            item['poster'] = imglist[0] if imglist else ''

            filmUrl = "https://maoyan.com" + filmUrl
            request = Request(filmUrl, callback=self.parseDetail)
            request.meta['item'] = item
            yield request

