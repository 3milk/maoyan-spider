# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql

#class MyfilmPipeline(object):
#    def process_item(self, item, spider):
#        with open("meiju.txt", 'a') as fp:
#            fp.write(item['fid'] + '\t' + item['name'] + '\t' + item['score'] +
#                '\t' + item['releaseTime'] + '\t' + item['boxOffice'] + 
#                    '\t' + item['country'] + '\t' + item['length'] +
#                        '\t' + item['tags'] + '\t' + item['actors'] + '\n')
        #return item

class MyFilmPipeline(object):
    movieInsert = '''insert into films(fid, name, ename, score, releaseTimeOnlyYear, releaseTime, boxOffice, monetaryUnit, \
        scorePeopleNum, scorePeopleNumUnit, actors, country, tags, length) values \
    ('{fid}','{name}','{ename}','{score}','{releaseTimeOnlyYear}','{releaseTime}','{boxOffice}','{monetaryUnit}',\
        '{scorePeopleNum}','{scorePeopleNumUnit}','{actors}','{country}','{tags}','{length}' )'''

    def process_item(self, item, spider):

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

    def process_item(self, item, spider):

        cid = item['cid']
        sql = 'select * from comments where cid=%s'% cid
        self.cursor.execute(sql)
        results = self.cursor.fetchall()
        if len(results) > 0:
            comment = item['score']
            sql = 'update comments set comment=%s where cid =%s' % (comment, cid)
            self.cursor.execute(sql)
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
