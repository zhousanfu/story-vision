#!python3.10
# coding=utf-8
'''
 Author: Sanfor Chow
 Date: 2024-03-13 09:27:10
 LastEditors: Sanfor Chow
 LastEditTime: 2024-03-13 10:36:32
 FilePath: /story-vision/txt.py
'''
import re, os, time, json
import requests
import parsel
from tqdm import tqdm



headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
}

book_id = 7207072067127086118
url = f'https://fanqienovel.com/page/{str(book_id)}'
response = requests.get(url=url, headers=headers)
html_data = response.text

name = re.findall('<div class="info-name"><h1>(.*?)</h1', html_data)[0]
selector = parsel.Selector(html_data)
css_name = selector.css('.info-name h1::text').get()
href = selector.css('.chapter-item a::attr(href)').getall()
print(f'{name}, 小说正在下载, 请稍后....')
if not os.path.exists(f'data/txt/{name}'):
    os.makedirs(f'data/txt/{name}')
else:
    print("文件夹已经存在")
for index in tqdm(href):
    chapter_id = index.split('/')[-1]
    link = f'https://novel.snssdk.com/api/novel/book/reader/full/v1/?device_platform=android&parent_enterfrom=novel_channel_search.tab.&aid=2329&platform_id=1&group_id={chapter_id}&item_id={chapter_id}'
    time.sleep(30)
    res = requests.get(url=link, headers=headers)
    print(res.status_code, res, link)
    json_data = res.json()['data']['content']
    title = re.findall('<div class="tt-title">(.*?)</div>', json_data)[0]
    content = '\n'.join(re.findall('<p>(.*?)</p>', json_data))
    with open(f'data/txt/{name}/{title}.json', "w", encoding='utf-8') as json_file:
        json.dump({'title':title,  'content':content}, json_file, ensure_ascii=False)
    time.sleep(120)