#!python3.10
# coding=utf-8
'''
 Author: Sanfor Chow
 Date: 2024-03-12 12:44:43
 LastEditors: Sanfor Chow
 LastEditTime: 2024-03-12 12:45:45
 FilePath: /story-vision/config.py
'''
import configparser



def read_config():
    file = 'config.ini'
    con = configparser.ConfigParser()
    con.read(file, encoding='utf-8')
    sections = con.sections()
    items = con.items('main')
    items = dict(items)
    return items