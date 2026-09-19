"""修复被 PowerShell 误用 GBK(cp936) 编码读写而损坏的 UTF-8 文本文件。

原理：
  PowerShell 的 Get-Content 在中文 Windows 上默认用 GBK(cp936) 解码 UTF-8 字节，
  得到"乱码字符串"；Set-Content -Encoding UTF8 再把它按 UTF-8 写回。
  因为 GBK 解码是逐字节的确定性映射，反向执行即可还原：
      UTF-8 解码(当前文件) -> 查表得到原始字节 -> 按 UTF-8 解码 -> 写回

  不用 str.encode('gbk')，因为 GBK 解码会产出码位落在用户区(PUA)的字符，
  标准编码器拒绝把这些码位编回去。改为穷举所有 1~2 字节序列，
  构建"字符 -> 原始字节"的完整反向表。

用法: python tools/fix-encoding.py <文件> [<文件> ...]
"""
import sys


def build_reverse_table():
    table = {}
    # 单字节 0x00-0xFF
    for b in range(0x100):
        try:
            ch = bytes([b]).decode('gbk')
        except UnicodeDecodeError:
            continue
        table.setdefault(ch, bytes([b]))
    # 双字节 0x81-0xFE / 0x40-0xFE
    for lead in range(0x81, 0xFF):
        for trail in list(range(0x40, 0x7F)) + list(range(0x80, 0xFF)):
            pair = bytes([lead, trail])
            try:
                ch = pair.decode('gbk')
            except UnicodeDecodeError:
                continue
            table.setdefault(ch, pair)
    return table


def repair(path: str, table: dict) -> str:
    raw = open(path, 'rb').read()
    if raw.startswith(b'\xef\xbb\xbf'):
        raw = raw[3:]
    text = raw.decode('utf-8')

    out = bytearray()
    missing = []
    for ch in text:
        seq = table.get(ch)
        if seq is None:
            missing.append(ch)
            continue
        out.extend(seq)

    if missing:
        return f'失败：有 {len(missing)} 个字符不在 GBK 反向表内，例如 {missing[:5]!r}'

    try:
        fixed = out.decode('utf-8')
    except UnicodeDecodeError as exc:
        return f'失败：还原后的字节不是合法 UTF-8（{exc}）'

    open(path, 'wb').write(fixed.encode('utf-8'))
    return f'已修复，{len(raw)} -> {len(out)} 字节'


def main():
    if len(sys.argv) < 2:
        print('用法: python tools/fix-encoding.py <文件> [...]')
        return
    table = build_reverse_table()
    print(f'GBK 反向表构建完成：{len(table)} 项')
    for path in sys.argv[1:]:
        print(f'{path}: {repair(path, table)}')


if __name__ == '__main__':
    main()
