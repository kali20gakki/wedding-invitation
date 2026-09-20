"""
把真实婚纱照（婚礼照片/*.jpg）转成网页用的 WebP，供「风车邮局来信」轮播使用。

⚠️ 这里**不做任何风格转换** —— 新人明确要求用原图风格。
   只做两件事：等比缩小 + 转 WebP 压缩。

每种尺寸出两档：
  photo-NN.webp       长边 1280（桌面 / 高分辨率屏）
  photo-NN@640.webp   长边 640（手机；卡片实际只显示约 308px 宽，@2x 就是 616px）
配合 HTML 的 srcset，手机只下载 @640 那一档，首屏体积减半。

用法: python tools/build-wedding-photos.py

编号 → 画面内容的对应关系（逐张看图确认过，改选片时照这张表改）：
  4964  玫瑰花裙长拖尾铺满地面，花瓣飘落
  4965  大理石楼梯旁，新娘捧花侧身，新郎倚栏
  4966  烛光中白花冠新娘侧坐
  4967  黑幕前，新娘宽檐纱帽、新郎黑西装
  4968  黑幕前，新娘纱帽与长头纱特写
  4969  林间两把透明伞相望
  4970  俯瞰草坪，白花与新人相对
  4971  古门前共读，新郎为新娘掀纱（烛台）
  4972  红幕圆月，中式礼服相望
  4973  拱窗前新娘剪影，满地花瓣
"""
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / '婚礼照片'
OUT = ROOT / 'assets' / 'crew'

# 顺序 = 轮播顺序
PICKS = [
    ('4966', 'photo-01'),  # 烛光白花冠
    ('4968', 'photo-02'),  # 黑幕纱帽特写
    ('4965', 'photo-03'),  # 楼梯旁捧花
    ('4971', 'photo-04'),  # 古门前掀纱
    ('4964', 'photo-05'),  # 花裙长拖尾
    ('4969', 'photo-06'),  # 林间两伞
    ('4970', 'photo-07'),  # 俯瞰草坪
    ('4973', 'photo-08'),  # 拱窗剪影
    ('4967', 'photo-09'),  # 黑幕白纱帽
    ('4972', 'photo-10'),  # 红幕圆月
]

SIZES = [('', 1280, 95), ('@640', 640, 45)]   # (文件名后缀, 长边, 单张体积上限 KB)
QUALITIES = (84, 80, 76, 72, 68, 64, 58)


def find_by_serial(files, serial):
    """按照片自身编号定位源图。

    不能用 sorted 的序号 —— 文件名的时间戳前缀和照片编号顺序并不一一对应，
    按序号写会错位（此前连错两次）。
    """
    for path in files:
        if f'_{serial}_' in path.name:
            return path
    raise SystemExit(f'没找到编号为 {serial} 的照片')


def main() -> None:
    files = sorted(SRC.glob('*.jpg'))
    if not files:
        raise SystemExit(f'没找到婚纱照：{SRC}')
    OUT.mkdir(parents=True, exist_ok=True)

    total = 0
    for serial, stem in PICKS:
        src = find_by_serial(files, serial)
        original = ImageOps.exif_transpose(Image.open(src)).convert('RGB')
        line = [f'{stem} [{serial}]']
        for suffix, max_side, limit_kb in SIZES:
            image = original.copy()
            image.thumbnail((max_side, max_side), Image.LANCZOS)
            dst = OUT / f'{stem}{suffix}.webp'
            chosen = None
            for quality in QUALITIES:
                image.save(dst, format='WEBP', quality=quality, method=6)
                if dst.stat().st_size / 1024 <= limit_kb:
                    chosen = quality
                    break
            size = dst.stat().st_size
            total += size
            line.append(f'{suffix or "full"}:{image.size[0]}x{image.size[1]} q{chosen or "min"} {size / 1024:.0f}KB')
        print('  '.join(line))

    print(f'共 {len(PICKS)} 张 × {len(SIZES)} 档，合计 {total / 1024:.0f} KB')


if __name__ == '__main__':
    main()
