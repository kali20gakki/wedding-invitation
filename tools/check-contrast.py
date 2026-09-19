"""从首页截图里采样顶部区域的背景亮度，估算白色文字的对比度。

白字压在压暗的天空上，需要确认压暗程度是否够用。
按 WCAG 相对亮度公式计算对比度，正文/小字建议 >= 4.5:1。

用法: python tools/check-contrast.py
"""
from PIL import Image

SHOT = 'generated-raw/shots/hero-view.png'
# 需要检查的文字区域（x0, y0, x1, y1），坐标基于 390x844 的截图。
# 首页改版后姓名上移到 15%、邀请语在 29%，所以采样框跟着挪；
# 原来那行「日期白字」已删除，改为采样邀请语。
REGIONS = {
    '顶部状态条（A JOURNEY OF WIND / 日期）': (18, 12, 372, 30),
    '邀请函标识（WEDDING · INVITATION）': (80, 60, 310, 82),
    '姓名白字': (60, 130, 330, 225),
    '邀请语白字（婚礼邀请函）': (100, 245, 290, 298),
}
WHITE = (255, 255, 255)


def relative_luminance(rgb):
    channels = []
    for value in rgb[:3]:
        srgb = value / 255
        channels.append(srgb / 12.92 if srgb <= 0.04045 else ((srgb + 0.055) / 1.055) ** 2.4)
    r, g, b = channels
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(a, b):
    la, lb = relative_luminance(a), relative_luminance(b)
    lighter, darker = max(la, lb), min(la, lb)
    return (lighter + 0.05) / (darker + 0.05)


def main():
    image = Image.open(SHOT).convert('RGB')
    print(f'截图: {SHOT}  {image.size}')
    print(f'{"区域":<34}{"背景亮度":>10}{"对比度":>10}  结论')
    print('-' * 74)
    for label, box in REGIONS.items():
        crop = image.crop(box)
        pixels = list(crop.getdata())
        # 文字是白色，取最暗的一批像素近似背景
        pixels.sort(key=lambda p: sum(p))
        darkest = pixels[:max(1, len(pixels) // 5)]
        average = tuple(sum(c[i] for c in darkest) // len(darkest) for i in range(3))
        lum = relative_luminance(average) * 255
        ratio = contrast_ratio(WHITE, average)
        verdict = '通过（>=4.5）' if ratio >= 4.5 else ('偏弱（3~4.5）' if ratio >= 3 else '不足（<3）')
        print(f'{label:<34}{lum:>10.0f}{ratio:>10.2f}  {verdict}')


if __name__ == '__main__':
    main()
