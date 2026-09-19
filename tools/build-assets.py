"""把生成好的 PNG 源转成网页用 WebP，并压到计划规定的体积上限内。

用法: python tools/build-assets.py
源图在 generated-raw/，产物写入 assets/（均为小写连字符命名）。
"""
import os
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "generated-raw")
DST = os.path.join(ROOT, "assets")

# (源文件, 目标文件名, 最大宽度, 体积上限 KB, 最大高度或 None)
JOBS = [
    # 首页封面（新人合影）与社交分享卡片
    ("hero-couple.png",            "hero-couple.webp",        1024, 380, None),
    ("og-share-v2.png",            "og-share.webp",           1200, 260, None),
    # 书法字图（透明底，用于首页姓名与邀请语）——v2 白色手写书信体
    ("text-names-v2.png",          "text/text-names.webp",     900, 150, None),
    # v3：四个字「婚礼邀请」，作为姓名下方的副题。
    # 只存到显示尺寸的 2 倍（约 366px @2x 屏），存更宽不会更清楚，只是白给流量。
    ("text-invite-v3.png",         "text/text-invite.webp",    440, 150, None),
    # 注：text-date（旧日期图）已从首页移除，这一项一并删掉，
    #     否则每次重跑 build-assets.py 都会把它从源图重新生成出一个没人用的孤儿文件。
    # 场景图
    ("scene-chime.png",            "scene-chime.webp",        1280, 250, None),
    ("scene-window.png",           "scene-window.webp",       1280, 250, None),
    ("scene-hotel.png",            "scene-hotel.webp",        1280, 260, None),
    ("scene-ending.png",           "scene-ending.webp",       1024, 250, None),
    # 婚纱照转绘
    ("couple-arch-v2.png",         "couple-arch.webp",        1280, 280, None),
    ("couple-umbrella-v2.png",     "couple-umbrella.webp",     800, 200, None),
    ("couple-door-v2.png",         "couple-door.webp",         800, 200, None),
]


def encode(img, path, quality):
    img.save(path, "WEBP", quality=quality, method=6)


def main():
    os.makedirs(DST, exist_ok=True)
    total = 0
    print(f"{'产物':<26}{'尺寸':<13}{'质量':<6}{'体积':>10}")
    print("-" * 58)
    for src_name, dst_name, max_w, limit_kb, max_h in JOBS:
        src_path = os.path.join(SRC, src_name)
        if not os.path.exists(src_path):
            print(f"{dst_name:<26}跳过（源图不存在: {src_name}）")
            continue

        img = Image.open(src_path)
        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGBA" if "A" in img.getbands() else "RGB")

        w, h = img.size
        if w > max_w:
            img = img.resize((max_w, round(h * max_w / w)), Image.LANCZOS)

        dst_path = os.path.join(DST, dst_name)
        os.makedirs(os.path.dirname(dst_path), exist_ok=True) or None
        # 从高到低试质量，命中体积上限即停
        chosen = None
        for q in (88, 84, 80, 76, 72, 66, 60, 52):
            encode(img, dst_path, q)
            kb = os.path.getsize(dst_path) / 1024
            if kb <= limit_kb:
                chosen = q
                break
        kb = os.path.getsize(dst_path) / 1024
        total += kb
        fit = "" if kb <= limit_kb else "  ⚠️ 超限"
        print(f"{dst_name:<26}{f'{img.size[0]}x{img.size[1]}':<13}{chosen or 'min':<6}{kb:>9.0f}K{fit}")

    print("-" * 58)
    print(f"assets/ 新增合计: {total/1024:.2f} MB")


if __name__ == "__main__":
    main()
