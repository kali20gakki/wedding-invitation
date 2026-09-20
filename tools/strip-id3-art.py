"""去掉 mp3 里内嵌的封面图（APIC），保留文字标签。

为什么必须去：
  ID3 标签在文件**开头**，浏览器要先把标签下完才能开始解码音频。
  这首 bgm 的 APIC（封面图）有 798,219 字节，占全文件 13% ——
  也就是说宾客点下播放，得先下完 800KB 才开始出声，手机上会明显卡一下。
  去掉后音频数据紧跟在一个 1KB 出头的标签后面，几乎可以立刻起播。

为什么保留文字标签而不是整个删掉：
  标题/艺术家等文字帧加起来只有 1KB 左右，留着不花钱，还能保住出处署名。

用法: python tools/strip-id3-art.py <源文件> <输出文件>
例:   python tools/strip-id3-art.py bgm.mp3 assets/wedding-bgm.mp3
"""
import io
import sys


def synchsafe(value):
    return bytes([(value >> 21) & 0x7F, (value >> 14) & 0x7F, (value >> 7) & 0x7F, value & 0x7F])


def read_synchsafe(raw):
    return (raw[0] << 21) | (raw[1] << 14) | (raw[2] << 7) | raw[3]


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else 'bgm.mp3'
    dst = sys.argv[2] if len(sys.argv) > 2 else 'assets/wedding-bgm.mp3'
    data = io.open(src, 'rb').read()
    print(f'源文件: {src}  {len(data)} bytes')

    if data[:3] != b'ID3':
        print('没有 ID3v2 标签，直接复制')
        io.open(dst, 'wb').write(data)
        return

    major, revision, flags = data[3], data[4], data[5]
    tag_size = read_synchsafe(data[6:10])
    audio_at = 10 + tag_size + (10 if flags & 0x10 else 0)
    print(f'ID3v2.{major}.{revision}  flags=0x{flags:02x}  标签 {tag_size + 10} bytes  音频从 {audio_at} 开始')

    if flags & 0x80:
        # 用了 unsynchronisation，帧内容被转义过，逐帧搬运会破坏数据 —— 整个标签丢掉最稳
        print('标签带 unsynchronisation，改为整段丢弃标签（更稳）')
        new_tag = b''
    elif major <= 2:
        print('ID3v2.2 帧头格式不同，改为整段丢弃标签（更稳）')
        new_tag = b''
    else:
        body = data[10:10 + tag_size]
        kept, dropped = bytearray(), []
        pos = 0
        while pos + 10 <= len(body):
            fid = body[pos:pos + 4]
            if not fid.strip(b'\x00'):
                break
            fsize = int.from_bytes(body[pos + 4:pos + 8], 'big')
            if fsize <= 0 or pos + 10 + fsize > len(body):
                break
            frame = body[pos:pos + 10 + fsize]
            if fid in (b'APIC', b'PIC'):
                dropped.append((fid.decode('latin-1'), fsize))
            else:
                kept += frame
            pos += 10 + fsize
        if dropped:
            print(f'丢弃的帧: {dropped}')
        else:
            print('标签里没有封面图帧，原样保留全部文字帧')
        new_tag = b'ID3' + bytes([major, 0, 0]) + synchsafe(len(kept)) + bytes(kept) if kept else b''

    out = new_tag + data[audio_at:]
    io.open(dst, 'wb').write(out)
    saved = len(data) - len(out)
    print(f'输出: {dst}  {len(out)} bytes  （省下 {saved} bytes / {saved / len(data) * 100:.1f}%）')
    print(f'新标签长度 {len(new_tag)} bytes，音频仍在 {len(new_tag)} 处开始')


if __name__ == '__main__':
    main()
