"""调用图片 API 生成素材（走 curl，支持透明背景与多张参考图）。

为什么用 curl 而不是 Python 的 urllib：
  该代理对 urllib 构造的 multipart 请求返回 403，用 curl 的 -F 则正常。
  实测结论，勿改回 urllib。

用法:
  set IMAGE_API_KEY=sk-...
  python tools/gen-image.py <任务名> [<任务名> ...]
  python tools/gen-image.py --list
"""
import json
import os
import subprocess
import sys

API = 'https://code28.ccwu.cc/v1/images/edits'
RAW = 'generated-raw'

CEL_PERSON = '起风了人物.webp'
SCENE_MASTER = 'generated-raw/hero-journey-v5.png'

JOBS = {}


def job(name, prompt, refs, size='1024x1536', background=None, quality='high'):
    JOBS[name] = {'name': name, 'prompt': prompt, 'refs': refs, 'size': size,
                  'background': background, 'quality': quality}


# ---------------------------------------------------------------- 封面与文字
job(
    'text-names',
    'Produce ONLY decorative Chinese calligraphy lettering on a fully TRANSPARENT background. '
    'No scene, no illustration, no background colour, no border, no frame - just the lettering itself, '
    'centred with generous empty margin around it.\n'
    'The text to render, exactly: 张伟 & 李旭雨\n'
    'Style: elegant hand-lettered Chinese calligraphy in a soft romantic brush script, '
    'warm antique gold (#D9A441) with a subtle darker warm outline, '
    'slightly varied stroke weight, gentle and festive, '
    'in the spirit of hand-lettered titles of classic Japanese animation films.\n'
    'Render every character correctly and legibly, including the ampersand between the two names. '
    'No other text, no watermark, no signature.',
    [CEL_PERSON],
)

job(
    'text-invite',
    'Produce ONLY decorative Chinese calligraphy lettering on a fully TRANSPARENT background. '
    'No scene, no illustration, no background colour, no border, no frame - just the lettering itself, '
    'centred with generous empty margin around it.\n'
    'The text to render, exactly: 婚礼邀请函\n'
    'Style: elegant hand-lettered Chinese calligraphy, a calm refined brush script, '
    'deep ink colour #3A3B33 with slight warm gold accents, generous letter spacing, '
    'dignified and warm, in the spirit of hand-lettered titles of classic Japanese animation films.\n'
    'Render every character correctly and legibly. No other text, no watermark, no signature.',
    [CEL_PERSON],
    size='1536x1024',
)

job(
    'text-date',
    'Produce ONLY decorative lettering on a fully TRANSPARENT background. '
    'No scene, no illustration, no background colour, no border, no frame - just the lettering itself.\n'
    'The text to render, exactly: 2026.10.02\n'
    'Style: elegant thin serif numerals, warm antique gold (#D9A441), very wide letter spacing, '
    'refined and understated.\n'
    'No other text, no watermark, no signature.',
    [CEL_PERSON],
    size='1536x1024',
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
               '-F', f'quality={spec["quality"]}',
               '-F', 'n=1']
    if spec['background']:
        command += ['-F', f'background={spec["background"]}']
    for ref in spec['refs']:
        command += ['-F', f'image=@{ref}']

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
    if item.get('b64_json'):
        import base64
        open(target, 'wb').write(base64.b64decode(item['b64_json']))
    size_mb = os.path.getsize(target) / 1024 / 1024
    print(f'{name}.png  {payload.get("size")}  {size_mb:.2f} MB  background={payload.get("background")}')


def main():
    if len(sys.argv) < 2 or sys.argv[1] == '--list':
        print('可用任务:')
        for name in JOBS:
            print(' ', name)
        return
    for name in sys.argv[1:]:
        if name not in JOBS:
            print(f'未知任务: {name}')
            continue
        generate(name)


if __name__ == '__main__':
    main()
