import tkinter as tk
from tkinter import font as tkfont
from PIL import Image, ImageTk, ImageDraw, ImageFont
import random
import os
import sys
import time
import json
import winsound
import math

# 경로 설정
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
    local_assets = os.path.join(BASE_DIR, 'assets')
    internal_assets = os.path.join(BASE_DIR, '_internal', 'assets')
    # 실행 파일 옆 assets 폴�더를 최우선으로 사용 (사용자가 쉽게 교체 가능)
    if os.path.exists(local_assets):
        ASSETS_DIR = local_assets
    elif os.path.exists(internal_assets):
        ASSETS_DIR = internal_assets
    else:
        ASSETS_DIR = local_assets
    CONFIG_DIR = BASE_DIR
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
    CONFIG_DIR = BASE_DIR

CONFIG_FILE = os.path.join(CONFIG_DIR, 'settings.json')

# 기본 설정
DEFAULT_CONFIG = {
    "prizes": ["-5%", "Retry", "-50%", "-30%", "Loose", "-5%", "-30%", "-80%"],
    "colors": ["#667eea", "#764ba2", "#f093fb", "#f5576c", "#4facfe", "#00f2fe", "#43e97b", "#38f9d7"],
    "congrats": "축하합니다!",
    "winning_index": -1,
    "winning_slots": [1, 7]
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return DEFAULT_CONFIG.copy()

def save_config(config):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

def apply_circular_mask(img):
    """이미지를 원형으로 마스킹"""
    size = img.size
    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size[0], size[1]), fill=255)
    output = Image.new('RGBA', size, (0, 0, 0, 0))
    output.paste(img, (0, 0), mask)
    return output

def draw_wheel(size, config, angle=0):
    """설정에 따라 룰렛 휠을 그림"""
    prizes = config['prizes']
    colors = config['colors']
    count = len(prizes)
    segment = 360 / count

    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    cx, cy = size // 2, size // 2
    radius = size // 2 - 10

    # 칸 그리기
    for i in range(count):
        start = i * segment - 90
        end = start + segment
        draw.pieslice(
            [cx - radius, cy - radius, cx + radius, cy + radius],
            start, end,
            fill=colors[i % len(colors)],
            outline='white',
            width=3
        )

    # 외곽 점선 테두리
    for a in range(0, 360, 10):
        rad = math.radians(a)
        x1 = cx + (radius - 8) * math.cos(rad)
        y1 = cy + (radius - 8) * math.sin(rad)
        x2 = cx + (radius - 2) * math.cos(rad)
        y2 = cy + (radius - 2) * math.sin(rad)
        draw.line([(x1, y1), (x2, y2)], fill='#ffd700', width=3)

    # 중앙 원
    center_radius = 55
    draw.ellipse(
        [cx - center_radius, cy - center_radius, cx + center_radius, cy + center_radius],
        fill='#2d3436',
        outline='#ffd700',
        width=5
    )

    # 중앙 글씨
    try:
        font_center = ImageFont.truetype("malgun.ttf", 28)
    except Exception:
        font_center = ImageFont.load_default()

    text = "SPIN"
    bbox = draw.textbbox((0, 0), text, font=font_center)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    draw.text((cx - tw/2, cy - th/2 - 5), text, font=font_center, fill='#ffd700', stroke_width=2, stroke_fill='white')

    # 각 칸에 텍스트 그리기
    try:
        font_text = ImageFont.truetype("malgun.ttf", 26)
    except Exception:
        font_text = ImageFont.load_default()

    for i in range(count):
        mid = i * segment + segment / 2 - 90
        rad = math.radians(mid)
        text_radius = radius * 0.62
        tx = cx + text_radius * math.cos(rad)
        ty = cy + text_radius * math.sin(rad)

        txt_img = Image.new('RGBA', (200, 80), (0, 0, 0, 0))
        txt_draw = ImageDraw.Draw(txt_img)
        text = prizes[i]
        bbox = txt_draw.textbbox((0, 0), text, font=font_text)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        txt_draw.text((100 - tw/2, 40 - th/2), text, font=font_text, fill='white', stroke_width=3, stroke_fill='#2d3436')

        rotated = txt_img.rotate(-mid - 90, expand=True)
        rw, rh = rotated.size
        img.paste(rotated, (int(tx - rw/2), int(ty - rh/2)), rotated)

    # 회전 적용
    img = img.rotate(-angle, resample=Image.Resampling.BICUBIC, expand=False)
    return apply_circular_mask(img)

def make_gradient_bg(width, height):
    """럭셔리한 어두운 카지노 스타일 기본 배경"""
    base = Image.new('RGB', (width, height), '#0a0a1a')
    draw = ImageDraw.Draw(base)
    for y in range(height):
        ratio = y / height
        r = int(15 + (35 - 15) * ratio)
        g = int(8 + (15 - 8) * ratio)
        b = int(35 + (60 - 35) * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # 반짝이는 별 효과
    overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    random.seed(42)
    for _ in range(60):
        x = random.randint(0, width)
        y = random.randint(0, height)
        size = random.choice([1, 2, 2, 3])
        alpha = random.choice([60, 100, 140, 180])
        overlay_draw.ellipse([x-size, y-size, x+size, y+size], fill=(255, 215, 0, alpha))

    base = base.convert('RGBA')
    base = Image.alpha_composite(base, overlay)
    return base.convert('RGB')

def draw_luxury_button(text, width, height, font_size=18):
    """럭셔리한 버튼 이미지 생성"""
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    radius = 10
    margin = 2

    # 그림자
    shadow = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle(
        [margin + 3, margin + 3, width - margin, height - margin],
        radius=radius, fill=(0, 0, 0, 100)
    )
    img = Image.alpha_composite(img, shadow)
    draw = ImageDraw.Draw(img)

    # 버튼 본체 그라데이션 (위쪽 밝은 금색, 아래쪽 어두운 금색)
    btn = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    btn_draw = ImageDraw.Draw(btn)
    for y in range(height):
        ratio = y / height
        r = int(255)
        g = int(215 - (150 - 215) * ratio)
        b = int(0 + (30 - 0) * ratio)
        btn_draw.line([(0, y), (width, y)], fill=(r, g, b, 250))

    mask = Image.new('L', (width, height), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle([margin, margin, width - margin, height - margin], radius=radius, fill=255)
    btn.putalpha(mask)
    img = Image.alpha_composite(img, btn)
    draw = ImageDraw.Draw(img)

    # 테두리
    draw.rounded_rectangle([margin, margin, width - margin, height - margin], radius=radius, outline='#ffffff', width=2)

    # 글씨
    try:
        font = ImageFont.truetype("malgun.ttf", font_size)
    except Exception:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    draw.text(((width - tw) / 2, (height - th) / 2 - 3), text, font=font, fill='#2d1b4e',
              stroke_width=1, stroke_fill='white')

    return img

def draw_history_thumbnail(slot_filename, size=40):
    """히스토리용 썸네일: 사진 + 금색 테두리 + 그림자"""
    img = Image.open(slot_filename).convert('RGBA')
    img = img.resize((size, size), Image.Resampling.LANCZOS)

    # 새 캔버스
    canvas_size = size + 8
    result = Image.new('RGBA', (canvas_size, canvas_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(result)

    # 그림자
    draw.rounded_rectangle([4, 4, canvas_size - 2, canvas_size - 2], radius=6, fill=(0, 0, 0, 80))

    # 금색 테두리 배경
    draw.rounded_rectangle([2, 2, canvas_size - 4, canvas_size - 4], radius=6, fill='#ffd700')

    # 사진 붙이기
    result.paste(img, (4, 4), img)

    # 안쪽 하이라이트 선
    draw.rounded_rectangle([4, 4, canvas_size - 4, canvas_size - 4], radius=5, outline=(255, 255, 255, 120), width=1)

    return result

def find_dice_gif():
    """주사위 굴림 GIF 파일이 있으면 경로 반환"""
    candidates = ['dice_roll.gif', 'dice.gif', '주사위.gif']
    for filename in candidates:
        path = os.path.join(ASSETS_DIR, filename)
        if os.path.exists(path):
            return path
    return None

def load_gif_frames(path, width=None, height=None):
    """GIF 파일의 모든 프레임을 추출"""
    frames = []
    try:
        img = Image.open(path)
        for frame in range(img.n_frames):
            img.seek(frame)
            frame_img = img.copy().convert('RGBA')
            if width and height:
                frame_img = frame_img.resize((width, height), Image.Resampling.LANCZOS)
            frames.append(frame_img)
    except Exception:
        pass
    return frames

def find_celebrations():
    """celebration01.gif ~ celebration05.gif 중 존재하는 파일 목록 반환"""
    found = []
    for i in range(1, 6):
        filename = f'celebration{i:02d}.gif'
        path = os.path.join(ASSETS_DIR, filename)
        if os.path.exists(path):
            found.append(filename)
    return found

def get_gif_thumbnail(path, size):
    """GIF 파일의 첫 번째 프레임을 썸네일로 반환"""
    try:
        img = Image.open(path)
        img.seek(0)
        frame = img.copy().convert('RGB')
        frame = frame.resize((size, size), Image.Resampling.LANCZOS)
        return frame
    except Exception:
        return None

def load_background(width, height, filename='background.png'):
    """assets 폴�더에서 지정한 파일을 배경으로 로드, 없으면 그라데이션"""
    bg_path = os.path.join(ASSETS_DIR, filename)
    if os.path.exists(bg_path):
        try:
            img = Image.open(bg_path).convert('RGB')
            img = img.resize((width, height), Image.Resampling.LANCZOS)
            return img
        except Exception:
            pass
    return make_gradient_bg(width, height)

def find_backgrounds():
    """background01.png ~ background10.png 중 존재하는 파일 목록 반환"""
    found = []
    for i in range(1, 11):
        filename = f'background{i:02d}.png'
        path = os.path.join(ASSETS_DIR, filename)
        if os.path.exists(path):
            found.append(filename)
    return found

def draw_result_panel(width, height):
    """상업적 세련된 결과창 패널 이미지 생성"""
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    radius = 20
    margin = 4

    # 그림자
    shadow = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle(
        [margin + 6, margin + 6, width - margin, height - margin],
        radius=radius, fill=(0, 0, 0, 80)
    )
    img = Image.alpha_composite(img, shadow)
    draw = ImageDraw.Draw(img)

    # 메인 본체 그라데이션 (위쪽 별빛 느낌 아래로 어두워짐)
    base = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    base_draw = ImageDraw.Draw(base)
    for y in range(height):
        ratio = y / height
        r = int(45 + (20 - 45) * ratio)
        g = int(15 + (10 - 15) * ratio)
        b = int(70 + (40 - 70) * ratio)
        base_draw.line([(0, y), (width, y)], fill=(r, g, b, 245))

    # 패널 모양 마스크
    mask = Image.new('L', (width, height), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle(
        [margin, margin, width - margin, height - margin],
        radius=radius, fill=255
    )
    base.putalpha(mask)
    img = Image.alpha_composite(img, base)
    draw = ImageDraw.Draw(img)

    # 금색 테두리
    draw.rounded_rectangle(
        [margin, margin, width - margin, height - margin],
        radius=radius, outline='#ffd700', width=4
    )

    # 상단 헤더 영역
    header_height = 46
    header = Image.new('RGBA', (width - margin * 2, header_height), (0, 0, 0, 0))
    header_draw = ImageDraw.Draw(header)
    for y in range(header_height):
        ratio = y / header_height
        r = int(255)
        g = int(215 + (180 - 215) * ratio)
        b = int(0 + (30 - 0) * ratio)
        header_draw.line([(0, y), (width, y)], fill=(r, g, b, 230))

    # 헤더 모서리 둥글게 (위쪽만)
    header_mask = Image.new('L', (width - margin * 2, header_height), 0)
    header_mask_draw = ImageDraw.Draw(header_mask)
    header_mask_draw.rounded_rectangle(
        [0, 0, width - margin * 2, header_height + radius],
        radius=radius, fill=255
    )
    header.putalpha(header_mask)
    img.paste(header, (margin, margin), header)

    # 헤더 구분선
    draw.line([(margin, margin + header_height), (width - margin, margin + header_height)], fill='#ffd700', width=2)

    # RESULT 글씨
    try:
        font_header = ImageFont.truetype("malgun.ttf", 22)
    except Exception:
        font_header = ImageFont.load_default()
    text = "RESULT"
    bbox = draw.textbbox((0, 0), text, font=font_header)
    tw = bbox[2] - bbox[0]
    draw.text(((width - tw) / 2, margin + 10), text, font=font_header, fill='#2d1b4e', stroke_width=1, stroke_fill='white')

    # 반짝이 장식 점들
    random.seed(0)
    for _ in range(30):
        x = random.randint(margin + 10, width - margin - 10)
        y = random.randint(header_height + margin + 10, height - margin - 10)
        size = random.choice([2, 3, 4])
        alpha = random.choice([80, 120, 160, 200])
        draw.ellipse([x - size, y - size, x + size, y + size], fill=(255, 255, 255, alpha))

    return img

def draw_dice(value, size=120):
    """상업적 3D 느낌의 주사위 이미지 생성"""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    margin = 6
    radius = 12
    cx, cy = size // 2, size // 2

    # 그림자
    shadow = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle(
        [margin + 4, margin + 4, size - margin, size - margin],
        radius=radius, fill=(0, 0, 0, 90)
    )
    img = Image.alpha_composite(img, shadow)
    draw = ImageDraw.Draw(img)

    # 주사위 본체 그라데이션 (위쪽 밝게, 아래쪽 어둡게)
    base = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    base_draw = ImageDraw.Draw(base)
    for y in range(size):
        ratio = y / size
        r = int(255 - (60 - 255) * ratio)
        g = int(255 - (40 - 255) * ratio)
        b = int(255 - (90 - 255) * ratio)
        base_draw.line([(0, y), (size, y)], fill=(r, g, b, 250))

    mask = Image.new('L', (size, size), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle(
        [margin, margin, size - margin, size - margin],
        radius=radius, fill=255
    )
    base.putalpha(mask)
    img = Image.alpha_composite(img, base)
    draw = ImageDraw.Draw(img)

    # 금색 테두리
    draw.rounded_rectangle(
        [margin, margin, size - margin, size - margin],
        radius=radius, outline='#ffd700', width=3
    )

    # 하이라이트 (3D 느낌)
    highlight = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    highlight_draw = ImageDraw.Draw(highlight)
    highlight_draw.rounded_rectangle(
        [margin + 4, margin + 4, size - margin - 4, int(size * 0.42)],
        radius=radius - 4, fill=(255, 255, 255, 50)
    )
    img = Image.alpha_composite(img, highlight)
    draw = ImageDraw.Draw(img)

    # 점 위치
    positions = {
        1: [(0.5, 0.5)],
        2: [(0.29, 0.29), (0.71, 0.71)],
        3: [(0.29, 0.29), (0.5, 0.5), (0.71, 0.71)],
        4: [(0.29, 0.29), (0.71, 0.29), (0.29, 0.71), (0.71, 0.71)],
        5: [(0.29, 0.29), (0.71, 0.29), (0.5, 0.5), (0.29, 0.71), (0.71, 0.71)],
        6: [(0.29, 0.29), (0.71, 0.29), (0.29, 0.5), (0.71, 0.5), (0.29, 0.71), (0.71, 0.71)]
    }
    dot_r = size * 0.085
    for px, py in positions.get(value, [(0.5, 0.5)]):
        x = margin + (size - 2 * margin) * px
        y = margin + (size - 2 * margin) * py
        # 점 그림자
        draw.ellipse([x - dot_r + 1, y - dot_r + 1, x + dot_r + 1, y + dot_r + 1], fill=(0, 0, 0, 80))
        # 점 본체 (빨강-금색 그라데이션 느낌)
        draw.ellipse([x - dot_r, y - dot_r, x + dot_r, y + dot_r], fill='#ff0040', outline='#ffd700', width=2)

    return img

def draw_dice_question(size=120):
    """물음표 주사위 (굴리는 중)"""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    margin = 6
    radius = 12

    # 그림자
    shadow = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle(
        [margin + 4, margin + 4, size - margin, size - margin],
        radius=radius, fill=(0, 0, 0, 90)
    )
    img = Image.alpha_composite(img, shadow)
    draw = ImageDraw.Draw(img)

    base = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    base_draw = ImageDraw.Draw(base)
    for y in range(size):
        ratio = y / size
        r = int(80 - (30 - 80) * ratio)
        g = int(30 - (10 - 30) * ratio)
        b = int(100 - (50 - 100) * ratio)
        base_draw.line([(0, y), (size, y)], fill=(r, g, b, 250))

    mask = Image.new('L', (size, size), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle([margin, margin, size - margin, size - margin], radius=radius, fill=255)
    base.putalpha(mask)
    img = Image.alpha_composite(img, base)
    draw = ImageDraw.Draw(img)

    draw.rounded_rectangle([margin, margin, size - margin, size - margin], radius=radius, outline='#ffd700', width=3)

    try:
        font = ImageFont.truetype("malgun.ttf", int(size * 0.5))
    except Exception:
        font = ImageFont.load_default()
    text = "?"
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    draw.text(((size - tw) / 2, (size - th) / 2 - 5), text, font=font, fill='#ffd700', stroke_width=2, stroke_fill='white')
    return img

class RouletteGame:
    def __init__(self, root):
        self.root = root
        self.root.title('제비뽑기 룰렛')
        self.root.geometry('1400x720')
        self.root.configure(bg='#0a0a1a')
        self.root.resizable(False, False)

        self.config = load_config()

        # 폰트
        self.title_font = tkfont.Font(family='Malgun Gothic', size=32, weight='bold')
        self.value_font = tkfont.Font(family='Malgun Gothic', size=22, weight='bold')
        self.desc_font = tkfont.Font(family='Malgun Gothic', size=13, weight='bold')
        self.header_font = tkfont.Font(family='Malgun Gothic', size=30, weight='bold')
        self.small_font = tkfont.Font(family='Malgun Gothic', size=14, weight='bold')
        self.slot_num_font = tkfont.Font(family='Malgun Gothic', size=12, weight='bold')

        # 캔버스
        self.canvas = tk.Canvas(root, width=1400, height=720, bg='#0a0a1a', highlightthickness=0)
        self.canvas.pack()

        # 배경 이미지 (assets/background.png 우선 사용)
        self.bg_image = ImageTk.PhotoImage(load_background(1400, 720))
        self.bg_canvas_id = self.canvas.create_image(0, 0, image=self.bg_image, anchor='nw')

        # 배경 썸네일 버튼들
        self.bg_thumb_tks = []
        self.bg_buttons = []
        bg_files = find_backgrounds()
        thumb_size = 14
        start_x = 20
        start_y = 680
        gap = 18
        for i, bg_file in enumerate(bg_files):
            x = start_x + i * gap
            img = Image.open(os.path.join(ASSETS_DIR, bg_file)).convert('RGB')
            img = img.resize((thumb_size, thumb_size), Image.Resampling.LANCZOS)
            tk_img = ImageTk.PhotoImage(img)
            self.bg_thumb_tks.append(tk_img)
            btn = tk.Button(root, image=tk_img, width=thumb_size, height=thumb_size,
                            bg='#0a0a1a', activebackground='#ffd700', relief='flat',
                            command=lambda f=bg_file: self.change_background(f))
            self.bg_buttons.append(btn)
            self.canvas.create_window(x, start_y, window=btn, anchor='nw')

        # 기본 그라데이션 버튼
        default_img = make_gradient_bg(thumb_size, thumb_size)
        default_tk = ImageTk.PhotoImage(default_img)
        self.bg_thumb_tks.append(default_tk)
        default_btn = tk.Button(root, image=default_tk, width=thumb_size, height=thumb_size,
                                bg='#0a0a1a', activebackground='#ffd700', relief='flat',
                                command=lambda: self.change_background(''))
        self.bg_buttons.append(default_btn)
        self.canvas.create_window(start_x + len(bg_files) * gap, start_y, window=default_btn, anchor='nw')

        # 축하 GIF 썸네일 버튼들 (배경 썸네일 아래)
        self.celeb_files = find_celebrations()
        self.selected_celebration = self.celeb_files[0] if self.celeb_files else ''
        self.celeb_thumb_tks = []
        self.celeb_buttons = []
        celeb_start_y = start_y + 18
        for i, celeb_file in enumerate(self.celeb_files):
            x = start_x + i * gap
            thumb = get_gif_thumbnail(os.path.join(ASSETS_DIR, celeb_file), thumb_size)
            if thumb:
                tk_img = ImageTk.PhotoImage(thumb)
            else:
                tk_img = default_tk
            self.celeb_thumb_tks.append(tk_img)
            btn = tk.Button(root, image=tk_img, width=thumb_size, height=thumb_size,
                            bg='#0a0a1a', activebackground='#ffd700', relief='flat',
                            highlightbackground='#ffd700', highlightthickness=0,
                            command=lambda f=celeb_file, idx=i: self.select_celebration(f, idx))
            self.celeb_buttons.append(btn)
            self.canvas.create_window(x, celeb_start_y, window=btn, anchor='nw')

        # 기본 폭죽 효과 버튼
        confetti_img = Image.new('RGB', (thumb_size, thumb_size), '#0a0a1a')
        confetti_draw = ImageDraw.Draw(confetti_img)
        for _ in range(8):
            cx = random.randint(3, thumb_size - 3)
            cy = random.randint(3, thumb_size - 3)
            confetti_draw.ellipse([cx-2, cy-2, cx+2, cy+2], fill=random.choice(['#ffd700', '#ff006e', '#00f2fe', '#43e97b']))
        confetti_tk = ImageTk.PhotoImage(confetti_img)
        self.celeb_thumb_tks.append(confetti_tk)
        confetti_btn = tk.Button(root, image=confetti_tk, width=thumb_size, height=thumb_size,
                                 bg='#0a0a1a', activebackground='#ffd700', relief='flat',
                                 highlightbackground='#ffd700', highlightthickness=0,
                                 command=lambda: self.select_celebration('', len(self.celeb_files)))
        self.celeb_buttons.append(confetti_btn)
        self.canvas.create_window(start_x + len(self.celeb_files) * gap, celeb_start_y, window=confetti_btn, anchor='nw')

        # 초기 선택 표시
        if self.celeb_files:
            self.select_celebration(self.celeb_files[0], 0)
        else:
            self.select_celebration('', 0)

        # 제목 (금색 + 그림자)
        self.canvas.create_text(702, 42, text='제비뽑기 룰렛', font=self.header_font, fill='#2d1b4e')
        self.canvas.create_text(700, 40, text='제비뽑기 룰렛', font=self.header_font, fill='#ffd700')

        # 왼쪽 여자 이미지 (금색 테두리 프레임)
        self.girl_frame = ImageTk.PhotoImage(self.draw_rounded_frame(310, 430, 20, '#ffd700', 4))
        self.canvas.create_image(150, 360, image=self.girl_frame, anchor='center')
        self.girl_img = self.load_girl_image('girl.png', 300, 420)
        self.girl_canvas_id = self.canvas.create_image(150, 360, image=self.girl_img, anchor='center')

        # 룰렛 휠 (금색 글로우 링)
        self.wheel_glow = ImageTk.PhotoImage(self.draw_wheel_glow(520))
        self.canvas.create_image(480, 360, image=self.wheel_glow, anchor='center')

        self.wheel_size = 480
        self.wheel_source = draw_wheel(self.wheel_size, self.config, angle=0)
        self.wheel_img = ImageTk.PhotoImage(self.wheel_source)
        self.wheel_id = self.canvas.create_image(480, 360, image=self.wheel_img, anchor='center')

        # 화살표 (룰렛 가장자리에 맞춤)
        arrow_tip_y = 360 - (self.wheel_size // 2 - 10) - 12
        self.canvas.create_polygon([480, arrow_tip_y, 460, arrow_tip_y + 45, 500, arrow_tip_y + 45],
                                   fill='#ffd700', outline='#ffffff', width=2)

        # 슬롯
        self.slot_images = []
        self.slots = []
        slot_size = 120
        gap = 20
        start_x = 980
        start_y = 80
        cols = 3

        # 슬롯 프레임 생성 (슬롯보다 10px 큰 둥근 금색 테두리)
        self.slot_frame = ImageTk.PhotoImage(self.draw_rounded_frame(slot_size + 12, slot_size + 12, 12, '#ffd700', 3))

        for i in range(12):
            row = i // cols
            col = i % cols
            x = start_x + col * (slot_size + gap)
            y = start_y + row * (slot_size + gap)
            # 금색 테두리 프레임
            frame_id = self.canvas.create_image(x + slot_size/2, y + slot_size/2, image=self.slot_frame, anchor='center')
            img = self.load_image(f'slot{i+1:02d}.png', slot_size, slot_size)
            self.slot_images.append(img)
            slot_id = self.canvas.create_image(x, y, image=img, anchor='nw')
            self.slots.append({'id': slot_id, 'frame_id': frame_id, 'x': x, 'y': y, 'size': slot_size, 'index': i+1})
            self.canvas.tag_bind(slot_id, '<Button-1>', lambda e, idx=i+1: self.on_slot_click(idx))
            self.canvas.create_text(x + slot_size/2, y + slot_size + 14, text=str(i+1), font=self.slot_num_font, fill='#ffd700')

        # 결과 영역 (상업적 세련된 패널 이미지)
        panel_width = 200
        panel_height = 530
        self.result_panel_img_tk = ImageTk.PhotoImage(draw_result_panel(panel_width, panel_height))
        self.result_panel_id = self.canvas.create_image(700, 75, image=self.result_panel_img_tk, anchor='nw')

        self.result_title = self.canvas.create_text(790, 110, text='You won', font=self.title_font, fill='#ffd700')
        self.result_value = self.canvas.create_text(790, 165, text='???', font=self.value_font, fill='white', width=160)
        self.result_desc = self.canvas.create_text(790, 220, text='오른쪽 사진을 클릭하세요', font=self.desc_font, fill='#cccccc', width=160)

        # 주사위 이미지 (룰렛 결과 옆 작게)
        self.dice_source = draw_dice_question(55)
        self.dice_img_tk = ImageTk.PhotoImage(self.dice_source)
        self.dice_img_id = self.canvas.create_image(745, 165, image=self.dice_img_tk, anchor='center')

        # 결과 히스토리 라벨
        self.canvas.create_text(745, 265, text='DICE', font=self.desc_font, fill='#ffd700')
        self.canvas.create_text(835, 265, text='ROULETTE', font=self.desc_font, fill='#ffd700')

        # 결과 히스토리 (세로로 최대 10개, 주사위 왼쪽/룰렛 오른쪽)
        self.dice_history = []
        self.roulette_history = []
        self.dice_history_ids = []
        self.roulette_history_ids = []
        self.dice_history_tks = []
        start_y = 285
        spacing = 36
        for i in range(10):
            y = start_y + i * spacing
            dice_id = self.canvas.create_image(745, y, image='', anchor='center')
            roulette_id = self.canvas.create_text(835, y, text='', font=self.small_font, fill='white', width=80, anchor='center')
            self.dice_history_ids.append(dice_id)
            self.roulette_history_ids.append(roulette_id)
            self.dice_history_tks.append(None)

        # 버튼들 (럭셔리 이미지 버튼)
        self.spin_btn_tk = ImageTk.PhotoImage(draw_luxury_button('돌리기', 120, 45, 16))
        self.spin_btn = tk.Button(root, image=self.spin_btn_tk, bg='#0a0a1a', activebackground='#0a0a1a',
                                  relief='flat', bd=0, command=self.on_spin_click)
        self.canvas.create_window(730, 630, window=self.spin_btn)

        self.dice_btn_tk = ImageTk.PhotoImage(draw_luxury_button('주사위 굴리기', 140, 45, 15))
        self.dice_btn = tk.Button(root, image=self.dice_btn_tk, bg='#0a0a1a', activebackground='#0a0a1a',
                                  relief='flat', bd=0, command=self.on_dice_click)
        self.canvas.create_window(850, 630, window=self.dice_btn)

        self.settings_btn_tk = ImageTk.PhotoImage(draw_luxury_button('룰렛 글씨 설정', 160, 45, 15))
        self.settings_btn = tk.Button(root, image=self.settings_btn_tk, bg='#0a0a1a', activebackground='#0a0a1a',
                                      relief='flat', bd=0, command=self.open_settings)
        self.canvas.create_window(790, 690, window=self.settings_btn)

        # 상태
        self.is_spinning = False
        self.dice_animating = False
        self.current_angle = 0
        self.target_angle = 0
        self.anim_start = 0
        self.anim_duration = 3000
        self.selected_slot = 0
        self.last_tick_angle = 0
        self.dice_value = 1
        self.dice_anim_start = 0
        self.dice_final_slot = 0
        self.dice_gif_frames = []
        self.dice_gif_label = None
        self.dice_gif_id = None
        self.dice_gif_index = 0
        self.dice_gif_path = find_dice_gif()
        self.celebrating = False
        self.confetti = []
        self.gif_celeb_id = None
        self.gif_celeb_label = None
        self.gif_celeb_frames = []
        self.gif_celeb_index = 0

    def change_background(self, filename):
        new_bg = ImageTk.PhotoImage(load_background(1400, 720, filename if filename else 'background.png'))
        self.bg_image = new_bg
        self.canvas.itemconfig(self.bg_canvas_id, image=self.bg_image)

    def select_celebration(self, filename, selected_index):
        """축하 효과 GIF 선택 및 썸네일 강조 표시"""
        self.selected_celebration = filename
        for i, btn in enumerate(self.celeb_buttons):
            if i == selected_index:
                btn.config(bg='#ffd700', highlightthickness=2)
            else:
                btn.config(bg='#0a0a1a', highlightthickness=0)

    def draw_rounded_frame(self, width, height, radius, color, border_width):
        """둥근 모서리 금색 테두리 프레임"""
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        # 그림자
        shadow = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow)
        shadow_draw.rounded_rectangle(
            [6, 6, width - 2, height - 2], radius=radius, fill=(0, 0, 0, 80)
        )
        img = Image.alpha_composite(img, shadow)
        draw = ImageDraw.Draw(img)
        # 테두리
        draw.rounded_rectangle(
            [2, 2, width - 2, height - 2], radius=radius, outline=color, width=border_width
        )
        # 안쪽 하이라이트
        draw.rounded_rectangle(
            [4, 4, width - 4, height - 4], radius=radius - 2, outline=(255, 255, 255, 120), width=1
        )
        return img

    def draw_wheel_glow(self, size):
        """룰렛 주변 금색 글로우 링"""
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        cx, cy = size // 2, size // 2
        outer = size // 2 - 5
        inner = size // 2 - 25
        for r in range(outer, inner, -1):
            alpha = int(60 * (outer - r) / (outer - inner))
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(255, 215, 0, alpha), width=2)
        return img

    def load_image(self, filename, width, height):
        path = os.path.join(ASSETS_DIR, filename)
        img = Image.open(path).convert('RGBA')
        img = img.resize((width, height), Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(img)

    def load_girl_image(self, filename, width, height):
        """왼쪽 여자 이미지 로드 (없으면 기본 girl.png 사용)"""
        path = os.path.join(ASSETS_DIR, filename)
        if not os.path.exists(path):
            path = os.path.join(ASSETS_DIR, 'girl.png')
        img = Image.open(path).convert('RGBA')
        img = img.resize((width, height), Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(img)

    def update_girl_image(self, prize_index):
        """룰렛 결과(0~7)에 따라 왼쪽 여자 이미지 교체"""
        filename = f'girl_{prize_index + 1:02d}.png'
        self.girl_img = self.load_girl_image(filename, 300, 420)
        self.canvas.itemconfig(self.girl_canvas_id, image=self.girl_img)

    def redraw_wheel(self):
        self.wheel_source = draw_wheel(self.wheel_size, self.config, angle=self.current_angle)
        self.wheel_img = ImageTk.PhotoImage(self.wheel_source)
        self.canvas.itemconfig(self.wheel_id, image=self.wheel_img)

    def rotate_wheel(self, angle):
        rotated = draw_wheel(self.wheel_size, self.config, angle=angle)
        self.wheel_img = ImageTk.PhotoImage(rotated)
        self.canvas.itemconfig(self.wheel_id, image=self.wheel_img)

    def play_tick(self):
        try:
            winsound.Beep(700, 40)
        except Exception:
            pass

    def play_win_melody(self, note_index=0):
        notes = [523, 659, 784, 1047]
        durations = [150, 150, 150, 400]
        if note_index < len(notes):
            try:
                winsound.Beep(notes[note_index], durations[note_index])
            except Exception:
                pass
            self.root.after(durations[note_index] + 50, lambda: self.play_win_melody(note_index + 1))

    def play_jackpot_melody(self, note_index=0):
        """당첨 잭팟 소리 (더 화려한 멜로디)"""
        notes = [523, 659, 784, 1047, 1319, 1047, 1319, 1568, 2093]
        durations = [120, 120, 120, 200, 120, 120, 120, 200, 600]
        if note_index < len(notes):
            try:
                winsound.Beep(notes[note_index], durations[note_index])
            except Exception:
                pass
            self.root.after(durations[note_index] + 50, lambda: self.play_jackpot_melody(note_index + 1))

    def is_jackpot(self, prize_index, slot_index=None):
        """해당 인덱스가 당첨 칸인지 확인 (룰렛 칸 또는 슬롯 번호)"""
        # 룰렛 칸 기준 당첨
        winning_index = self.config.get('winning_index', -1)
        if 0 <= winning_index < len(self.config['prizes']):
            if prize_index == winning_index:
                return True
        else:
            # 설정이 -1이면 '당첨' 글씨가 있는 칸을 자동으로 당첨으로 인식
            prize_text = self.config['prizes'][prize_index]
            if '당첨' in prize_text or 'JACKPOT' in prize_text.upper():
                return True
        # 슬롯 번호 기준 당첨 (1번, 7번 등)
        winning_slots = self.config.get('winning_slots', [])
        if slot_index is not None and slot_index in winning_slots:
            return True
        return False

    def on_slot_click(self, slot_index):
        if self.is_spinning:
            return
        self.selected_slot = slot_index
        self.start_spin()

    def on_spin_click(self):
        if self.is_spinning:
            return
        self.selected_slot = random.randint(1, 12)
        self.start_spin()

    @staticmethod
    def ease_out_cubic(t):
        return 1 - pow(1 - t, 3)

    def start_spin(self):
        self.is_spinning = True
        self.last_tick_angle = 0
        self.canvas.itemconfig(self.result_title, text='돌림판을 돌리는 중...')
        self.canvas.itemconfig(self.result_value, text='')
        self.canvas.itemconfig(self.result_desc, text='잠시만 기다려주세요')

        count = len(self.config['prizes'])
        segment = 360 / count
        target_segment = (self.selected_slot - 1) % count
        # 화살표가 항상 당첨 칸의 정중앙을 가리키도록 절대 각도로 계산
        # 룰렛 회전 방향과 화살표 방향을 맞춤
        angle_end = (-(target_segment * segment + segment / 2)) % 360
        full_rotations = int(self.current_angle // 360) + 5
        self.target_angle = full_rotations * 360 + angle_end
        self.anim_start = time.time() * 1000
        self.animate()

    def animate(self):
        now = time.time() * 1000
        elapsed = now - self.anim_start
        progress = min(elapsed / self.anim_duration, 1.0)
        eased = self.ease_out_cubic(progress)
        angle = self.current_angle + (self.target_angle - self.current_angle) * eased
        self.rotate_wheel(angle)

        if abs(angle - self.last_tick_angle) >= 30:
            self.play_tick()
            self.last_tick_angle = angle

        if progress < 1.0:
            self.root.after(16, self.animate)
        else:
            self.current_angle = self.target_angle % 360
            self.is_spinning = False
            self.show_result()

    def show_celebration(self):
        """당첨 축하 효과: GIF 있으면 GIF 재생, 없으면 폭죽 효과"""
        if self.celebrating:
            return
        self.celebrating = True

        gif_path = os.path.join(ASSETS_DIR, self.selected_celebration) if self.selected_celebration else ''
        if gif_path and os.path.exists(gif_path):
            frames = load_gif_frames(gif_path, 220, 220)
            if frames:
                self.gif_celeb_frames = [ImageTk.PhotoImage(f) for f in frames]
                self.gif_celeb_label = tk.Label(self.root, image=self.gif_celeb_frames[0], bg='#0a0a1a')
                self.gif_celeb_id = self.canvas.create_window(790, 220, window=self.gif_celeb_label)
                self.animate_gif_celebration(0)
                self.root.after(2500, self.stop_celebration)
                return

        self.show_confetti_celebration()

    def animate_gif_celebration(self, index):
        if not self.celebrating or not self.gif_celeb_frames:
            return
        self.gif_celeb_index = index % len(self.gif_celeb_frames)
        self.gif_celeb_label.config(image=self.gif_celeb_frames[self.gif_celeb_index])
        self.root.after(80, lambda: self.animate_gif_celebration(index + 1))

    def show_confetti_celebration(self):
        """코드로 만든 폭죽 축하 효과"""
        colors = ['#ffd700', '#ff006e', '#00f2fe', '#43e97b', '#ffffff', '#ff8c00']
        for _ in range(60):
            x = random.randint(680, 900)
            y = random.randint(40, 180)
            size = random.randint(4, 10)
            color = random.choice(colors)
            speed = random.randint(3, 9)
            angle = random.randint(0, 360)
            item = self.canvas.create_polygon(
                [x, y, x + size, y, x + size, y + size, x, y + size],
                fill=color, outline=''
            )
            self.confetti.append({
                'id': item, 'x': x, 'y': y, 'size': size,
                'speed': speed, 'angle': angle
            })
        self.animate_confetti(0)

    def animate_confetti(self, frame):
        if frame > 45:
            self.stop_celebration()
            return
        for c in self.confetti:
            c['y'] += c['speed']
            c['angle'] += 12
            s = c['size']
            rad = math.radians(c['angle'])
            cos = math.cos(rad)
            sin = math.sin(rad)
            cx = c['x'] + s / 2
            cy = c['y'] + s / 2
            points = []
            for px, py in [(-s / 2, -s / 2), (s / 2, -s / 2), (s / 2, s / 2), (-s / 2, s / 2)]:
                rx = cx + px * cos - py * sin
                ry = cy + px * sin + py * cos
                points.extend([rx, ry])
            self.canvas.coords(c['id'], *points)
        self.root.after(45, lambda: self.animate_confetti(frame + 1))

    def stop_celebration(self):
        for c in self.confetti:
            self.canvas.delete(c['id'])
        self.confetti = []
        if self.gif_celeb_id:
            self.canvas.delete(self.gif_celeb_id)
            self.gif_celeb_id = None
            self.gif_celeb_label = None
            self.gif_celeb_frames = []
        self.celebrating = False

    def highlight_slot(self, index):
        """당첨 슬롯 주위에 금색 테두리 하이라이트 (1.5초 유지)"""
        for slot in self.slots:
            if slot['index'] == index:
                x, y, size = slot['x'], slot['y'], slot['size']
                # 바깥쪽 흰색 글로우
                glow = self.canvas.create_rectangle(x-8, y-8, x+size+8, y+size+8, outline='white', width=2)
                # 안쪽 금색 테두리
                rect = self.canvas.create_rectangle(x-5, y-5, x+size+5, y+size+5, outline='#ffd700', width=5)
                self.root.after(1500, lambda g=glow, r=rect: (self.canvas.delete(g), self.canvas.delete(r)))
                break

    def show_result(self):
        count = len(self.config['prizes'])
        segment = 360 / count
        # 화살표가 실제로 가리키는 칸 인덱스 계산
        angle = self.current_angle % 360
        prize_index = int(((360 - angle) % 360) // segment) % count
        prize_text = self.config['prizes'][prize_index]
        congrats = self.config['congrats']

        self.canvas.itemconfig(self.result_title, text=congrats)
        self.canvas.itemconfig(self.result_value, text=prize_text)
        self.canvas.itemconfig(self.result_desc, text=f'룰렛 선택 슬롯: {self.selected_slot}번')

        # 왼쪽 여자 이미지를 결과에 맞게 교체
        self.update_girl_image(prize_index)

        # 룰렛 히스토리에 추가 (최대 10개 유지)
        self.roulette_history.append(prize_text)
        if len(self.roulette_history) > 10:
            self.roulette_history.pop(0)

        # 룰렛 결과일 때 주사위 이미지는 물음표로, 히스토리는 유지
        self.update_dice_image('?')
        self.update_histories()

        if self.is_jackpot(prize_index, self.selected_slot):
            self.canvas.itemconfig(self.result_title, text='JACKPOT!')
            self.play_jackpot_melody()
        else:
            self.play_win_melody()
        self.highlight_slot(self.selected_slot)
        self.show_celebration()

    def on_dice_click(self):
        if self.is_spinning or self.dice_animating:
            return
        self.dice_animating = True
        self.canvas.itemconfig(self.result_title, text='주사위를 굴리는 중...')
        self.canvas.itemconfig(self.result_value, text='')
        self.canvas.itemconfig(self.result_desc, text='잠시만 기다려주세요')
        self.dice_final_slot = 0

        # GIF 주사위가 있으면 GIF 재생
        if self.dice_gif_path:
            self.dice_value = random.randint(1, 6)
            self.play_dice_gif()
        else:
            self.dice_anim_start = time.time() * 1000
            self.animate_dice()

    def play_dice_gif(self):
        """주사위 굴림 GIF 재생 후 결과 눈 표시"""
        frames = load_gif_frames(self.dice_gif_path, 55, 55)
        if not frames:
            self.dice_anim_start = time.time() * 1000
            self.animate_dice()
            return

        self.dice_gif_frames = [ImageTk.PhotoImage(f) for f in frames]
        self.canvas.itemconfig(self.dice_img_id, image='')
        self.dice_gif_label = tk.Label(self.root, image=self.dice_gif_frames[0], bg='#0a0a1a')
        self.dice_gif_id = self.canvas.create_window(745, 165, window=self.dice_gif_label)
        self.dice_gif_index = 0
        self.animate_dice_gif(0)

    def animate_dice_gif(self, index):
        if not self.dice_animating:
            return
        self.dice_gif_index = index % len(self.dice_gif_frames)
        self.dice_gif_label.config(image=self.dice_gif_frames[self.dice_gif_index])
        self.play_tick()
        if index < len(self.dice_gif_frames) * 2 - 1:
            self.root.after(60, lambda: self.animate_dice_gif(index + 1))
        else:
            self.root.after(200, self.finish_dice_gif)

    def finish_dice_gif(self):
        if self.dice_gif_id:
            self.canvas.delete(self.dice_gif_id)
            self.dice_gif_id = None
            self.dice_gif_label = None
        self.update_dice_image(self.dice_value)
        self.dice_animating = False
        self.show_dice_result()

    def animate_dice(self):
        now = time.time() * 1000
        elapsed = now - self.dice_anim_start
        if elapsed < 1500:
            value = random.randint(1, 6)
            self.update_dice_image(value)
            self.play_tick()
            self.root.after(80, self.animate_dice)
        else:
            self.dice_value = random.randint(1, 6)
            self.update_dice_image(self.dice_value)
            self.dice_animating = False
            self.show_dice_result()

    def update_dice_image(self, value):
        if value == '?' or value is None:
            source = draw_dice_question(55)
        else:
            source = draw_dice(value, 55)
        self.dice_img_tk = ImageTk.PhotoImage(source)
        self.canvas.itemconfig(self.dice_img_id, image=self.dice_img_tk)

    def update_histories(self):
        # 주사위 히스토리 이미지를 위에서부터 최신 순으로 표시
        for i in range(10):
            idx = len(self.dice_history) - 1 - i
            if idx >= 0:
                slot = self.dice_history[idx]
                slot_filename = f'slot{slot:02d}.png'
                img = draw_history_thumbnail(os.path.join(ASSETS_DIR, slot_filename), 36)
                self.dice_history_tks[i] = ImageTk.PhotoImage(img)
                self.canvas.itemconfig(self.dice_history_ids[i], image=self.dice_history_tks[i])
            else:
                self.dice_history_tks[i] = None
                self.canvas.itemconfig(self.dice_history_ids[i], image='')

        # 룰렛 히스토리 글씨를 위에서부터 최신 순으로 표시
        for i in range(10):
            idx = len(self.roulette_history) - 1 - i
            if idx >= 0:
                text = self.roulette_history[idx]
                self.canvas.itemconfig(self.roulette_history_ids[i], text=text)
            else:
                self.canvas.itemconfig(self.roulette_history_ids[i], text='')

    def show_dice_result(self):
        # 주사위 1~6에 따라 (n, n+6) 중 랜덤 선택
        candidates = [self.dice_value, self.dice_value + 6]
        self.dice_final_slot = random.choice(candidates)
        self.selected_slot = self.dice_final_slot

        count = len(self.config['prizes'])
        prize_index = (self.dice_final_slot - 1) % count
        prize_text = self.config['prizes'][prize_index]
        congrats = self.config['congrats']

        self.canvas.itemconfig(self.result_title, text=congrats)
        self.canvas.itemconfig(self.result_value, text=prize_text)
        self.canvas.itemconfig(self.result_desc, text=f'주사위: {self.dice_value}점\n선택된 슬롯: {self.dice_final_slot}번')

        # 왼쪽 여자 이미지를 결과에 맞게 교체
        self.update_girl_image(prize_index)

        # 주사위 히스토리에 추가 (최대 10개 유지)
        self.dice_history.append(self.dice_final_slot)
        if len(self.dice_history) > 10:
            self.dice_history.pop(0)
        self.update_histories()

        if self.is_jackpot(prize_index, self.dice_final_slot):
            self.canvas.itemconfig(self.result_title, text='JACKPOT!')
            self.play_jackpot_melody()
        else:
            self.play_win_melody()
        self.highlight_slot(self.dice_final_slot)
        self.show_celebration()

    def open_settings(self):
        settings_window = tk.Toplevel(self.root)
        settings_window.title('룰렛 글씨 설정')
        settings_window.geometry('550x700')
        settings_window.configure(bg='#1a0f2e')
        settings_window.resizable(False, False)
        settings_window.grab_set()

        tk.Label(settings_window, text='룰렛 각 칸에 표시할 글씨를 입력하세요', bg='#1a0f2e', fg='#ffd700',
                 font=('Malgun Gothic', 14, 'bold')).pack(pady=10)

        entries = []
        prizes = self.config['prizes']
        for i in range(8):
            frame = tk.Frame(settings_window, bg='#1a0f2e')
            frame.pack(pady=5)
            tk.Label(frame, text=f'{i+1}번 칸:', bg='#1a0f2e', fg='white', font=('Malgun Gothic', 12), width=10).pack(side='left')
            entry = tk.Entry(frame, font=('Malgun Gothic', 12), width=25, bg='#2d1b4e', fg='white', insertbackground='white')
            entry.insert(0, prizes[i] if i < len(prizes) else '')
            entry.pack(side='left')
            entries.append(entry)

        tk.Label(settings_window, text='축하 메시지:', bg='#1a0f2e', fg='white', font=('Malgun Gothic', 12)).pack(pady=(15, 5))
        congrats_entry = tk.Entry(settings_window, font=('Malgun Gothic', 12), width=35, bg='#2d1b4e', fg='white', insertbackground='white')
        congrats_entry.insert(0, self.config.get('congrats', '축하합니다!'))
        congrats_entry.pack()

        tk.Label(settings_window, text='당첨 칸 (0=자동, 1~8=해당 칸):', bg='#1a0f2e', fg='white', font=('Malgun Gothic', 12)).pack(pady=(15, 5))
        winning_var = tk.StringVar(value=str(self.config.get('winning_index', -1) + 1))
        winning_spin = tk.Spinbox(settings_window, from_=0, to=8, textvariable=winning_var, font=('Malgun Gothic', 12), width=10, bg='#2d1b4e', fg='white')
        winning_spin.pack()
        tk.Label(settings_window, text='0으로 두면 "당첨" 또는 "JACKPOT" 글씨가 있는 칸을 자동으로 당첨으로 인식', bg='#1a0f2e', fg='#cccccc', font=('Malgun Gothic', 10)).pack(pady=(2, 0))

        tk.Label(settings_window, text='당첨 슬롯 (1~12, 쉼표로 구분):', bg='#1a0f2e', fg='white', font=('Malgun Gothic', 12)).pack(pady=(15, 5))
        winning_slots_entry = tk.Entry(settings_window, font=('Malgun Gothic', 12), width=35, bg='#2d1b4e', fg='white', insertbackground='white')
        winning_slots = self.config.get('winning_slots', [1, 7])
        winning_slots_entry.insert(0, ', '.join(str(s) for s in winning_slots))
        winning_slots_entry.pack()
        tk.Label(settings_window, text='예: 1, 7  →  오른쪽 1번과 7번 슬롯이 당첨 슬롯이 됩니다', bg='#1a0f2e', fg='#cccccc', font=('Malgun Gothic', 10)).pack(pady=(2, 0))

        def save_and_close():
            new_prizes = [entry.get() for entry in entries]
            self.config['prizes'] = new_prizes
            self.config['congrats'] = congrats_entry.get()
            try:
                self.config['winning_index'] = int(winning_var.get()) - 1
            except Exception:
                self.config['winning_index'] = -1
            # 당첨 슬롯 파싱
            try:
                slots_text = winning_slots_entry.get()
                slots = [int(s.strip()) for s in slots_text.split(',') if s.strip()]
                self.config['winning_slots'] = slots
            except Exception:
                self.config['winning_slots'] = [1, 7]
            save_config(self.config)
            self.redraw_wheel()
            settings_window.destroy()

        save_btn = tk.Button(settings_window, text='저장', font=('Malgun Gothic', 12),
                             bg='#ffd700', fg='#2d1b4e', activebackground='#ffec8b',
                             command=save_and_close)
        save_btn.pack(pady=20)

if __name__ == '__main__':
    root = tk.Tk()
    app = RouletteGame(root)
    root.mainloop()
