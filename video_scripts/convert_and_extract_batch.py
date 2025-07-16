#!/usr/bin/env python3
import os
import re
import subprocess
import argparse
from pathlib import Path
from tqdm import tqdm

def find_year(filename):
    """Tìm năm đầu tiên (19xx hoặc 20xx)"""
    match = re.search(r'(19\d{2}|20\d{2})', filename)
    return match.group(1) if match else None

def convert_video(input_path, output_path):
    print(f"Converting: {input_path} -> {output_path.name}")
    cmd = [
        "HandBrakeCLI",
        "--preset=H.265 MKV 720p30",
        "-i", str(input_path),
        "-o", str(output_path)
    ]
    subprocess.run(cmd, check=True)

def extract_and_rename_subtitles(input_path, output_basename, output_dir):
    print(f"Extracting subtitles from: {input_path.name}")
    cmd = [
        "ffprobe", "-v", "error", "-select_streams", "s",
        "-show_entries", "stream=index,codec_name:stream_tags=language",
        "-of", "csv=p=0", str(input_path)
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, check=True, text=True)
    lines = result.stdout.strip().splitlines()

    for line in lines:
        idx, codec, lang = line.split(',')
        if lang not in ("eng", "vie"):
            continue

        ext_map = {
            "subrip": "srt",
            "ass": "ass",
            "mov_text": "txt",
            "webvtt": "vtt",
            "dvb_subtitle": "sub",
            "hdmv_pgs_subtitle": "sup"
        }
        ext = ext_map.get(codec, codec)
        tmp_name = f"subtitle_{idx}_{lang}.{ext}"

        print(f"  Extracting stream 0:{idx} ({lang}, {codec}) -> {tmp_name}")
        extract_cmd = [
            "ffmpeg", "-i", str(input_path),
            "-map", f"0:{idx}",
            "-c", "copy", tmp_name
        ]
        subprocess.run(extract_cmd, check=True)

        lang_suffix = ".en" if lang == "eng" else ".vi"
        final_name = f"{output_basename}{lang_suffix}.{ext}"
        final_path = output_dir / final_name
        print(f"  Renaming {tmp_name} -> {final_path.name}")
        os.rename(tmp_name, final_path)

def main():
    parser = argparse.ArgumentParser(description="Batch convert & extract subtitles")
    parser.add_argument("input_dir", help="Input folder containing MKV files")
    parser.add_argument("output_dir", help="Output folder to save converted files & subtitles")
    parser.add_argument("--recursive", action="store_true", help="Recursively search subdirectories")
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Chọn glob hoặc rglob dựa vào --recursive
    if args.recursive:
        files = list(input_dir.rglob("*.mkv"))
    else:
        files = list(input_dir.glob("*.mkv"))

    print(f"Found {len(files)} mkv files in {input_dir} (recursive={args.recursive})")

    for file in tqdm(files, desc="Processing files"):
        if "264" not in file.name:
            print(f"Skipping {file} (does not contain '264')")
            continue

        year = find_year(file.stem)
        if year:
            basename = file.stem.split(year, 1)[0] + year
        else:
            basename = file.stem

        output_video_name = f"{basename}.720p.BluRay.AAC2.0.x265-NR.mkv"
        output_video_path = output_dir / output_video_name

        try:
            convert_video(file, output_video_path)
            extract_and_rename_subtitles(file, f"{basename}.720p.BluRay.AAC2.0.x265-NR", output_dir)
        except subprocess.CalledProcessError as e:
            print(f"Error processing {file}: {e}")
            continue

    print("All done!")

if __name__ == "__main__":
    main()
