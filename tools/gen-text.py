"""首页文字图层：白色手写书信体（换成清新风格）。

背景是蓝天，白字对比强、观感清新。
输出透明底 PNG，网页端用 filter: drop-shadow 加柔和阴影保证可读性。

用法:
  set IMAGE_API_KEY=sk-...
  python tools/gen-text.py [任务名 ...]
  python tools/gen-text.py --list
"""
import json
import os
import subprocess
import sys

API = 'https://code28.ccwu.cc/v1/images/edits'
RAW = 'generated-raw'
REF_PERSON = '起风了人物.webp'

# 共用的白字风格段
WHITE_LETTER = (
    'Produce ONLY decorative white hand-lettering on a fully TRANSPARENT background. '
    'No scene, no illustration, no background colour, no paper, no border, no frame, no decoration, '
    'no shadow baked into the image - just the pure white lettering itself, '
    'centred with generous empty margin around it.\n'
    'Style: delicate, fresh and clean hand-lettered script, as if written with a fine white gel pen '
    'or a light brush on a letter - smooth flowing strokes, gentle variation in stroke width, '
    'light and airy, nothing heavy or ornate, no gold, no outline, no drop shadow.\n'
    'Pure white (#FFFFFF).\n'
    'Render every character correctly and legibly. No other text, no watermark, no signature.'
)

JOBS = {}


def job(name, prompt, size='1536x1024'):
    JOBS[name] = {'name': name, 'prompt': prompt, 'size': size}


job(
    'text-names-v2',
    WHITE_LETTER + '\nThe text to render, exactly: 张伟 & 李旭雨\n'
                   'The ampersand should be smaller and lighter than the two names.',
    size='1536x1024',
)

job(
    'text-date-v2',
    WHITE_LETTER + '\nThe text to render, exactly: 2026.10.02\n'
                   'Use simple clean numerals with wide letter spacing, light weight.',
)

job(
    'text-invite-v2',
    WHITE_LETTER + '\nThe text to render, exactly: 婚礼邀请函\n'
                   'Calm and dignified, generous letter spacing.',
)

# v3：首页改版后只要四个字（"函"去掉），作为姓名下方的副题。
# 沿用 v2 的 WHITE_LETTER 与同一张参考图，笔迹才能和 text-names 完全一致。
job(
    'text-invite-v3',
    WHITE_LETTER + '\nThe text to render, exactly: 婚礼邀请\n'
                   'Calm and dignified, generous letter spacing. '
                   'Only these four characters - do not add any other character.',
)


def generate(name):
    spec = JOBS[name]
    key = os.environ.get('IMAGE_API_KEY', '')
    if not key:
        raise SystemExit('缺少环境变量 IMAGE_API_KEY')
    command = ['curl.exe', '-s', '-S', '-X', 'POST', API,
               '-H', f'Authorization: Bearer {key}',
               '-F', 'model=gpt-image-2',
               '-F', f'prompt={spec["prompt"]}',
               '-F', f'size={spec["size"]}',
               '-F', 'quality=high',
               '-F', 'n=1',
               '-F', 'background=transparent',
               '-F', f'image=@{REF_PERSON}']
    result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
    text = (result.stdout or '').strip()
    json.dump({'raw': text}, open(os.path.join(RAW, f'{name}.json'), 'w'), ensure_ascii=False, indent=2)
    try:
        payload = json.loads(text)
        item = payload['data'][0]
    except Exception as exc:  # noqa: BLE001
        print(f'{name}: 解析失败 {exc}\n{text[:400]}')
        return
    target = os.path.join(RAW, f'{name}.png')
    subprocess.run(['curl.exe', '-s', '-S', '-o', target, item['url']], check=True)
    size_mb = os.path.getsize(target) / 1024 / 1024
    print(f'{name}.png  {payload.get("size")}  {size_mb:.2f} MB')


def main():
    if len(sys.argv) < 2 or sys.argv[1] == '--list':
        print('可用任务:', ', '.join(JOBS))
        return
    for name in sys.argv[1:]:
        if name not in JOBS:
            print(f'未知任务: {name}')
            continue
        generate(name)


if __name__ == '__main__':
    main()
