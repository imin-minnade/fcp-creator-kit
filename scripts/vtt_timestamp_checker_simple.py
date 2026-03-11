VTT_FILE = "vtt_input/sample.vtt"

text = open(VTT_FILE, encoding="utf-8").read()

# タイムスタンプ行（"-->" を含む行）だけを抽出
lines = []
for l in text.splitlines():
    if "-->" in l:
        lines.append(l)

# 隣り合うタイムスタンプを比較して、前の終了より次の開始が早ければ表示
for i in range(1, len(lines)):
    prev_end = lines[i-1].split("-->")[1].strip()
    curr_start = lines[i].split("-->")[0].strip()
    if curr_start < prev_end:
        print(lines[i-1])
