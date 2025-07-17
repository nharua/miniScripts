# FLAC to MP3 Conversion Tools with Metadata Support

This collection of scripts helps you convert `.flac` music albums to properly tagged `.mp3` files, supporting both:
- **Multi-track `.flac` folders** (e.g., CD1/CD2)
- **Single large `.flac` files with embedded CUE metadata**

Cover art embedding and metadata tagging are handled automatically.

---

## Scripts Overview

### `convert_flac_mp3.py` (Main Script)
A flexible and powerful CLI tool that converts `.flac` files to `.mp3` with metadata and cover art.

Supports:
- CUE-based splitting of a large `.flac` file
- Recursively converting a folder of `.flac` files (multi-disc albums)
- Automatic tagging and cover embedding

---

### `extract_metadata.py`
Extracts metadata and cover art from a single `.flac` file and generates a structured `info.json` file with tracklist (for CUE-style albums).

---

### `requirements.txt`
Python dependencies needed to run the scripts. Includes:
- `eyed3`
- `python-slugify`
- `titlecase`
- (and more…)

---

## Prerequisites

Before using the scripts, ensure you have the following installed and available in your system’s `PATH`:

- [Python 3.8+](https://www.python.org/)
- [FFmpeg](https://ffmpeg.org/)
- Required Python packages:

```bash
pip install -r requirements.txt
```

---

## Usage

### 1. Convert a folder of `.flac` files (multi-disc)

This mode scans all `.flac` files recursively under a given path and converts them with consistent track numbering.

```bash
python convert_flac_mp3.py -p /path/to/folder -m info.json
```

Example:

```bash
python convert_flac_mp3.py -p ./Elton_John_BestOf -m info.json
```

---

### 2. Convert a single `.flac` file with cue metadata

Use this if your `.flac` is one big file with multiple tracks defined in cue metadata.

```bash
python convert_flac_mp3.py -f big_album.flac -m info.json
```

---

### 3. Extract metadata and cover art

To generate `info.json` from a `.flac` file with embedded cue information:

```bash
python extract_metadata.py big_album.flac
```

This will output:
- `info.json` — structured metadata with album info and track list
- `folder.jpg` — extracted cover art if available

---

## Output

- All `.mp3` files are saved in `output_mp3/` subdirectory by default
- Files are named like:

```
01. Your Song - Elton John.mp3
02. Rocket Man - Elton John.mp3
...
```

Each file is tagged with:
- Title
- Artist
- Album
- Track number
- Genre
- Year
- Cover art (if available)

---

## Help

```bash
python convert_flac_mp3.py -h
```

---

## Example Directory Structure

```
Elton John - The Very Best Of Elton John/
├── CD1/
│   ├── 01. Your Song.flac
│   ├── 02. Rocket Man.flac
│   └── folder.jpg
├── CD2/
│   ├── 01. I'm Still Standing.flac
│   ├── 02. Nikita.flac
├── info.json
├── convert_flac_mp3.py
```

---

## License

MIT or your preferred open source license.
