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

# FIXED: Use file descriptor 3 to avoid stdin interference
exec 3< <(ffprobe -v error -select_streams s \
  -show_entries stream=index,codec_name:stream_tags=language \
  -of csv=p=0 "$INPUT")

while IFS=',' read -r IDX CODEC LANG <&3; do
  echo "Processing stream: IDX=$IDX, CODEC=$CODEC, LANG='$LANG'"
  
  # If language is empty, assume it's English (common for many files)
  if [ -z "$LANG" ]; then
    LANG="eng"
    echo "  -> No language tag found, assuming English"
  fi

  # Only extract if language is eng or vie
  if [[ "$LANG" == "eng" || "$LANG" == "vie" ]]; then
    EXT=$(get_extension "$CODEC")
    # Get base filename without extension
    BASENAME=$(basename "$INPUT" .mkv)
    OUTFILE="${BASENAME}.${IDX}.${LANG}.${EXT}"

    echo "  -> Extracting stream 0:$IDX ($LANG, $CODEC) -> $OUTFILE"
    # Use </dev/null to prevent ffmpeg from reading stdin
    ffmpeg -v quiet -i "$INPUT" -map "0:$IDX" -c copy "$OUTFILE" </dev/null
    
    if [ $? -eq 0 ]; then
      SIZE=$(stat -f%z "$OUTFILE" 2>/dev/null || stat -c%s "$OUTFILE" 2>/dev/null)
      echo "  ✅ SUCCESS: $SIZE bytes"
    else
      echo "  ❌ FAILED"
    fi
  else
    echo "  -> Skipping: language '$LANG' not in target list"
  fi
  echo
done

exec 3<&-  # Close file descriptor 3

echo "Extraction complete!"
