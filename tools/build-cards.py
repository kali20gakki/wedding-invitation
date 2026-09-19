"""
把新人提供的成品邀请卡（抽卡图片/*.png）转成站点用的 WebP。

原图是 1080×1920 的成品卡（不是裁好的摄影图）：
卡面已经印好新人姓名、婚期、地点、日程，所以页面上直接整张显示，不再套 CSS 相框。

用法: python tools/build-cards.py
"""
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / '抽卡图片'
OUT = ROOT / 'assets' / 'cards'

# 卡面最终显示宽度约 272px（设备像素比 2 时 544px）。存 720px 宽留够余量，
# 再大就是白给流量：8 张卡一共也要控制在 1MB 出头。
TARGET_WIDTH = 720
QUALITY = 82


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    sources = sorted(SRC.glob('*.png'))
    if not sources:
        raise SystemExit(f'没找到卡面：{SRC}')

    total = 0
    for index, src in enumerate(sources, start=1):
        image = Image.open(src).convert('RGB')
        if image.width != TARGET_WIDTH:
            height = round(image.height * TARGET_WIDTH / image.width)
            image = image.resize((TARGET_WIDTH, height), Image.LANCZOS)
        dst = OUT / f'card-{index:02d}.webp'
        image.save(dst, format='WEBP', quality=QUALITY, method=6)
        size = dst.stat().st_size
        total += size
        print(f'{dst.name}  {image.width}x{image.height}  {size / 1024:.0f} KB')

    print(f'共 {len(sources)} 张，合计 {total / 1024:.0f} KB')


if __name__ == '__main__':
    main()
