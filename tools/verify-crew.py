"""检查「风车邮局来信」改造后的结构与残留。结果写 JSON，避免控制台编码问题。"""
import json
import os
import re

html = open('index.html', 'rb').read().decode('utf-8')
css = open('style.css', 'rb').read().decode('utf-8')
js = open('app.js', 'rb').read().decode('utf-8')

slides = re.findall(r'<article class="crew-slide[^"]*">(.*?)</article>', html, re.S)
result = {
    'slide_count': len(slides),
    'slide_images': [re.search(r'assets/([\w.-]+)', s).group(1) for s in slides],
    'slide_captions': [re.search(r'<p>(.*?)</p>', s, re.S).group(1) for s in slides],
    'section_nums': re.findall(r'<span>(\d\d)</span>', html),
    'counter_text': re.search(r'<output id="crew-name">(.*?)</output>', html).group(1),
    'gone_from_html': [k for k in ['crew-postman', 'crew-baker', 'crew-tinker',
                                   'letter-shot', 'letter-pair', 'data-name'] if k not in html],
    'still_in_html': [k for k in ['crew-postman', 'crew-baker', 'crew-tinker',
                                  'letter-shot', 'letter-pair', 'data-name'] if k in html],
    'gone_from_css': [k for k in ['.letter-shot', '.letter-pair', '.crew-slide p b'] if k not in css],
    'js_uses_dataset_name': 'dataset.name' in js,
    'crew_files_left': [f for f in os.listdir('assets') if f.startswith('crew-')],
}
open('generated-raw/verify-crew.json', 'w', encoding='utf-8').write(
    json.dumps(result, ensure_ascii=False, indent=2))
print('written')
