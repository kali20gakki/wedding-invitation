"""为挑选照片生成缩小预览。

用法: python tools/make-previews.py
"""
import os
from PIL import Image

SRC = 'raw-photos'
OUT = 'generated-raw/photo-preview'


def main():
    os.makedirs(OUT, exist_ok=True)
    for index, name in enumerate(sorted(os.listdir(SRC)), 1):
        path = os.path.join(SRC, name)
        if not os.path.isfile(path):
            continue
        image = Image.open(path).convert('RGB')
        width, height = image.size
        scale = 1000 / max(width, height)
        preview = image.resize((round(width * scale), round(height * scale)), Image.LANCZOS)
        target = os.path.join(OUT, f'p{index}.jpg')
        preview.save(target, 'JPEG', quality=88)
        print(f'p{index}.jpg  <-  {name}  {width}x{height} -> {preview.size[0]}x{preview.size[1]}')


if __name__ == '__main__':
    main()
