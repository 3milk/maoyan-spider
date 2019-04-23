# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals

import time

# 导入随机模块
import random
# 导入IPPOOL UAPOOL
from myFilm.settings import IPPOOL
from myFilm.settings import UAPOOL
# 导入官方文档对应的HttpProxyMiddleware
from scrapy.downloadermiddlewares.httpproxy import HttpProxyMiddleware
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
import requests
#from myFilm.try_to_getProxy import ProxyModel

from scrapy.http import HtmlResponse

class IPPOOLS(HttpProxyMiddleware):
    # 初始化
    def __init__(self, ip=''):
        self.ip = ip
        self.current_proxy = None
        # 这里填写无忧代理IP提供的API订单号（请到用户中心获取）
        self.order = "d31aadd16053290f8694a8278b8d64d9"
        # 获取IP的API接口
        self.apiUrl = "http://api.ip.data5u.com/dynamic/get.html?order=" + self.order + "&ttl=1&sep=3"
        self.init_proxy()
        
    # 请求处理，随机选择一个IP代理
    def process_request(self, request, spider):
        # 先随机选择一个IP
        self.current_proxy = random.choice(IPPOOL)
        print("当前使用IP是："+ self.current_proxy)
        request.meta["proxy"] = "http://" + self.current_proxy
    
    # 响应处理，视情况更新IP代理池
    def process_response(self, request, response, spider):
        # 如果对方重定向（302）去验证码的网页，换掉代理IP
        # 'captcha' in response.url 指的是有时候验证码的网页返回的状态码是200，所以用这个作为辨识的标志
        if response.status != 200 or 'captcha' in response.url:
            # 如果来到这里，说明这个请求已经被识别为爬虫了
            # 所以这个请求就相当于什么都没有获取到
            # 所以要重新返回request，让这个请求重新加入到调度中
            # 下次再发送
            print('%s代理失效' % response.url)
            self.update_proxy(response.url)
            self.current_proxy = random.choice(IPPOOL)
            request.meta['proxy'] = "http://" + self.current_proxy
            request = request.replace(dont_filter=True)
            return request

        # 如果是正常的话，记得最后要返回response
        # 如果不返回，这个response就不会被传到爬虫那里去
        # 也就得不到解析
        return response
    
    # 初始化IP代理池
    def init_proxy(self):
        # 初始化1个IP
        while len(IPPOOL) < 1:
            res = requests.get(self.apiUrl).content.decode()
            # 按照,分割获取到的IP:port
            ipport = res.split(',')[0]
            if(ipport not in IPPOOL):
                IPPOOL.append(ipport)
            time.sleep(1)

    # 更新IP代理池
    def update_proxy(self, delProxy):
        for i, p in enumerate(IPPOOL):      
            if(p in delProxy):
                # 删除失效IP
                IPPOOL.remove(p)
                # 请求新的非重复IP
                found = True
                while(found):
                    res = requests.get(self.apiUrl).content.decode()
                    ipport = res.split(',')[0]
                    if(ipport not in IPPOOL):
                        IPPOOL.append(ipport)
                        found = False

class Uamid(UserAgentMiddleware):
    # 初始化 注意一定要user_agent，不然容易报错   
    def __init__(self, user_agent=''):
        self.user_agent = user_agent
    # 请求处理
    def process_request(self, request, spider):
        # 先随机选择一个用户代理
        thisua = random.choice(UAPOOL)
        print("当前使用User-Agent是："+thisua)
        request.headers.setdefault('User-Agent',thisua)


class ProcessAllExceptionMiddleware(object):
    def __init__(self):
        self.ALL_EXCEPTIONS = (TimeoutError, ConnectionRefusedError, IOError)

    # 生成异常response在IPPOOLS.process_response中处理
    def process_exception(self,request,exception,spider):
        #捕获异常
        # ConnectionRefusedError
        #if isinstance(exception, self.ALL_EXCEPTIONS):#if(exception.osError == 111):
        #在日志中打印异常类型
        print('Got exception: %s' % (exception))
        print('%s代理失效' % request.meta['proxy'])
        response = HtmlResponse(url=request.meta['proxy'])
        response.status = 404
        return response
            #return self._retry(request, exception, spider)
        #打印出未捕获到的异常
        #print('not contained exception: %s'%exception)


class MyfilmSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class MyfilmDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.
    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
