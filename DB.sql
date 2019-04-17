CREATE DATABASE if not exists myFilms DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;

use myFilms;

CREATE TABLE if not exists `films` (
    `fid` int PRIMARY KEY COMMENT 'film id',
    `name` varchar(256) NOT NULL COMMENT 'Chinese name for the film',
    `ename` varchar(256) COMMENT 'foreign name for the film',
    `score` float(3,1) COMMENT 'score of the film, such as 9.0; some films do not have score, for these films, the score is -1',
    `releaseTimeOnlyYear` BOOLEAN COMMENT 'if release time just precise on year, this field is set true',
    `releaseTime` date COMMENT 'release time',
    `boxOffice` int COMMENT 'box Office, unit is WAN',
    `monetaryUnit` varchar(32) COMMENT 'RMB DOLLARS ...',
    `scorePeopleNum` float(8,2) COMMENT 'score people number',
    `scorePeopleNumUnit` BOOLEAN default 0 COMMENT 'score people number unit, 1 for WAN, 0 for nothing',
    `actors` text COMMENT 'actor and actress list, split by ,',
    `country` varchar(256) COMMENT 'country or countries, list split by ,',
    `tags` varchar(256) COMMENT 'TAGs, list split by ,',
    `length` smallint COMMENT 'length of film, unit is minute',
    `poster` varchar(256) COMMENT 'origin poster URL, by adding width and height param to change the size'
);

CREATE TABLE if not exists `comments` (
    `cid` int PRIMARY KEY COMMENT 'comment id',
    `fid` int COMMENT 'film id',
    `score` float(2,1) NOT NULL COMMENT 'score',
    `comment` text NOT NULL COMMENT 'comment',
    `liked` int NOT NULL COMMENT 'comment liked number',
    `commentTime` timestamp NOT NULL COMMENT 'comment time'
);