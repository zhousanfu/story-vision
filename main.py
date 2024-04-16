#!python3.10
# coding=utf-8
'''
 Author: Sanfor Chow
 Date: 2024-03-13 08:47:59
 LastEditors: Sanfor Chow
 LastEditTime: 2024-04-16 17:39:49
 FilePath: /story-vision/main.py
'''
import re
import cv2
import json
import time
import asyncio
import numpy as np
from pydub import AudioSegment
from moviepy.editor import VideoFileClip, AudioFileClip
from my_lls import story_board, illu_stration, story_board_for_genai, illu_stration_for_genai
from my_sd import sd_cetus
from my_tts import tts_function



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

def structure_extraction(text):
    pattern = r'(原文描述|画面描述)：(.*?)。|(画面角色|穿着|位置|表情|行为)：(.*?)(\n|$)'
    matches = re.findall(pattern, text, re.MULTILINE)

    character_list = []
    character = {"原文描述": [], "画面描述": [], "画面角色": [], "穿着": [], "位置": [], "表情": [], "行为": []}
    for match in matches:
        match = [item.strip() for item in match if item.strip()]
        character[match[0]].append(match[1])
    
    result = [dict(zip(character.keys(), values)) for values in zip(*character.values())]
    return result

def get_audio_duration(audio_file):
    audio = AudioSegment.from_file(audio_file)
    duration = len(audio) / 1000  # 将毫秒转换为秒
    return duration

def merge_audio(audio_files):
    merged_audio = None
    for audio_file in audio_files:
        audio = AudioSegment.from_file(audio_file)
        if merged_audio is None:
            merged_audio = audio
        else:
            merged_audio += audio
    return merged_audio

def story_llm(file_path):
    con = 0

    with open(file_path, "r") as json_file:
        data = json.load(json_file)
    json_file.close()

    data['illu_stration'] = []
    storys = story_board_for_genai(text=data['content'])
    storys = structure_extraction(storys)
    for s in storys:
        con += 1
        text = ''
        for k,v in s.items():
            text += k + ':' + v + '\n'
        illu = illu_stration_for_genai(text=text)
        data['illu_stration'].append({'id': con, 'story': s, 'illu': illu})
    
    content = replace_non_gb2312(data['content'])
    illu_stration = []
    for i in data['illu_stration']:
        pattern = r'.*?' + replace_non_gb2312(i['story']['原文描述'])
        matches = re.findall(pattern, content, flags=re.DOTALL)
        if len(matches) == 0:
            pattern = r'.*?'+i['story']['原文描述'].split("，")[0]
            matches = re.findall(pattern, content, flags=re.DOTALL)
        content = re.sub(pattern, '', content, flags=re.DOTALL)
        i['story']['原文描述'] = matches[0]
        illu_stration.append(i)
    data['illu_stration'] = illu_stration

    with open(file_path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)
    json_file.close()

def story_sd(file_path):
    with open(file_path, "r") as json_file:
        data = json.load(json_file)
    json_file.close()

    file_name = file_path.split('/')[-1].split('.')[0]
    for i in data['illu_stration']:
        sd_cetus(save_name=file_name+'_'+str(i['id']), prompt=i['illu'])

def story_tts(file_path):
    with open(file_path, "r") as json_file:
        data = json.load(json_file)
    json_file.close()

    file_name = file_path.split('/')[-1].split('.')[0]
    for i in data['illu_stration']:
        asyncio.run(tts_function(save_name=file_name+'_'+str(i['id']), text=i['原文'][0]))

def stitch_videos(file_path):
    fps = 25  # 设置视频帧率
    width, height = 640, 480  # 自定义视频大小
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # 设置视频编码器
    img_li = []
    vie_li = []

    with open(file_path, "r") as json_file:
        data = json.load(json_file)
    json_file.close()

    file_name = file_path.split('/')[-1].split('.')[0]
    for i in data['illu_stration']:
        img_li.append('data/img/' + file_name+'_'+str(i['id']) + '.jpg')
        vie_li.append('data/voice/' + file_name+'_'+str(i['id']) + '.wav')

    # 生成视频
    video_writer = cv2.VideoWriter('data/video/'+file_name+'.mp4', fourcc, fps, (width, height))
    for i, audio in enumerate(vie_li):
        print(img_li[i], audio)
        image = cv2.imread(img_li[i])
        image = cv2.resize(image, (width, height))

        audio_durations = get_audio_duration(audio)
        frame_count = int(audio_durations * fps)

        for _ in range(frame_count):
            video_writer.write(image)
    video_writer.release()
    cv2.destroyAllWindows()

    # 合并音频
    merged_audio = merge_audio(vie_li)
    merged_audio.export('data/voice/'+file_name+'.mp3', format="mp3")

    # 加载视频和音频文件
    video_clip = VideoFileClip('data/video/'+file_name+'.mp4')
    audio_clip = AudioFileClip('data/voice/'+file_name+'.mp3')
    
    # 将音频与视频的持续时间对齐
    audio_clip = audio_clip.set_duration(video_clip.duration)
    
    # 将音频与视频合并
    video_clip = video_clip.set_audio(audio_clip)
    
    # 保存合并后的视频文件
    video_clip.write_videofile('data/video/'+file_name+'_out.mp4', codec="libx264", audio_codec="aac")



if __name__ == '__main__':
    story_llm(file_path="data/txt/学姐别怕，我来保护你/第1章 进局子了.json")
    # story_sd(file_path="data/txt/学姐别怕，我来保护你/第1章 进局子了.json")
    # story_tts(file_path="data/txt/学姐别怕，我来保护你/第1章 进局子了.json")
    # stitch_videos(file_path="data/txt/学姐别怕，我来保护你/第1章 进局子了.json")