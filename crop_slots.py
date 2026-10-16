from PIL import Image
import os

img = Image.open(r'C:\Users\Lucky\.verdent\storage\profiles\prod-s1\workspaces\new-project-1--proj_2ad219c8dd8e2cda\shared\blobs\sha256\eb\f6\ebf67384a0349539869f2a67c4ab37f0b2b6d9870ace2d6caef2a044529a388b')
w, h = img.size
cols = 4
rows = 3
cw = w // cols
ch = h // rows
outdir = r'C:\Users\Lucky\Desktop\제비뽑기\assets'
os.makedirs(outdir, exist_ok=True)

idx = 1
for row in range(rows):
    for col in range(cols):
        left = col * cw
        top = row * ch
        right = (col + 1) * cw if col < cols - 1 else w
        bottom = (row + 1) * ch if row < rows - 1 else h
        crop = img.crop((left, top, right, bottom))
        crop.save(os.path.join(outdir, f'slot{idx:02d}.png'))
        idx += 1

print('done', w, h)
