#!/bin/bash

# Usage: ./extract_lang_subs.sh "input.mkv"

INPUT="$1"
if [ -z "$INPUT" ]; then
  echo "Usage: $0 <input.mkv>"
  exit 1
fi

# Function: Map codec to extension
get_extension() {
  case "$1" in
    subrip) echo "srt" ;;
    ass) echo "ass" ;;
    mov_text) echo "txt" ;;
    webvtt) echo "vtt" ;;
    dvb_subtitle) echo "sub" ;;
    hdmv_pgs_subtitle) echo "sup" ;;
    *) echo "$1" ;; # fallback
  esac
}

# Use ffprobe to get subtitle stream info line by line
ffprobe -v error -select_streams s \
  -show_entries stream=index,codec_name:stream_tags=language \
  -of csv=p=0 "$INPUT" | while IFS=',' read -r IDX CODEC LANG; do

  # Only extract if language is eng or vie
  if [[ "$LANG" == "eng" || "$LANG" == "vie" ]]; then
    EXT=$(get_extension "$CODEC")
    OUTFILE="subtitle_${IDX}_${LANG}.${EXT}"

    echo "Extracting stream 0:$IDX ($LANG, $CODEC) -> $OUTFILE"
    ffmpeg -i "$INPUT" -map "0:$IDX" -c copy "$OUTFILE"
  fi
done

