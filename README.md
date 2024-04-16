<!--
 * @Author: Sanfor Chow
 * @Date: 2024-01-31 03:53:52
 * @LastEditors: Sanfor Chow
 * @LastEditTime: 2024-04-16 17:46:07
 * @FilePath: /story-vision/README.md
-->

# 功能设计
总体>main.py
1、提取分镜场景: 小说文本分句、SD生成图片和TTS文本转语音(带时间)
2、小说内容>推导提示词(SD绘画)
3、图片音频合并视频

模型:
TTS(edge)、SD绘画模型(这里使用:cetusMix_Whalefall2)、GPT(这里使用Gemini)

# 后续改进
SD人物保持一致role
视频合并时画面转变效果、字幕等