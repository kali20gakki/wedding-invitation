"""检查背景音乐 mp3 是否可用：时长、码率、采样率、通道、ID3 标签、文件体积。

为什么需要手写解析：
  这台机器没有 ffmpeg / ffprobe / mutagen，而背景音乐是宾客要下载的东西，
  发布前必须确认它是**能播的真 mp3**（不是改了后缀的文件）、以及有多大。

用法: python tools/check-bgm.py [路径]
"""
import io
import os
import sys

BITRATE_V1_L3 = [None, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320, None]
BITRATE_V2_L3 = [None, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160, None]
SAMPLE_RATE = {3: [44100, 48000, 32000], 2: [22050, 24000, 16000], 0: [11025, 12000, 8000]}
TEXT_FRAMES = {'TIT2': '标题', 'TPE1': '艺术家', 'TALB': '专辑', 'TCON': '风格', 'TDRC': '年份', 'TPE2': '专辑艺术家'}


def synchsafe(raw):
    return (raw[0] << 21) | (raw[1] << 14) | (raw[2] << 7) | raw[3]


def read_id3(data):
    """返回 (标签字典, 音频起始偏移, 全部帧的 [(ID, 字节数)])。"""
    tags, start, frames_out = {}, 0, []
    if data[:3] != b'ID3':
        return tags, 0, frames_out
    major = data[3]
    size = synchsafe(data[6:10])
    flags = data[5]
    body = data[10:10 + size]
    start = 10 + size + (10 if flags & 0x10 else 0)  # footer
    text_encodings = {0: 'latin-1', 1: 'utf-16', 2: 'utf-16-be', 3: 'utf-8'}
    pos = 0
    # v2.2 的帧头是 3 字节 ID + 3 字节长度，v2.3+ 是 4+4
    if major <= 2:
        return tags, start, frames_out
    while pos + 10 <= len(body):
        fid = body[pos:pos + 4].decode('latin-1')
        if not fid.strip('\x00'):
            break
        fsize = int.from_bytes(body[pos + 4:pos + 8], 'big')
        if fsize <= 0 or pos + 10 + fsize > len(body):
            break
        payload = body[pos + 10:pos + 10 + fsize]
        frames_out.append((fid, fsize + 10))
        if fid in TEXT_FRAMES and payload:
            enc = text_encodings.get(payload[0], 'utf-8')
            tags[TEXT_FRAMES[fid]] = payload[1:].decode(enc, 'replace').strip('\x00').strip()
        pos += 10 + fsize
    return tags, start, frames_out


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else 'assets/wedding-bgm.mp3'
    data = io.open(path, 'rb').read()
    print(f'文件: {path}')
    print(f'体积: {len(data)} bytes  ({len(data) / 1048576:.2f} MB)')

    tags, start, id3_frames = read_id3(data)
    print(f'ID3 标签: {tags if tags else "无"}')
    if id3_frames:
        print(f'ID3 帧（占 {start} 字节 = 全文件的 {start / len(data) * 100:.0f}%）：')
        for fid, fsize in sorted(id3_frames, key=lambda x: -x[1]):
            print(f'   {fid}  {fsize} bytes')

    pos = start
    while pos + 4 <= len(data) and not (data[pos] == 0xFF and (data[pos + 1] & 0xE0) == 0xE0):
        pos += 1
    if pos + 4 > len(data):
        raise SystemExit('没找到 MPEG 帧同步头 —— 这很可能不是 mp3')
    print(f'音频起始偏移: {pos}（跳过了 {pos} 字节的标签）')

    version_bits = (data[pos + 1] >> 3) & 0x03
    layer_bits = (data[pos + 1] >> 1) & 0x03
    if layer_bits != 0x01:
        raise SystemExit(f'不是 Layer III（layer_bits={layer_bits}）')
    version = {3: 1, 2: 2, 0: 2.5}.get(version_bits)
    br_index = (data[pos + 2] >> 4) & 0x0F
    sr_index = (data[pos + 2] >> 2) & 0x03
    padding = (data[pos + 2] >> 1) & 0x01
    channel = '单声道' if ((data[pos + 3] >> 6) & 0x03) == 3 else '立体声'

    bitrate = (BITRATE_V1_L3 if version == 1 else BITRATE_V2_L3)[br_index]
    rate = SAMPLE_RATE[version_bits][sr_index]
    print(f'MPEG{version} Layer III  {rate} Hz  {channel}  首帧 {bitrate} kbps  padding={padding}')

    # 逐帧统计：既能得到精确时长，也能看出是 CBR 还是 VBR
    samples_per_frame = 1152 if version == 1 else 576
    total_samples, frames, bitrates = 0, 0, set()
    p = start
    while p + 4 <= len(data):
        if not (data[p] == 0xFF and (data[p + 1] & 0xE0) == 0xE0):
            p += 1
            continue
        b_idx = (data[p + 2] >> 4) & 0x0F
        s_idx = (data[p + 2] >> 2) & 0x03
        pad = (data[p + 2] >> 1) & 0x01
        v_bits = (data[p + 1] >> 3) & 0x03
        if b_idx in (0, 15) or s_idx == 3 or v_bits == 1:
            p += 1
            continue
        br = (BITRATE_V1_L3 if v_bits == 3 else BITRATE_V2_L3)[b_idx]
        sr = SAMPLE_RATE[v_bits][s_idx]
        if not br or not sr:
            p += 1
            continue
        spf = 1152 if v_bits == 3 else 576
        size = (144 if v_bits == 3 else 72) * br * 1000 // sr + pad
        if size <= 4:
            p += 1
            continue
        bitrates.add(br)
        total_samples += spf
        frames += 1
        p += size

    if not frames:
        raise SystemExit('没有解析出任何完整帧')
    seconds = total_samples / rate
    print(f'帧数: {frames}   码率种类: {sorted(bitrates)}  （{"CBR" if len(bitrates) == 1 else "VBR"}）')
    print(f'时长: {seconds:.1f} 秒 = {int(seconds // 60)} 分 {seconds % 60:.0f} 秒')
    print(f'平均码率: {len(data) * 8 / seconds / 1000:.0f} kbps')


if __name__ == '__main__':
    main()
