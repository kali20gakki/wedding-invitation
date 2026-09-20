"""把分享缩略图从 WebP 转出一份 JPG。

为什么需要：
  微信 / QQ 抓取分享卡片缩略图时对 WebP 支持不稳，抓不到就只剩标题和描述，
  卡片是空白的。JPG 是各家爬虫都认的格式，所以 og:image 指向 JPG，
  WebP 作为第二张备用（Open Graph 允许 og:image 出现多次，消费方取第一张）。

用法: python tools/build-og.py
输入: assets/og-share.webp  (1200×630)
输出: assets/og-share.jpg
"""
from PIL import Image

SRC = 'assets/og-share.webp'
DST = 'assets/og-share.jpg'
# WebP 带 alpha 通道；JPG 不支持透明，透明处垫成页面纸色，避免出现黑边
PAPER = (247, 240, 225)


def main():
    image = Image.open(SRC)
    print(f'源图: {SRC}  {image.size}  {image.mode}')
    if image.size != (1200, 630):
        raise SystemExit(f'期望 1200×630，实际 {image.size} —— 尺寸变了要先确认再转')

    if image.mode in ('RGBA', 'LA', 'P'):
        rgba = image.convert('RGBA')
        flat = Image.new('RGB', rgba.size, PAPER)
        flat.paste(rgba, mask=rgba.split()[-1])
        image = flat
    else:
        image = image.convert('RGB')

    image.save(DST, 'JPEG', quality=90, optimize=True, progressive=True)
    out = Image.open(DST)
    import os
    print(f'输出: {DST}  {out.size}  {out.mode}  {os.path.getsize(DST)} bytes')


if __name__ == '__main__':
    main()
