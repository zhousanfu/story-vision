#!python3.10
# coding=utf-8
'''
 Author: Sanfor Chow
 Date: 2024-02-01 00:13:38
 LastEditors: Sanfor Chow
 LastEditTime: 2024-04-15 22:10:14
 FilePath: /story-vision/my_lls.py
'''
import os
import datetime
from tqdm import tqdm
import google.generativeai as genai
from openai import OpenAI
from typing import Dict, List, Optional, Tuple, Union
from langchain.llms.base import LLM
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from config import read_config



cfg = read_config()
client = OpenAI(
    api_key = cfg['openai_api_key'],
    base_url = cfg["openai_url"]
)
ai_max_length = 1000

class OpenAI_LLM(LLM):
    model_type: str = "openai"

    def __init__(self):
        super().__init__()

    @property
    def _llm_type(self) -> str:
        return "openai"
    
    def _call(self, prompt: str, history: List = [], stop: Optional[List[str]] = None) -> str:
        res = gpt_35_api(prompt)
        return res
            
    @property
    def _identifying_params(self):
        """Get the identifying parameters.
        """
        return {"model": self.model_type}

def split_text_into_chunks(text, max_length=ai_max_length):
    """
    Split text into chunks with a maximum length, ensuring that splits only occur at line breaks.
    """
    lines = text.splitlines()
    chunks = []
    current_chunk = ''
    for line in lines:
        if len(current_chunk + ' ' + line) <= max_length:
            current_chunk += ' ' + line
        else:
            chunks.append(current_chunk)
            current_chunk = line
    chunks.append(current_chunk)
    return chunks

def rewrite_text_with_genai(text, prompt="Please rewrite this text:"):
    chunks = split_text_into_chunks(text)
    rewritten_text = ''
    # pbar = tqdm(total=len(chunks), ncols=150)
    genai.configure(api_key=cfg['genai_api_key'])
    model = genai.GenerativeModel('gemini-pro')
    for chunk in chunks:
        _prompt=f"{prompt}\n{chunk}",
        response = model.generate_content(
            contents=_prompt, 
            generation_config=genai.GenerationConfig(
                temperature=0.1,
            ),
            stream=True,
            safety_settings = [
                {
                    "category": "HARM_CATEGORY_DANGEROUS",
                    "threshold": "BLOCK_NONE",
                },
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_NONE",
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_NONE",
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_NONE",
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_NONE",
                },
            ]
        )
        for _chunk in response:
            if _chunk.text is not None:
                rewritten_text += _chunk.text.strip()
    #     pbar.update(1)
    # pbar.close()
    return rewritten_text

def gpt_35_api(prompt, model="gpt-3.5-turbo"):
    """为提供的对话消息创建新的回答
    Args:
        messages (list): 完整的对话消息
    """
    messages = [{"role": "user", "content": prompt}]
    response = client.chat.completions.create(model=model, messages=messages)
    print(response)
    return response.choices[0].message.content

def gpt_35_api_stream(prompt, model="gpt-3.5-turbo"):
    """为提供的对话消息创建新的回答 (流式传输)
    Args:
        messages (list): 完整的对话消息
    """
    messages = [{"role": "user", "content": prompt}]
    stream = client.chat.completions.create(
        model=model,
        messages=messages,
        stream=True,
    )
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            print(chunk.choices[0].delta.content, end="")

def get_completion(prompt, model="gpt-3.5-turbo"):
    '''
    prompt: 对应的提示词
    model: 调用的模型，默认为 gpt-3.5-turbo(ChatGPT)，有内测资格的用户可以选择 gpt-4
    '''
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0, # 模型输出的温度系数，控制输出的随机程度
    )
    return response.choices[0].message["content"]

def story_board(text):
    template = cfg["fj_prompt"] + "{my_text}"
    prompt = PromptTemplate(input_variables=["my_text"], template=template)

    llm = OpenAI_LLM()
    llm_chain = LLMChain(llm=llm, prompt=prompt)
    res = llm_chain.run({"my_text": text})
    return res

def illu_stration(text):
    template = cfg["sd_prompt"] + "{my_text}"
    prompt = PromptTemplate(input_variables=["my_text"], template=template)

    llm = OpenAI_LLM()
    llm_chain = LLMChain(llm=llm, prompt=prompt)
    res = llm_chain.run({"my_text": text})
    return res

def story_board_for_genai(text):
    res = rewrite_text_with_genai(text=text, prompt=cfg["fj_prompt"])
    return res

def illu_stration_for_genai(text):
    res = rewrite_text_with_genai(text=text, prompt=cfg["sd_prompt"])
    return res


if __name__ == '__main__':
    # res = story_board(text="这是洛野第一次来派出所。\n还是被抓来的。\n全程一脸懵逼，洛野在家里打游戏，突然两个警察走了进来，和善的给他戴上了手铐，邀请他坐警车自驾游去派出所。")

    # res = illu_stration(text='插画一：原文描述：洛野一脸懵逼地被警察带到警察局的审讯室。 "姓名。" “洛野。” 画面描述：洛野坐在审讯室的椅子上，警察小哥哥拿着资料看着他，面部表情严肃。 画面角色：洛野、警察小哥哥 穿着：洛野穿着便装，警察小哥哥穿着制服。 位置：坐在审讯室的椅子上。 表情：警察小哥哥表情严肃，洛野一脸懵逼。 行为：警察小哥哥拿着资料询问洛野。 环境：审讯室的背景是简洁的墙壁和桌椅，给人一种紧张的氛围。')

    template = cfg["fj_prompt"] + "{my_text}"
    prompt = PromptTemplate(input_variables=["my_text"], template=template)
    # res = rewrite_text_with_genai(text='插画一：原文描述：洛野一脸懵逼地被警察带到警察局的审讯室。 "姓名。" “洛野。” 画面描述：洛野坐在审讯室的椅子上，警察小哥哥拿着资料看着他，面部表情严肃。 画面角色：洛野、警察小哥哥 穿着：洛野穿着便装，警察小哥哥穿着制服。 位置：坐在审讯室的椅子上。 表情：警察小哥哥表情严肃，洛野一脸懵逼。 行为：警察小哥哥拿着资料询问洛野。 环境：审讯室的背景是简洁的墙壁和桌椅，给人一种紧张的氛围。', prompt=prompt)
    # print(res)
    print(prompt)