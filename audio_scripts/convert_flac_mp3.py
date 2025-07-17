import argparse
import subprocess
import eyed3
import json
from pathlib import Path
from slugify import slugify
import re
from titlecase import titlecase


def cue_index_to_seconds(index_str):
    mm, ss, ff = map(int, index_str.split(":"))
    return mm * 60 + ss + ff / 75.0


def find_cover_for_file(path: Path) -> Path | None:
    for name in ["folder.jpg", "cover.jpg", "Folder.jpg", "Cover.jpg"]:
        candidate = path.parent / name if path.is_file() else path / name
        if candidate.exists():
            return candidate
    return None


def get_metadata_from_flac(file_path: Path) -> dict:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format_tags",
            "-of",
            "json",
            str(file_path),
        ],
        capture_output=True,
        text=True,
    )
    data = json.loads(result.stdout)
    tags = {k.lower(): v for k, v in data.get("format", {}).get("tags", {}).items()}

    return {
        "title": tags.get("title"),
        "artist": tags.get("artist"),
        "album": tags.get("album"),
        "album_artist": tags.get("album_artist"),
        "track": int(tags.get("track", "0").split("/")[0]) if "track" in tags else None,
        "genre": tags.get("genre"),
        "year": tags.get("date") or tags.get("year"),
    }


def tag_mp3(mp3_path, tag_info, cover_path=None):
    audiofile = eyed3.load(str(mp3_path))
    if not audiofile or not audiofile.tag:
        audiofile.initTag()

    tag = audiofile.tag
    tag.title = tag_info["title"]
    tag.artist = tag_info["artist"]
    tag.album = tag_info["album"]
    tag.album_artist = tag_info["album_artist"]
    tag.track_num = tag_info["track_num"]
    tag.genre = tag_info["genre"]

    year = tag_info.get("year")
    if year:
        match = re.match(r"(\d{4})", str(year))
        if match:
            tag.recording_date = eyed3.core.Date(int(match.group(1)))

    if cover_path and cover_path.exists():
        with open(cover_path, "rb") as img:
            tag.images.set(
                eyed3.id3.frames.ImageFrame.FRONT_COVER,
                img.read(),
                "image/jpeg",
                "Cover (front)",
            )

    tag.save(version=eyed3.id3.ID3_V2_3)


def convert_cue_flac(info_path: Path, flac_file: Path):
    with open(info_path, "r", encoding="utf-8") as f:
        info = json.load(f)

    output_dir = Path("output_mp3")
    output_dir.mkdir(exist_ok=True)
    total_tracks = len(info["tracks"])
    cover = find_cover_for_file(flac_file)

    for i, track in enumerate(info["tracks"]):
        title = titlecase(track["title"])
        start_sec = cue_index_to_seconds(track["start"])

        # Duration
        if i < total_tracks - 1:
            end_sec = cue_index_to_seconds(info["tracks"][i + 1]["start"])
            duration = end_sec - start_sec
        else:
            duration = None

        filename = f"{track['track']:02d}.{slugify(title, separator=' ', lowercase=False)} - {info['artist']}.mp3"
        output_path = output_dir / filename

        cmd = [
            "ffmpeg",
            "-y",
            "-ss",
            str(start_sec),
            "-i",
            str(flac_file),
            "-t",
            str(duration) if duration else "9999",
            "-codec:a",
            "libmp3lame",
            "-qscale:a",
            "2",
            str(output_path),
        ]
        print(f"🎧 Converting: {filename}")
        subprocess.run(
            cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )

        tag_info = {
            "title": title,
            "artist": info.get("artist", ""),
            "album": titlecase(info.get("album", "")),
            "album_artist": info.get("album_artist", ""),
            "track_num": (track["track"], total_tracks),
            "genre": info.get("genre", ""),
            "year": info.get("year"),
        }
        tag_mp3(output_path, tag_info, cover)

    print(f"\n✅ Done! MP3 saved to: {output_dir.resolve()}")


def convert_flac_folder(info_path: Path, base_folder: Path):
    with open(info_path, "r", encoding="utf-8") as f:
        default_info = json.load(f)

    output_dir = base_folder / "output_mp3"
    output_dir.mkdir(exist_ok=True)

    flac_files = sorted(base_folder.rglob("*.flac"), key=lambda f: f.name)
    track_counter = 1

    for flac_file in flac_files:
        meta = get_metadata_from_flac(flac_file)
        title = titlecase(meta["title"] or flac_file.stem)
        artist = meta["artist"] or default_info.get("artist", "")
        album = titlecase(meta["album"] or default_info.get("album", ""))
        album_artist = meta["album_artist"] or default_info.get("album_artist", "")
        year = meta["year"] or default_info.get("year", "")
        genre = meta["genre"] or default_info.get("genre", "")

        filename = f"{track_counter:02d}.{slugify(title, separator=' ', lowercase=False)} - {artist}.mp3"
        output_path = output_dir / filename

        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            str(flac_file),
            "-codec:a",
            "libmp3lame",
            "-qscale:a",
            "2",
            str(output_path),
        ]
        print(f"🎧 Converting: {filename}")
        subprocess.run(
            cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )

        tag_info = {
            "title": title,
            "artist": artist,
            "album": album,
            "album_artist": album_artist,
            "track_num": track_counter,
            "genre": genre,
            "year": year,
        }
        cover = find_cover_for_file(flac_file)
        tag_mp3(output_path, tag_info, cover)

        track_counter += 1

    print(f"\n✅ Done! Converted {track_counter - 1} tracks to: {output_dir.resolve()}")


def main():
    parser = argparse.ArgumentParser(description="Convert FLAC to MP3 with tagging.")
    parser.add_argument("-f", "--flac", type=Path, help="Single FLAC file (big album)")
    parser.add_argument(
        "-p", "--path", type=Path, help="Folder with multiple FLAC files"
    )
    parser.add_argument(
        "-m",
        "--meta",
        type=Path,
        required=True,
        help="Path to metadata JSON (info.json)",
    )

    args = parser.parse_args()

    if args.flac and args.path:
        print("❌ Cannot use both --flac and --path at the same time.")
        return

    if args.flac:
        convert_cue_flac(args.meta, args.flac)
    elif args.path:
        convert_flac_folder(args.meta, args.path)
    else:
        print("❌ Must specify either --flac or --path")
        parser.print_help()


if __name__ == "__main__":
    main()
