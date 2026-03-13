import xml.etree.ElementTree as ET
import os

def parse_fcpx_time(time_str):
    if not time_str:
        return 0.0
    time_str = time_str.replace('s', '')
    if '/' in time_str:
        num, den = map(float, time_str.split('/'))
        return num / den
    return float(time_str)

def format_timestamp(seconds):
    # YouTubeは0.5秒以上の端数を切り上げて認識することが多いためroundを使用
    seconds = int(round(seconds))
    hrs = seconds // 3600
    mins = (seconds % 3600) // 60
    secs = seconds % 60
    if hrs > 0:
        return f"{hrs:02}:{mins:02}:{secs:02}"
    else:
        return f"{mins:02}:{secs:02}"

def generate_chapters():
    input_file = 'xml_input/info.fcpxml'
    output_file = 'xml_output/info_chapters.txt'

    if not os.path.exists(input_file):
        print(f"Error: {input_file} が見つかりません。")
        return

    tree = ET.parse(input_file)
    root = tree.getroot()

    # 全要素の親への参照マップを作成
    parent_map = {child: parent for parent in root.iter() for child in parent}

    chapters = []

    # タイムライン(spine)内の全マーカーを対象にする
    # spineの中にないマーカー（イベント内の素材マーカーなど）は除外する
    for spine in root.findall(".//spine"):
        # spineの中の全てのマーカーを再帰的に検索
        for marker in spine.iter('marker'):
            name = marker.get('value')
            m_start = parse_fcpx_time(marker.get('start'))
            
            # 親を遡って絶対時間を算出
            abs_time = m_start
            current = marker
            while True:
                parent = parent_map.get(current)
                if parent is None or parent.tag == 'spine':
                    break
                
                # クリップやストーリーラインには offset と start がある
                # 自身の開始位置(offset)を足して、親の中でのトリミング開始位置(start)を引く
                p_offset = parse_fcpx_time(parent.get('offset', '0s'))
                p_start = parse_fcpx_time(parent.get('start', '0s'))
                
                abs_time += (p_offset - p_start)
                current = parent
            
            chapters.append((abs_time, name))

        # chapter-markerも同様に処理
        for c_marker in spine.iter('chapter-marker'):
            name = c_marker.get('value')
            m_start = parse_fcpx_time(c_marker.get('start'))
            
            abs_time = m_start
            current = c_marker
            while True:
                parent = parent_map.get(current)
                if parent is None or parent.tag == 'spine':
                    break
                p_offset = parse_fcpx_time(parent.get('offset', '0s'))
                p_start = parse_fcpx_time(parent.get('start', '0s'))
                abs_time += (p_offset - p_start)
                current = parent
            
            chapters.append((abs_time, name))

    # 時間順にソート
    chapters.sort()

    final_list = []
    # YouTube用の 00:00 補完
    if not chapters or chapters[0][0] > 0.5:
        final_list.append("00:00 Introduction")

    for time_val, name in chapters:
        # 秒単位で重複を排除
        timestamp = format_timestamp(time_val)
        if not final_list or not final_list[-1].startswith(timestamp):
            final_list.append(f"{timestamp} {name}")

    # 書き出し
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(final_list))

    print(f"--- 完了！ {len(final_list)}個のチャプターを検出しました ---")
    print("\n".join(final_list))

if __name__ == "__main__":
    generate_chapters()