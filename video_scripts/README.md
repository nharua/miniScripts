# Video Conversion and Subtitle Extraction Tools

This collection of scripts helps you convert videos from H.264 to H.265 (HEVC) and extract English/Vietnamese subtitles.

## Scripts Overview

* **`convert_and_extract_batch.py`**: The main script for batch processing. It can find `.mkv` files in a directory, convert them to H.265, and extracts `eng`/`vie` subtitles. **This is the recommended script for most uses.**
* **`convert_and_extract.sh`**: A simple shell script to convert a *single* video file and extract its subtitles.
* **`extract_sub.sh`**: A utility script to extract *only* the English and Vietnamese subtitles from a single video file without any video conversion.

## Prerequisites

Before you begin, make sure you have the following command-line tools installed and accessible in your system's PATH:

* **FFmpeg**
* **HandBrakeCLI**
* **Python 3**

## Quick Guide

### 1. Batch Convert and Extract (Recommended)

The Python script `convert_and_extract_batch.py` is the most powerful and flexible tool. It can process a folder of videos in one go.

**Usage**

```bash
python3 convert_and_extract_batch.py [input_directory] [output_directory] [options]
```

**Examples**

* To process all `.mkv` files in a folder named `input_videos` and save the results to `output_videos`:
    ```bash
    python3 convert_and_extract_batch.py ./input_videos ./output_videos
    ```

* To do the same, but also include videos in subdirectories:
    ```bash
    python3 convert_and_extract_batch.py ./input_videos ./output_videos --recursive
    ```

### 2. Convert a Single File

If you only need to process one file, you can use the `convert_and_extract.sh` shell script.

**Usage**

```bash
./convert_and_extract.sh <input_file.mkv> <base_output_name>
```


**Example**

```bash
./convert_and_extract.sh "My.Movie.2023.1080p.x264.mkv" "My.Movie.2023"
```

This will create:
* `My.Movie.2023.720p.BluRay.AAC2.0.x265-NR.mkv`
* `My.Movie.2023.720p.BluRay.AAC2.0.x265-NR.en.srt` (if English subtitles exist)
* `My.Movie.2023.720p.BluRay.AAC2.0.x265-NR.vi.srt` (if Vietnamese subtitles exist)

### 3. Extract Subtitles Only

If you don't want to convert the video and only need the subtitles, use `extract_sub.sh`.

**Usage**

```bash
./extract_sub.sh <input_file.mkv>
```


**Example**

```bash
./extract_sub.sh "Another.Movie.2021.mkv"
```

This will extract any English or Vietnamese subtitles into files in the current directory, such as `subtitle_2_eng.srt`.
