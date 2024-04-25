#!python3.10
# coding=utf-8
'''
 Author: Sanfor Chow
 Date: 2024-03-13 08:47:59
 LastEditors: Sanfor Chow
 LastEditTime: 2024-04-25 16:26:48
 FilePath: /story-vision/main.py
'''
import os
import re
import cv2
import json
import time
import asyncio
import numpy as np
from tqdm import tqdm
from pydub import AudioSegment
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips
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
        match = [item.replace('*', '').strip() for item in match if item.strip()]
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
    with open(file_path, "r") as json_file:
        data = json.load(json_file)
    json_file.close()

    if 'illu_stration' not in data.keys():
        con = 0
        data['illu_stration'] = []
        storys = story_board_for_genai(text=data['content'])
        storys = structure_extraction(storys)
        for s in storys:
            con += 1
            text = ''
            for k,v in s.items():
                text += k + ':' + v + '\n'
            illu = illu_stration_for_genai(text=text)
            time.sleep(3)
            data['illu_stration'].append({'id': con, 'story': s, 'illu': illu})
        
        content = replace_non_gb2312(data['content'])
        illu_stration = []
        for i in data['illu_stration']:
            pattern = r'.*?' + replace_non_gb2312(i['story']['原文描述'])
            try:
                matches = re.findall(pattern, content, flags=re.DOTALL)
            except:
                matches = []
            if len(matches) == 0:
                pattern = r'.*?'+i['story']['原文描述'].split("，")[0]
                try:
                    matches = re.findall(pattern, content, flags=re.DOTALL)
                except:
                    matches = []
            try:
                content = re.sub(pattern, '', content, flags=re.DOTALL)
            except:
                pass
            i['原文'] = matches
            try:
                i['story']['原文描述'] = matches[0]
            except IndexError:
                pass
            illu_stration.append(i)
        data['illu_stration'] = illu_stration

        with open(file_path, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)
        json_file.close()

def story_sd(file_path):
    file_name = file_path.split('/')[-1].split('.')[0]

    with open(file_path, "r") as json_file:
        data = json.load(json_file)
    json_file.close()

    if 'illu_stration' in data.keys():
        for i in data['illu_stration']:
            if os.path.exists('/content/drive/MyDrive/Data/img/'+file_name+'_'+str(i['id'])+'.jpg'):
                pass
            else:
                sd_cetus(save_name=file_name+'_'+str(i['id']), prompt=i['illu'])

def story_tts(file_path):
    with open(file_path, "r") as json_file:
        data = json.load(json_file)
    json_file.close()

    file_name = file_path.split('/')[-1].split('.')[0]

    if 'illu_stration' in data.keys():
        for i in data['illu_stration']:
            if len(i['原文']) > 0:
                asyncio.run(tts_function(save_name=file_name+'_'+str(i['id']), text=i['原文'][0]))
            else:
                asyncio.run(tts_function(save_name=file_name+'_'+str(i['id']), text=i['story']['原文描述'][0]))

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
    base_path = r'data/txt/学姐别怕，我来保护你'
    files = os.listdir(base_path)
    files.sort(key=lambda x: int(x.split('.')[0]))

    pbar = tqdm(total=len(files))
    for path in files:
        file_path = os.path.join(base_path, path)
        story_llm(file_path)
        pbar.update(1)
    pbar.close()

    pbar = tqdm(total=len(files))
    for path in files:
        file_path = os.path.join(base_path, path)
        story_sd(file_path)
        pbar.update(1)
    pbar.close()

    pbar = tqdm(total=len(files))
    for path in files:
        file_path = os.path.join(base_path, path)
        story_tts(file_path)
        pbar.update(1)
    pbar.close()

    pbar = tqdm(total=len(files))
    for path in files:
        file_path = os.path.join(base_path, path)
        stitch_videos(file_path)
        pbar.update(1)
    pbar.close()

    clips = []
    base_path = r'data/video'
    files = os.listdir(base_path)
    files.sort(key=lambda x: int(x.split('第')[1].split('章')[0]))
    for path in files:
        if '_out' in path:
            full_path = os.path.join(base_path, path)
            clip = VideoFileClip(full_path)
            clips.append(clip)
    
    final_clip = concatenate_videoclips(clips)
    final_clip.write_videofile("data/video/merged_video.mp4")