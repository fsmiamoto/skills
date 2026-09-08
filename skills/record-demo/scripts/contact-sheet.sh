#!/usr/bin/env bash
# Sample frames from a video into a grid PNG for visual QA.
#
#   contact-sheet.sh <video> [--n 12] [--cols 4] [--width 480] [--at 1,5.5,9] [--out sheet.png]
#
# Prints a position -> timestamp legend (ffmpeg here has no drawtext).
set -euo pipefail

video="" n=12 cols=4 width=480 at="" out=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --n) n="$2"; shift 2 ;;
    --cols) cols="$2"; shift 2 ;;
    --width) width="$2"; shift 2 ;;
    --at) at="$2"; shift 2 ;;
    --out) out="$2"; shift 2 ;;
    -h|--help) sed -n '2,7p' "$0"; exit 0 ;;
    *) video="$1"; shift ;;
  esac
done
[[ -n "$video" && -f "$video" ]] || { echo "usage: contact-sheet.sh <video> [--n N] [--cols N] [--width PX] [--at s,s,...] [--out PNG]" >&2; exit 1; }
out="${out:-$(dirname "$video")/sheet.png}"

dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$video")
if [[ -z "$at" ]]; then
  # Evenly spaced, skipping the very first/last frame (often blank / static).
  at=$(awk -v d="$dur" -v n="$n" 'BEGIN{for(i=0;i<n;i++){printf "%s%.2f",(i?",":""),(d*(i+0.5))/n}}')
fi

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
i=0
IFS=',' read -ra stamps <<<"$at"
for t in "${stamps[@]}"; do
  ffmpeg -v error -y -ss "$t" -i "$video" -frames:v 1 -vf "scale=${width}:-2" "$tmp/f_$(printf %03d $i).png"
  i=$((i+1))
done
rows=$(( (i + cols - 1) / cols ))
ffmpeg -v error -y -framerate 1 -i "$tmp/f_%03d.png" -vf "tile=${cols}x${rows}:padding=4:margin=4:color=0x222222" -frames:v 1 "$out"

echo "sheet: $out  (${i} frames, ${cols} cols, video ${dur}s)"
echo "legend (row,col -> seconds):"
for ((k=0; k<i; k++)); do
  printf "  r%d c%d  %6.2fs\n" $((k/cols+1)) $((k%cols+1)) "${stamps[$k]}"
done
echo "read this image: $out"
