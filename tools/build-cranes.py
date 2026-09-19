"""
由 assets/crane-shape.svg 模板生成一组上色的纸鹤 SVG。

为什么不用 currentColor：
    SVG 作为 <img src="..."> 独立文档加载时无法继承页面的 color，
    未匹配的 currentColor 会退回黑色。所以颜色必须在生成阶段写死。
    模板里统一用 __CRANE_INK__ 占位，本脚本替换成具体色值。

用法: python tools/build-cranes.py
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / 'assets'
TEMPLATE = ASSETS / 'crane.svg'

# 与 style.css 的调色板一致（app.js 里的 craneTones 也引用这几个键）
# 只保留压在浅色天空上仍看得清的色：天蓝 #A8CFE0、米白 #F2E3C9 与天空底太接近，不用
TONES = {
    'sunset': '#E8A657',   # --sunset
    'brick': '#B6463C',    # --accent-brick
    'grass': '#8FAE6B',    # --grass
    'road': '#D08A3E',     # 手绘标识里的暖橙，比 sunset 深一档
    'ink': '#3A3B33',      # --ink，最深的一只
}

# 折痕线的墨色，带一点透明度，压在浅色天空底上也不脏
INK = 'rgba(58,59,51,.5)'

HEADER = ('<!-- 由 tools/build-cranes.py 生成，请勿手改；改形状请改 assets/crane.svg 模板 -->\n')


def main() -> None:
    template = TEMPLATE.read_text(encoding='utf-8')
    if '__CRANE_INK__' not in template:
        raise SystemExit('模板 assets/crane.svg 里找不到 __CRANE_INK__ 占位符')

    written = []
    for name, color in TONES.items():
        svg = template.replace('__CRANE_INK__', INK).replace('currentColor', color)
        out = ASSETS / f'crane-{name}.svg'
        out.write_text(HEADER + svg, encoding='utf-8')
        written.append((out.name, len(svg)))

    for name, size in written:
        print(f'{name:24} {size:6} bytes')
    print(f'共 {len(written)} 个文件')


if __name__ == '__main__':
    main()
