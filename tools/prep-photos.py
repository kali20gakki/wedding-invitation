"""把选中的原片缩小到 API 处理用的尺寸，并转成便于上传的 JPEG。

原片是 4672x7008 / 6772x4515 的大图（9~19MB），直接上传会很慢。
统一缩到长边 3200px、质量 92，肉眼无损但体积降到 1~3MB。

用法: python tools/prep-photos.py
"""
import os
from PIL import Image

SRC = 'raw-photos'
OUT = 'generated-raw/photo-src'

# 选中的原片 -> 输出名
PICKS = {
    '微信图片_20260919201848_15_8.jpg': 'couple-umbrella.jpg',   # p1 户外撑伞
    '微信图片_20260919201928_19_8.jpg': 'couple-arch.jpg',       # p5 横版拱廊
    '微信图片_20260919201907_17_8.jpg': 'couple-door.jpg',       # p3 室内木门
}
MAX_EDGE = 3200


def main():
    os.makedirs(OUT, exist_ok=True)
    for src_name, out_name in PICKS.items():
        path = os.path.join(SRC, src_name)
        if not os.path.exists(path):
            print(f'跳过（不存在）: {src_name}')
            continue
        image = Image.open(path).convert('RGB')
        width, height = image.size
        if max(width, height) > MAX_EDGE:
            scale = MAX_EDGE / max(width, height)
            image = image.resize((round(width * scale), round(height * scale)), Image.LANCZOS)
        target = os.path.join(OUT, out_name)
        image.save(target, 'JPEG', quality=92, optimize=True)
        size_mb = os.path.getsize(target) / 1024 / 1024
        print(f'{out_name:<24} {width}x{height} -> {image.size[0]}x{image.size[1]}  {size_mb:.2f} MB')


if __name__ == '__main__':
    main()
