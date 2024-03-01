#!/usr/bin/env python
# Create Schema
import sqlite3

def createSchema():
    cx = sqlite3.connect('db')
    cu = cx.cursor()
    #create
    cu.execute('''create table TB_DATA_SOURCE
    (
      NAME      VARCHAR(255) not null primary key,
      HOST_NAME VARCHAR(255) not null,
      DB_NAME   VARCHAR(255) not null,
      USER_NAME VARCHAR(255) not null,
      PASSWORD  VARCHAR(255) not null,
      PORT      VARCHAR(255) not null,
      DB_TYPE   VARCHAR(255) not null
    )''')
    cu.execute('''create table TB_COMPARED_RESULT
    (
      ID           INTEGER not null primary key AUTOINCREMENT,
      CONTENT      BLOB,
      MEMO         VARCHAR(255),
      CREATED_TIME DATETIME default (datetime('now', 'localtime'))
    )''')
    cu.execute('''create table TB_SQL
    (
      ID           INTEGER not null primary key AUTOINCREMENT,
      SQL          VARCHAR(2000),
      MEMO         VARCHAR(255),
      CREATED_TIME DATETIME default (datetime('now', 'localtime'))
    )''')
    cx.close()

createSchema()
