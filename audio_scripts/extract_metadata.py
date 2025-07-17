import subprocess
import json
import sys
import re
from pathlib import Path


def extract_cover(flac_path: Path, output_jpg: Path = Path("folder.jpg")):
    if output_jpg.exists():
        print("🖼️  folder.jpg already exists. Skipping cover extract.")
        return
    try:
        subprocess.run(
            ["ffmpeg", "-i", str(flac_path), "-an", "-vcodec", "copy", str(output_jpg)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
        print(f"✅ Extracted cover art to {output_jpg}")
    except subprocess.CalledProcessError:
        print("⚠️  No embedded cover art found or extraction failed.")


def extract_info(flac_path: Path, output_json: Path = Path("info.json")) -> None:
    result = subprocess.run(
        ["ffmpeg", "-i", str(flac_path)],
        stderr=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        text=True,
    )
    metadata_raw = result.stderr

    if not metadata_raw:
        print(f"❌ ffmpeg failed to extract metadata from {flac_path}")
        return

    album = re.search(r"ALBUM\s*:\s*(.+)", metadata_raw, re.IGNORECASE)
    album_artist = re.search(r"album_artist\s*:\s*(.+)", metadata_raw, re.IGNORECASE)
    if not album_artist:
        album_artist = re.search(
            r"ALBUM ARTIST\s*:\s*(.+)", metadata_raw, re.IGNORECASE
        )
    artist = re.search(r"ARTIST\s*:\s*(.+)", metadata_raw, re.IGNORECASE)
    if not artist:
        artist = re.search(r"PERFORMER\s*:\s*(.+)", metadata_raw, re.IGNORECASE)

    genre = re.search(r"GENRE\s*:\s*(.+)", metadata_raw, re.IGNORECASE)
    if not genre:
        genre = re.search(r'REM GENRE\s+"([^"]+)"', metadata_raw, re.IGNORECASE)
    if not genre:
        genre = re.search(r"REM GENRE\s+(.+)", metadata_raw, re.IGNORECASE)
    year = re.search(r"DATE\s*:\s*(\d{4})", metadata_raw, re.IGNORECASE)
    if not year:
        year = re.search(r'REM DATE\s+"?(\d{4})"?', metadata_raw, re.IGNORECASE)
    cuesheet = re.findall(
        r'TRACK\s+(\d+)\s+AUDIO.*?TITLE\s+"(.+?)".*?INDEX 01\s+(\d+:\d+:\d+)',
        metadata_raw,
        re.DOTALL | re.IGNORECASE,
    )

    info = {
        "album": album.group(1).strip() if album else "",
        "album_artist": album_artist.group(1).strip() if album_artist else "",
        "artist": artist.group(1).strip() if artist else "",
        "genre": genre.group(1).strip() if genre else "",
        "year": year.group(1).strip() if year else "",
        "tracks": [
            {"track": int(num), "title": title.strip(), "start": index.strip()}
            for num, title, index in cuesheet
        ],
    }

    try:
        with output_json.open("w", encoding="utf-8") as f:
            json.dump(info, f, indent=2, ensure_ascii=False)
        print(f"✅ Saved metadata to {output_json}")
    except Exception as e:
        print(f"❌ Failed to write metadata: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python convert_flac_mp3.py file.flac")
        sys.exit(1)

    flac_file = Path(sys.argv[1])
    if not flac_file.exists():
        print(f"❌ File not found: {flac_file}")
        sys.exit(1)

    extract_info(flac_file)
    extract_cover(flac_file)
