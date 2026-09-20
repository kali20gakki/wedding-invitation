"""
把真实婚纱照（婚礼照片/*.jpg）转成网页用的 WebP，供「风车邮局来信」轮播使用。

⚠️ 这里**不做任何风格转换** —— 新人明确要求用原图风格。
   只做两件事：等比缩小 + 转 WebP 压缩。

选片（按画面内容挑三张，形成"由外到内、由动到静"的节奏）：
  couple-umbrella  林间各自撑伞相望        ← 4969
  couple-veil      古门前共读、新郎掀纱     ← 4971
  couple-window    拱窗前的新娘剪影         ← 4973

用法: python tools/build-wedding-photos.py
"""
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / '婚礼照片'
OUT = ROOT / 'assets'

# (源图的照片编号, 目标文件名)
# 用照片自身的编号（微信导出文件名里 _4969_ 这一段）来定位，不要用排序序号 ——
# 按序号写太容易错位：sorted 之后第 6 张是 _4969_，第 8 张才是 _4971_。
# 编号 → 画面内容的对应关系逐张看过图确认过：
#   4969 林间两把透明伞相望      4971 古门前掀纱（烛台）      4973 拱窗前新娘剪影
PICKS = [
    ('4969', 'couple-umbrella.webp'),  # 林间各自撑伞相望
    ('4971', 'couple-veil.webp'),      # 古门前共读、新郎为新娘掀纱
    ('4973', 'couple-window.webp'),    # 拱窗前的新娘剪影
]


def find_by_serial(files, serial):
    for path in files:
        # 微信导出名形如 微信图片_20260921003954_4968_3.jpg
        if f'_{serial}_' in path.name:
            return path
    raise SystemExit(f'没找到编号为 {serial} 的照片')

# 卡片最多显示 320px 宽、4:3 横版；竖版原图会被裁切，
# 所以素材按"高度"留足：目标长边 1440px，@2x 屏也够。
MAX_SIDE = 1440
QUALITY = 82


def main() -> None:
    files = sorted(SRC.glob('*.jpg'))
    if not files:
        raise SystemExit(f'没找到婚纱照：{SRC}')

    total = 0
    for serial, name in PICKS:
        src = find_by_serial(files, serial)
        image = ImageOps.exif_transpose(Image.open(src)).convert('RGB')
        before = image.size
        # 等比缩到长边 MAX_SIDE
        image.thumbnail((MAX_SIDE, MAX_SIDE), Image.LANCZOS)
        dst = OUT / name
        image.save(dst, format='WEBP', quality=QUALITY, method=6)
        size = dst.stat().st_size
        total += size
        print(f'{name:24} [{serial}] {before[0]}x{before[1]} -> {image.size[0]}x{image.size[1]}  {size / 1024:.0f} KB')

    print(f'共 {len(PICKS)} 张，合计 {total / 1024:.0f} KB')


if __name__ == '__main__':
    main()
