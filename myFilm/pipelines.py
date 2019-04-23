# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
from myFilm.items import MyFilmItem, MyCommentItem

class MyFilmPipeline(object):
    movieInsert = '''insert into films(fid, name, ename, score, releaseTimeOnlyYear, releaseTime, boxOffice, monetaryUnit, \
        scorePeopleNum, scorePeopleNumUnit, actors, country, tags, length, poster) values \
    ('{fid}','{name}','{ename}','{score}','{releaseTimeOnlyYear}','{releaseTime}','{boxOffice}','{monetaryUnit}',\
        '{scorePeopleNum}','{scorePeopleNumUnit}','{actors}','{country}','{tags}','{length}','{poster}' )'''

    def process_item(self, item, spider):
        if not isinstance(item, MyFilmItem):
            return item
        fid = item['fid']
        sql = 'select * from films where fid=%s'% fid
        self.cursor.execute(sql)
        results = self.cursor.fetchall()
        if len(results) > 0:
            score = item['score']
            boxOffice=item['boxOffice']
            scorePeopleNum=item['scorePeopleNum']
            scorePeopleNumUnit=item['scorePeopleNumUnit']
            sql = 'update films set score=%f, boxOffice=%d, scorePeopleNum=%d, scorePeopleNumUnit=%d \
                where fid =%s' % (score, boxOffice, scorePeopleNum, scorePeopleNumUnit, fid)
            self.cursor.execute(sql)
        else:
            sqlinsert = self.movieInsert.format(
                fid=item['fid'],
                name=pymysql.escape_string(item['name']),
                ename=pymysql.escape_string(item['ename']),
                score=item['score'],
                releaseTimeOnlyYear=item.get('releaseTimeOnlyYear'),
                releaseTime=item.get('releaseTime'),
                boxOffice=item['boxOffice'],
                monetaryUnit=item['monetaryUnit'],
                scorePeopleNum=item['scorePeopleNum'],
                scorePeopleNumUnit=item['scorePeopleNumUnit'],
                actors=pymysql.escape_string(item.get('actors')),
                country=pymysql.escape_string(item.get('country')),
                tags=pymysql.escape_string(item.get('tags')),
                length=item['length'],
                poster=pymysql.escape_string(item.get('poster'))
            )
            self.cursor.execute(sqlinsert)
        return item

    def open_spider(self, spider):
        config = {
          'host':'127.0.0.1',
          'port':3306,
          'user':'root',
          'password':'root',
          'database':'myFilms',
          'charset':'utf8',
          'use_unicode':True,
          }
        self.connect = pymysql.connect(**config)
        self.cursor = self.connect.cursor()
        self.connect.autocommit(True)

    def close_spider(self, spider):
        self.cursor.close()
        self.connect.close()

class MyCommentPipeline(object):
    commentInsert = '''insert into comments(cid, fid, score, comment, liked, commentTime) values \
    ('{cid}','{fid}','{score}','{comment}','{liked}','{commentTime}')'''
    commentUpdate = '''update comments set comment='{comm}' where cid ={cid}'''

    def process_item(self, item, spider):
        if not isinstance(item, MyCommentItem):
            return item
        cid = item['cid']
        sql = 'select * from comments where cid=%d'% cid
        self.cursor.execute(sql)
        results = self.cursor.fetchall()
        if len(results) > 0:
            sqlUpdate = self.commentUpdate.format(
                cid = item['cid'],
                comm=pymysql.escape_string(item['comment'])
            )
            self.cursor.execute(sqlUpdate)
        else:
            sqlinsert = self.commentInsert.format(
                cid=item['cid'],
                fid=item['fid'],
                score=item['score'],
                comment=pymysql.escape_string(item['comment']),
                liked=item['liked'],
                commentTime=item.get('commentTime')
            )
            self.cursor.execute(sqlinsert)
        return item

    def open_spider(self, spider):
        config = {
          'host':'127.0.0.1',
          'port':3306,
          'user':'root',
          'password':'root',
          'database':'myFilms',
          'charset':'utf8',
          'use_unicode':True,
          }
        self.connect = pymysql.connect(**config)
        self.cursor = self.connect.cursor()
        self.connect.autocommit(True)

    def close_spider(self, spider):
        self.cursor.close()
        self.connect.close()
