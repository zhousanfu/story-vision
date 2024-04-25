#!python3.10
# coding=utf-8
'''
 Author: Sanfor Chow
 Date: 2024-02-01 00:39:32
 LastEditors: Sanfor Chow
 LastEditTime: 2024-04-23 14:23:31
 FilePath: /story-vision/my_sd.py
'''
from diffusers import StableDiffusionPipeline
from diffusers.utils import load_image
import torch


def sd_cetus(save_name, prompt):
    model_path = "./models/cetusMix_Whalefall2.safetensors"

    pipeline = StableDiffusionPipeline.from_single_file(
        model_path,
        torch_dtype=torch.float16,
        variant="fp16"
        ).to("mps")
    generator = torch.Generator("mps").manual_seed(31)

    prompt = prompt
    image = pipeline(prompt, height=512, width=768, generator=generator).images[0]
    image.save('data/img/'+ save_name +'.jpg')