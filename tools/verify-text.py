"""核对关键文本文件是否包含应有的中文内容（防编码损坏）。

只做正向关键词检查，不依赖控制台编码，结果写成 UTF-8 文件。
用法: python tools/verify-text.py
"""
import json

CHECKS = {
    'index.html': ['张伟', '李旭雨', '金花玉湖酒店', '一封信', '关于我们', '风车邮局来信',
                   '旅人手账', '往那盏灯的路', '在旅人名册上落款', '带走一张',
                   '2026年10月2日', '星期五', '午宴', '草坪婚礼', 'surl.amap.com'],
    'style.css': ['.us-section', '.us-pair', '.hotel-shot', '.draw-layer', '.chime-note',
                  '.crew-slide', '.pixel-fish', '.game-hud', '.quick-nav'],
    'app.js': ['RSVP_FORM_URL', 'feishu.cn', 'DRAW_CARDS', 'craneBlessings', 'chimeBlessings',
               '2026-10-02', 'journey-wedding-draw'],
    'PROMPTS.md': ['B1', 'B11a', 'B14', 'hero-journey-v5', '金花玉湖'],
    'tools/CHECKLIST-web.md': ['横向滚动', 'ONLINE', '飞书'],
}

result = {}
for path, keys in CHECKS.items():
    try:
        text = open(path, 'rb').read().decode('utf-8')
    except Exception as exc:  # noqa: BLE001
        result[path] = {'decode_error': str(exc)}
        continue
    result[path] = {
        'bytes': len(text.encode('utf-8')),
        'missing': [k for k in keys if k not in text],
        'found': len(keys) - len([k for k in keys if k not in text]),
        'total': len(keys),
    }

open('generated-raw/verify-text.json', 'w', encoding='utf-8').write(
    json.dumps(result, ensure_ascii=False, indent=2))
print('written to generated-raw/verify-text.json')
