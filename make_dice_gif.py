import os
from PIL import Image, ImageDraw

def create_dice_gif(path, size=100):
    positions = {
        1: [(0.5, 0.5)],
        2: [(0.29, 0.29), (0.71, 0.71)],
        3: [(0.29, 0.29), (0.5, 0.5), (0.71, 0.71)],
        4: [(0.29, 0.29), (0.71, 0.29), (0.29, 0.71), (0.71, 0.71)],
        5: [(0.29, 0.29), (0.71, 0.29), (0.5, 0.5), (0.29, 0.71), (0.71, 0.71)],
        6: [(0.29, 0.29), (0.71, 0.29), (0.29, 0.5), (0.71, 0.5), (0.29, 0.71), (0.71, 0.71)]
    }
    bg = '#0a0a1a'
    frames = []
    for i, value in enumerate([1, 2, 3, 4, 5, 6]):
        img = Image.new('RGB', (size, size), bg)
        draw = ImageDraw.Draw(img)
        margin = 8
        radius = 12
        # 그림자
        draw.rounded_rectangle([margin + 4, margin + 4, size - margin, size - margin], radius=radius, fill=(20, 20, 40))
        # 본체
        draw.rounded_rectangle([margin, margin, size - margin, size - margin], radius=radius, fill='white', outline='#ffd700', width=3)
        # 점
        dot_r = size * 0.085
        for px, py in positions[value]:
            x = margin + (size - 2 * margin) * px
            y = margin + (size - 2 * margin) * py
            draw.ellipse([x - dot_r, y - dot_r, x + dot_r, y + dot_r], fill='black')
        # 회전
        img = img.rotate(i * 12, resample=Image.Resampling.BICUBIC, expand=False, fillcolor=bg)
        frames.append(img)
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=120, loop=0)

create_dice_gif(r'C:\Users\Lucky\Desktop\제비뽑기2\assets\dice_roll.gif', 100)
print('주사위 GIF 생성 완료')
