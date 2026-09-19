"""把透明底的白字图合成到深色底上，便于人工/多模态检查字形是否正确。

白字在白色预览背景上不可见，必须先合成再检查。

用法: python tools/preview-transparent.py
"""
import os
from PIL import Image

RAW = 'generated-raw'
OUT = 'generated-raw/preview'
ITEMS = ['text-names-v2', 'text-date-v2', 'text-invite-v2']
# 用接近蓝天与深色两种底，分别检查可读性
BACKGROUNDS = {'sky': (74, 150, 200), 'dark': (40, 44, 52)}


def main():
    os.makedirs(OUT, exist_ok=True)
    for name in ITEMS:
        path = os.path.join(RAW, f'{name}.png')
        if not os.path.exists(path):
            print(f'跳过（不存在）: {name}')
            continue
        foreground = Image.open(path).convert('RGBA')
        for label, colour in BACKGROUNDS.items():
            canvas = Image.new('RGBA', foreground.size, colour + (255,))
            canvas.alpha_composite(foreground)
            target = os.path.join(OUT, f'{name}-on-{label}.jpg')
            canvas.convert('RGB').save(target, 'JPEG', quality=90)
        print(f'{name}: 已合成 sky / dark 两种底 -> {OUT}/')


if __name__ == '__main__':
    main()
