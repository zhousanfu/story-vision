#!python3.10
# coding=utf-8
'''
 Author: Sanfor Chow
 Date: 2024-04-15 23:08:48
 LastEditors: Sanfor Chow
 LastEditTime: 2024-04-15 23:16:26
 FilePath: /story-vision/test.py
'''
import codecs



def replace_non_gb2312(string):
    def __is_gb2312_char(char):
        try:
            char.encode('gb2312')
            return True
        except UnicodeEncodeError:
            return False

    replaced_string = ""
    for char in string:
        if __is_gb2312_char(char):
            replaced_string += char
        else:
            replaced_string += "."
    return replaced_string

string1 = "这个时间顾明轩应该在⻜机上"
string2 = "这个时间顾明轩应该在飞机上"

replaced_string1 = replace_non_gb2312(string1)
replaced_string2 = replace_non_gb2312(string2)

print("替换后字符串1:", replaced_string1)
print("替换后字符串2:", replaced_string2)