"""Final Cut Pro のテキストクリップにセリフを貼り付けるスクリプト。

TXT ファイルからセリフを読み込み、FCP のタイムライン上で
先頭クリップから順にテキストを貼り付けします。
クリップはあらかじめ分割済みであることを前提とします。

【合成音声モード（LIVE_VOICE = False）】
  テキストクリップが連続して並んでいる状態。
  先頭クリップから順に全クリップへセリフを貼り付けます。

  [セリフA] [セリフB] [セリフC] ...

【生声モード（LIVE_VOICE = True）】
  空のテキストクリップと文字入りテキストクリップが交互に並んでいる状態。
  先頭は空クリップ。偶数番目（2,4,6...）のクリップにセリフを貼り付けます。

  [空] [セリフA] [空] [セリフB] [空] [セリフC] ...

使い方:
1. txt_input/ にセリフを1行1セリフで記述した TXT ファイルを配置
   - 空行はスキップされます
   - # で始まる行はコメントとしてスキップされます
2. TXT_FILE を対象ファイル名に変更
3. LIVE_VOICE を音声種別に合わせて変更（合成音声: False、生声: True）
4. INPUT_X, INPUT_Y を get_mouse_positions.py で取得した値に変更
5. FCP で先頭のテキストクリップを選択した状態にする
6. `python scripts/auto_fcp_telop_paste.py` を実行
"""

import os
import re
import sys
import pyautogui
import time
import pyperclip

# ===================== 設定 =====================
# セリフ TXT ファイル（txt_input/ ディレクトリに配置）
TXT_FILE = "txt_input/sample.txt"

# 生声モード: True = 生声（空クリップと文字入りクリップが交互）
#             False = 合成音声（テキストクリップが連続）
LIVE_VOICE = False

# テキスト入力欄の座標（get_mouse_positions.py で取得）
INPUT_X, INPUT_Y = 955, 204

# キー操作間のウェイト（秒）
SLEEP_SHORT = 0.5
# FCP がクリップ移動・描画を完了するまで待つ長めのウェイト（秒）
SLEEP_LONG = 3
# 開始前のカウントダウン（秒）
SLEEP_COUNTDOWN = 5
# ===================== 設定ここまで =====================


def is_metadata_line(line: str) -> bool:
    """VTT / SRT のメタデータ行かどうかを判定する。

    スキップ対象:
    - 空行
    - # で始まるコメント行
    - "WEBVTT" ヘッダー
    - タイムスタンプ行（例: 00:00:00.000 --> 00:00:04.220）
    - 連番行（数字のみ）
    """
    s = line.strip()
    if not s:
        return True
    if s.startswith("#"):
        return True
    if s == "WEBVTT":
        return True
    if re.fullmatch(r"[\d:.,\- >]+", s):
        return True
    return False


def load_voices_from_txt(txt_path: str) -> list[str]:
    """TXT / VTT / SRT ファイルからセリフを読み込む。

    メタデータ行（空行・コメント・ヘッダー・タイムスタンプ・連番）を除いた
    テキスト行のみを返す。
    """
    if not os.path.exists(txt_path):
        print(f"❌ ファイルが見つかりません: {txt_path}")
        print(f"   txt_input/ ディレクトリにファイルを配置してください。")
        sys.exit(1)

    with open(txt_path, encoding="utf-8") as f:
        lines = f.readlines()

    voices = [
        line.rstrip("\n")
        for line in lines
        if not is_metadata_line(line)
    ]

    if not voices:
        print(f"❌ セリフが見つかりません: {txt_path}")
        sys.exit(1)

    return voices


def main():
    # TXT からセリフを読み込み
    voice_list = load_voices_from_txt(TXT_FILE)

    print(f"📄 TXT ファイル: {TXT_FILE}")
    print(f"📝 セリフの数: {len(voice_list)}")
    print()

    # 確認表示
    for i, v in enumerate(voice_list):
        print(f"  {i + 1}. {v}")
    print()

    mode_label = "生声" if LIVE_VOICE else "合成音声"
    print(f"🎙 モード: {mode_label}")
    print("準備")
    print("テキストフィールドが見える状態にしておきます。")
    print(f"⏱ {SLEEP_COUNTDOWN}秒後に開始します。Final Cut Pro をアクティブにしておいてください！")
    time.sleep(SLEEP_COUNTDOWN)

    # 生声モードの場合、先頭の空クリップをスキップして次のクリップへ移動
    if LIVE_VOICE:
        pyautogui.keyDown("command")
        pyautogui.press("right")
        pyautogui.keyUp("command")
        time.sleep(SLEEP_SHORT)

    # ループでセリフを先頭から順に入力する
    for i, voice in enumerate(voice_list):
        print(f"  [{i + 1}/{len(voice_list)}] {voice}")

        # テキストフィールドに移動
        if i == 0:
            # 最初はテキストエリアをクリック
            pyautogui.click(INPUT_X, INPUT_Y)
            time.sleep(SLEEP_SHORT)
            # 【バグ修正】テキストエリアを確実に有効化するため2度目のクリックをする
            pyautogui.click(INPUT_X, INPUT_Y)
            time.sleep(SLEEP_LONG)
        else:
            # 2回目以降は Tab で移動
            pyautogui.press("tab")
            time.sleep(SLEEP_SHORT)

        # 全選択（Command + A）
        pyautogui.keyDown("command")
        pyautogui.press("a")
        pyautogui.keyUp("command")
        time.sleep(SLEEP_SHORT)

        # クリップボードにコピーして貼り付け（Command + V）
        pyperclip.copy(voice)
        pyautogui.keyDown("command")
        pyautogui.press("v")
        pyautogui.keyUp("command")
        time.sleep(SLEEP_SHORT)

        # 次のクリップへ移動（Command + Right）
        pyautogui.keyDown("command")
        pyautogui.press("right")
        pyautogui.keyUp("command")
        time.sleep(SLEEP_SHORT)

        # 生声モードの場合、空クリップをさらにスキップ
        if LIVE_VOICE:
            pyautogui.keyDown("command")
            pyautogui.press("right")
            pyautogui.keyUp("command")
            time.sleep(SLEEP_SHORT)

    print("✅ すべてのテロップを入力しました")


if __name__ == "__main__":
    main()
