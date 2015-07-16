# -*-coding: utf-8 -*-


import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter


def randchr():
    return chr(random.randint(65, 90))


def randcolor():
    return (random.randint(64, 255),
            random.randint(64, 255),
            random.randint(64, 255))


def randcolor2():
    return (random.randint(32, 127),
            random.randint(32, 127),
            random.randint(32, 127))


FONT_FILE = '/usr/share/fonts/truetype/ubuntu-font-family/Ubuntu-B.ttf'


def validcode(w=240, h=60):
    img = Image.new('RGB', [w, h])
    font = ImageFont.truetype(FONT_FILE, 36)
    draw = ImageDraw.Draw(img)

    for x in range(w):
        for y in range(h):
            draw.point((x, y), fill=randcolor())

    for x in range(4):
        draw.text((h * x + 10, 10), randchr(), font=font, fill=randcolor2())

    # img = img.filter(ImageFilter.BLUR)
    img.save('validcode.jpg', 'jpeg')

if __name__ == '__main__':
    validcode()
