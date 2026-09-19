"""裁掉透明文字图四周的多余留白，只保留文字本体加少量边距。

生成出来的文字图留白很大（透明像素占 90%+），直接用会导致定位困难。
问题：alpha 通道有极淡的扩散像素（alpha 1~20）铺满整张图，
直接 getbbox() 会得到整张图，所以先按阈值过滤再求包围盒。

用法: python tools/trim-text.py
"""
import os
from PIL import Image

ITEMS = [
    ('text-names', 0.06), ('text-invite', 0.06), ('text-date', 0.08),
    ('text-names-v2', 0.06), ('text-invite-v2', 0.06), ('text-date-v2', 0.08),
    ('text-invite-v3', 0.06),
]
RAW = 'generated-raw'
ALPHA_THRESHOLD = 40


def main():
    for name, pad in ITEMS:
        path = os.path.join(RAW, f'{name}.png')
        image = Image.open(path)
        if image.mode != 'RGBA':
            print(f'{name}: 无 alpha 通道，跳过')
            continue
        alpha = image.getchannel('A')
        # 阈值过滤：低于阈值的视为背景，置 0 后求包围盒
        mask = alpha.point(lambda value: 255 if value >= ALPHA_THRESHOLD else 0)
        box = mask.getbbox()
        if not box:
            print(f'{name}: 未找到有效文字区域，跳过')
            continue
        left, top, right, bottom = box
        margin = round(max(right - left, bottom - top) * pad)
        crop = (max(0, left - margin), max(0, top - margin),
                min(image.width, right + margin), min(image.height, bottom + margin))
        cropped = image.crop(crop)
        cropped.save(path, 'PNG')
        print(f'{name}: {image.size} -> {cropped.size}  宽高比={cropped.width / cropped.height:.2f}')


if __name__ == '__main__':
    main()
