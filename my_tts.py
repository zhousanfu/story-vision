#!python3.10
# coding=utf-8
'''
 Author: Sanfor Chow
 Date: 2024-01-31 03:48:40
 LastEditors: Sanfor Chow
 LastEditTime: 2024-04-16 16:31:42
 FilePath: /story-vision/my_tts.py
'''
import edge_tts
import asyncio



voice = 'zh-CN-YunxiNeural'
output = 'data/voice/'
rate = '-4%'
volume = '+0%'

async def tts_function(text, save_name):
    tts = edge_tts.Communicate(
        text,
        voice=voice,
        rate=rate,
        volume=volume
        )
    await tts.save(output + save_name + '.wav')