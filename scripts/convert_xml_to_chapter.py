import xml.etree.ElementTree as ET
import os


def parse_fcpx_time(time_str):
    """FCPXMLの時刻文字列（例: '32000/24000s'）を秒（float）に変換する"""
    if not time_str:
        return 0.0
    time_str = time_str.replace('s', '')
    if '/' in time_str:
        num, den = map(float, time_str.split('/'))
        return num / den
    return float(time_str)


def format_timestamp(seconds):
    """秒数をYouTubeチャプター形式（例: '1:23' や '1:02:03'）に変換する"""
    seconds = int(round(seconds))
    hrs = seconds // 3600
    mins = (seconds % 3600) // 60
    secs = seconds % 60
    if hrs > 0:
        return f"{hrs}:{mins:02}:{secs:02}"
    else:
        return f"{mins}:{secs:02}"


def generate_chapters(input_file, output_file):
    if not os.path.exists(input_file):
        print(f"Error: {input_file} が見つかりません。")
        return

    tree = ET.parse(input_file)
    root = tree.getroot()

    # 全要素の親子関係を辞書で保持する（子 → 親の逆引き）
    parent_map = {child: parent for parent in root.iter() for child in parent}

    chapters = []

    for spine in root.findall(".//spine"):
        for element in spine.iter():
            if element.tag not in ('marker', 'chapter-marker'):
                continue

            name = element.get('value')
            abs_time = parse_fcpx_time(element.get('start'))

            # --- マーカーの直接の親を取得 ---
            direct_parent = parent_map.get(element)

            # --- 孫マーカーの処理 ---
            # マーカーがasset-clipの直接の子でない場合（例: video, titleの子）、
            # マーカーのstartは親の素材内部タイムコード上の位置で記録されている。
            # タイムライン上の位置を求めるには、親のstartを引いて
            # 素材内での経過時間に変換する必要がある。
            #
            # 子の場合:  タイムライン位置 = 親のoffset + markerのstart
            # 孫の場合:  タイムライン位置 = 祖父のoffset + 親のoffset + (markerのstart - 親のstart)
            if direct_parent is not None and direct_parent.tag != 'asset-clip':
                abs_time -= parse_fcpx_time(direct_parent.get('start', '0s'))

            # --- 親を遡ってoffsetを加算する ---
            current = element
            while True:
                parent = parent_map.get(current)
                if parent is None or parent.tag == 'spine':
                    break
                abs_time += parse_fcpx_time(parent.get('offset', '0s'))
                current = parent

            chapters.append((abs_time, name))

    chapters.sort()

    final_list = []

    # 最初のチャプターが0秒付近にない場合、Introductionを自動追加
    if not chapters or chapters[0][0] > 0.5:
        final_list.append("0:00 Introduction")

    for time_val, name in chapters:
        timestamp = format_timestamp(time_val)
        entry = f"{timestamp} {name}"
        # 同じタイムスタンプのチャプターが連続する場合は重複を除外
        if not final_list or not final_list[-1].startswith(timestamp):
            final_list.append(entry)

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(final_list))

    print(f"--- 完了！ {len(final_list)}個のチャプターを検出しました ---")
    print("\n".join(final_list))


if __name__ == "__main__":
    input_file = 'xml_input/test.fcpxml'
    output_file = 'xml_output/test_chapters.txt'
    generate_chapters(input_file, output_file)