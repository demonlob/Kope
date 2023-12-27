import os
import re
import textwrap

import aiofiles
import aiohttp
from PIL import (Image, ImageDraw, ImageEnhance, ImageFilter,
                 ImageFont, ImageOps)
from youtubesearchpython.__future__ import VideosSearch

from config import MUSIC_BOT_NAME, YOUTUBE_IMG_URL


def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(widthRatio * image.size[0])
    newHeight = int(heightRatio * image.size[1])
    newImage = image.resize((newWidth, newHeight))
    return newImage



async def gen_thumb(videoid):
    cache_path = f"cache/{videoid}.png"
    os.makedirs("cache", exist_ok=True)

    url = f"https://www.youtube.com/watch?v={videoid}"
    try:
        results = VideosSearch(url, limit=1).result()
        for result in results["result"]:
            title = result.get("title", "Unsupported Title")
            title = re.sub("\W+", " ", title).title()
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            result.get("viewCount", {}).get("short", "Unknown Views")
            result.get("channel", {}).get("name", "Unknown Channel")

        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status == 200:
                    async with aiofiles.open(cache_path, mode="wb") as f:
                        await f.write(await resp.read())

        youtube = Image.open(cache_path)
        image1 = changeImageSize(1280, 720, youtube)
        image2 = image1.convert("RGBA")
        background = image2.filter(filter=ImageFilter.BoxBlur(30))
        enhancer = ImageEnhance.Brightness(background)
        background = enhancer.enhance(0.6)
        Xcenter = youtube.width / 2
        Ycenter = youtube.height / 2
        x1 = Xcenter - 250
        y1 = Ycenter - 250
        x2 = Xcenter + 250
        y2 = Ycenter + 250
        logo = youtube.crop((x1, y1, x2, y2))
        logo.thumbnail((350, 350), Image.LANCZOS)
        logo = ImageOps.expand(logo, border=15, fill="white")
        background.paste(logo, (465, 100))
        draw = ImageDraw.Draw(background)
        font = ImageFont.truetype("assets/font2.ttf", 45)
        ImageFont.truetype("assets/font2.ttf", 70)
        arial = ImageFont.truetype("assets/font2.ttf", 30)
        ImageFont.truetype("assets/font.ttf", 30)
        para = textwrap.wrap(title, width=32)
        if para:
            text_bbox = draw.textbbox((0, 0), para[0], font=font)
            draw.text(
                ((1280 - text_bbox[2]) / 2, 530),
                para[0],
                fill="white",
                stroke_width=1,
                stroke_fill="white",
                font=font,
            )
        if len(para) > 1:
            text_bbox = draw.textbbox((0, 0), para[1], font=font)
            draw.text(
                ((1280 - text_bbox[2]) / 2, 580),
                para[1],
                fill="white",
                stroke_width=1,
                stroke_fill="white",
                font=font,
            )
        text_bbox = draw.textbbox((0, 0), f"Streaming Now", font=arial)
        draw.text(
            ((1280 - text_bbox[2]) / 2, 660), f"Streaming Now", fill="white", font=arial
        )
        background.save(cache_path)
        return cache_path
    except Exception:
        return YOUTUBE_IMG_URL
