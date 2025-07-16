#!/bin/bash

# Usage: ./convert_and_extract.sh <input_file> <base_name>
# Example:
# ./convert_and_extract.sh Valentines.Day.2010.720p.BluRay.DTS.x264-HiDt.mkv Valentines.Day.2010

if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <input_file> <base_name>"
  exit 1
fi

INPUT="$1"
BASENAME="$2"

# Step 1: Convert video
OUTPUT="${BASENAME}.720p.BluRay.AAC2.0.x265-NR.mkv"
echo "Converting to $OUTPUT ..."
HandBrakeCLI --preset="H.265 MKV 720p30" -i "$INPUT" -o "$OUTPUT"

# Step 2: Extract subtitles (only eng and vie)
echo "Extracting subtitles from $INPUT ..."
ffprobe -v error -select_streams s \
  -show_entries stream=index,codec_name:stream_tags=language \
  -of csv=p=0 "$INPUT" | while IFS=',' read -r IDX CODEC LANG; do

  if [[ "$LANG" == "eng" || "$LANG" == "vie" ]]; then
    # Determine extension
    case "$CODEC" in
      subrip) EXT="srt" ;;
      ass) EXT="ass" ;;
      mov_text) EXT="txt" ;;
      webvtt) EXT="vtt" ;;
      dvb_subtitle) EXT="sub" ;;
      hdmv_pgs_subtitle) EXT="sup" ;;
      *) EXT="$CODEC" ;;
    esac

    # tmp output name
    TMP_OUT="subtitle_${IDX}_${LANG}.${EXT}"
    echo "Extracting stream 0:$IDX ($LANG, $CODEC) -> $TMP_OUT"
    ffmpeg -i "$INPUT" -map "0:$IDX" -c copy "$TMP_OUT"

    # Step 3: Rename to proper name
    if [ "$LANG" == "eng" ]; then
      FINAL_OUT="${BASENAME}.720p.BluRay.AAC2.0.x265-NR.en.${EXT}"
    else
      FINAL_OUT="${BASENAME}.720p.BluRay.AAC2.0.x265-NR.vi.${EXT}"
    fi
    echo "Renaming $TMP_OUT -> $FINAL_OUT"
    mv "$TMP_OUT" "$FINAL_OUT"
  fi
done

echo "Done!"

