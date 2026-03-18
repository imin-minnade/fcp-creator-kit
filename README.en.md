# FCP Creator Kit 🎬

[日本語](README.md) | English

**A Python toolkit to automate subtitle (telop) work in Final Cut Pro**

Reduces subtitle work per video by **~75%**.
Supports both synthetic voice (VOICEVOX / AquesTalk) and narration recording workflows.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Platform](https://img.shields.io/badge/Platform-macOS-lightgrey)
![License](https://img.shields.io/badge/License-MIT-green)

---

## What is this?

A collection of scripts that automate subtitle (text clip) insertion for YouTube videos.

Since clips are split and pasted directly on the Final Cut Pro timeline, you can visually confirm each step while automation proceeds safely.

### Supported Workflows

| Workflow | Description |
|---|---|
| **Synthetic Voice Route** | Scenario (CSV) → Generate audio with AquesTalk → Auto-insert subtitles in FCP |
| **Narration Route** | Record audio → Transcribe with Whisper (VTT) → Auto-insert subtitles in FCP |

### Why use this instead of VREW or AI Captions?

- **Directly editable in Final Cut Pro**: Inserted as text clips, so you can freely customize font, size, color, and animation
- **Bypasses AI caption limitations**: FCP's AI captions do not support Japanese (as of 2025), and even after support is added, style changes are not possible. This tool handles conversion from SRT/VTT to text clips
- **Environment-independent**: A calibration script automatically detects coordinates, so it works on any Mac environment

---

## Directory Structure

```
fcp-creator-kit/
├── scripts/                    # Automation scripts
│   ├── auto_fcp_telop_split_paste.py
│   ├── auto_fcp_telop_paste.py
│   ├── auto_fcp_vtt_to_telop.py
│   ├── auto_fcp_vtt_srt_to_telop.py
│   ├── auto_audio_to_vtt.py
│   ├── auto_aques_talk_player.py
│   ├── swap_title_number.py
│   ├── vtt_timestamp_checker.py
│   ├── convert_xml_to_chapter.py
│   └── get_mouse_positions.py
├── xml_input/                  # Place FCPXML files here (for chapter generation)
├── csv_input/                  # Place scenario CSV files here
│   └── sample.csv
├── txt_input/                  # Place dialogue TXT files here
│   └── sample.txt
├── audio_input/                # Place audio files here (narration route)
├── vtt_input/                  # Place VTT files here
│   └── sample.vtt
├── srt_input/                  # Place SRT files here
│   └── sample.srt
├── vtt_output/                 # Whisper transcription results are output here
├── wav_output/                 # Place AquesTalk audio files here
├── xml_output/                 # Chapter lists and other outputs
│   └── sample.fcpxml
├── requirements.txt
└── README.md
```

## Script List

| Script | Function | Input | Output |
|---|---|---|---|
| `auto_fcp_telop_split_paste.py` | Split text clips and paste dialogue on FCP in one step | `txt_input/*.txt` | FCP timeline |
| `auto_fcp_telop_paste.py` | Paste dialogue into pre-split clips (switchable between synthetic voice and narration) | `txt_input/*.txt` | FCP timeline |
| `auto_fcp_vtt_to_telop.py` | Split clips by VTT timestamps and paste dialogue | `vtt_input/*.vtt` | FCP timeline |
| `auto_fcp_vtt_srt_to_telop.py` | Split clips by VTT/SRT timestamps and paste dialogue (unified version) | `vtt_input/*.vtt` or `srt_input/*.srt` | FCP timeline |
| `auto_audio_to_vtt.py` | Transcribe audio files with faster-whisper | `audio_input/*` | `vtt_output/*.vtt` |
| `auto_aques_talk_player.py` | Auto-input text to AquesTalk Player for speech synthesis | `csv_input/*.csv` | `wav_output/*.wav` |
| `swap_title_number.py` | Rename WAV files from "dialogue_number" → "number_dialogue" | `wav_output/*.wav` | `wav_output/*.wav` |
| `vtt_timestamp_checker.py` | Check for overlapping timestamps in VTT files | `vtt_input/*.vtt` | stdout |
| `convert_xml_to_chapter.py` | Generate YouTube chapter list from FCPXML markers | `xml_input/info.fcpxml` | `xml_output/info_chapters.txt` |
| `get_mouse_positions.py` | Display screen coordinates on click | Mouse operation | Coordinate values |

---

## Quick Start

### 1. Setup

```bash
git clone git@github.com:imin-minnade/fcp-creator-kit.git
cd fcp-creator-kit
pip install -r requirements.txt
```

### 2. Coordinate Calibration

Get the coordinates of the FCP text input field to match your Mac's screen resolution.

```bash
python scripts/get_mouse_positions.py
```

Set the obtained coordinates to `INPUT_X, INPUT_Y` etc. in each script.

### 3A. Synthetic Voice Route

1. Place your scenario CSV in `csv_input/` (see `sample.csv`)
2. Auto-generate audio with AquesTalk Player:

```bash
python scripts/auto_aques_talk_player.py
```

3. Rename WAV files in `wav_output/` (move number to front so FCP sorts them correctly):

```bash
python scripts/swap_title_number.py
```

4. Import WAV files into FCP and select a text clip
5. Auto-insert subtitles:

```bash
python scripts/auto_fcp_telop_split_paste.py
```

### 3B. Narration Route

1. Place audio files in `audio_input/`
2. Transcribe with Whisper:

```bash
python scripts/auto_audio_to_vtt.py
```

3. Copy the generated VTT from `vtt_output/` to `vtt_input/` and review/edit
4. Check for timestamp overlaps:

```bash
python scripts/vtt_timestamp_checker.py
```

5. Auto-insert subtitles in FCP (supports both VTT and SRT):

```bash
python scripts/auto_fcp_vtt_srt_to_telop.py
```

### 3C. YouTube Chapter Generation

Auto-generate a YouTube chapter list from FCP markers.

#### How to Extract FCPXML

When you export from FCP via "File" → "Export XML...", a file with the `.fcpxmld` extension is created. This is a **compressed package** and cannot be read directly.

Right-click the `.fcpxmld` file in Finder → select "**Show Package Contents**", and you will find `info.fcpxml` inside. Copy this file to the `xml_input/` folder.

```
your_project.fcpxmld/   ← Right-click → "Show Package Contents"
└── info.fcpxml          ← Copy this to xml_input/
```

#### Run

```bash
python scripts/convert_xml_to_chapter.py
```

The chapter list is output to `xml_output/info_chapters.txt`. All `marker` and `chapter-marker` elements on the timeline are processed. If the first marker is not at `00:00`, an `Introduction` entry is automatically prepended.

---

### 4. Replace Subtitle Text

If clips are already split and you only want to paste new dialogue, use `auto_fcp_telop_paste.py`. This is useful for replacing Japanese dialogue with English, for example.

For narration recordings, set `LIVE_VOICE = True`.

---

## CSV Format (Synthetic Voice Route)

Used by `auto_aques_talk_player.py`. The CSV can be edited in Numbers or Excel. Installing a CSV extension in an IDE like VS Code is also recommended.

| Column | Description | Example |
|---|---|---|
| `実行` | 1 = execute, 0 = skip | `1` |
| `キャラクター` | Character name (for filtering) | `Marisa` |
| `セリフ` | Text to be read aloud | `Hello` |

```csv
実行,キャラクター,セリフ
1,魔理沙,皆さんこんにちは。
1,魔理沙,今回は動画制作の効率化について紹介します。
0,魔理沙,このセリフはスキップされます。
```

---

## Requirements

- macOS (an environment where Final Cut Pro runs)
- Python 3.10 or higher
- Final Cut Pro (with a text clip template placed in advance)

---

## Detailed Guide & Workflow

A detailed article covering script configuration, template creation, and efficiency techniques cultivated through 300+ videos is available.

👉 **[Final Cut Pro × Python Video Production Automation Bible (note)](https://note.com/YOUR_NOTE_URL)**

---

## License

MIT License — Free for both personal and commercial use.

---

## Author

I use this toolkit to produce videos on my YouTube channel.

- YouTube: [Channel](https://www.youtube.com/channel/UCPKMH4pEKMhZt7cNGfjoSRQ)
- X (Twitter): [@YOUR_HANDLE](https://x.com/YOUR_HANDLE)
- note: [YOUR_NOTE_URL](https://note.com/YOUR_NOTE_URL)
