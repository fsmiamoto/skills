#!/usr/bin/env bash
# Trim a recording and export an optimized GIF + MP4.
#
#   finalize.sh <video.webm> --name my-demo [--from 0.8] [--to 34]
#               [--dest ~/Downloads] [--gif-width 1200] [--fps 12] [--no-gif] [--no-mp4]
set -euo pipefail

video="" name="" from="0" to="" dest="$HOME/Downloads" gifw=1200 fps=12 gif=1 mp4=1
while [[ $# -gt 0 ]]; do
  case "$1" in
    --name) name="$2"; shift 2 ;;
    --from) from="$2"; shift 2 ;;
    --to) to="$2"; shift 2 ;;
    --dest) dest="$2"; shift 2 ;;
    --gif-width) gifw="$2"; shift 2 ;;
    --fps) fps="$2"; shift 2 ;;
    --no-gif) gif=0; shift ;;
    --no-mp4) mp4=0; shift ;;
    -h|--help) sed -n '2,5p' "$0"; exit 0 ;;
    *) video="$1"; shift ;;
  esac
done
[[ -n "$video" && -f "$video" && -n "$name" ]] || { echo "usage: finalize.sh <video> --name NAME [--from S] [--to S] [--dest DIR] [--gif-width PX] [--fps N] [--no-gif] [--no-mp4]" >&2; exit 1; }
mkdir -p "$dest"

trim=(-ss "$from")
[[ -n "$to" ]] && trim+=(-to "$to")

if [[ $mp4 -eq 1 ]]; then
  ffmpeg -v error -y "${trim[@]}" -i "$video" \
    -c:v libx264 -pix_fmt yuv420p -crf 22 -preset slow -movflags +faststart \
    -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" "$dest/$name.mp4"
fi
if [[ $gif -eq 1 ]]; then
  # Two-pass palette (diff stats + bayer dither) keeps text crisp at a sane size.
  ffmpeg -v error -y "${trim[@]}" -i "$video" \
    -vf "fps=${fps},scale=${gifw}:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=200:stats_mode=diff[p];[b][p]paletteuse=dither=bayer:bayer_scale=4:diff_mode=rectangle" \
    "$dest/$name.gif"
fi

for f in "$dest/$name.mp4" "$dest/$name.gif"; do
  [[ -f "$f" ]] || continue
  d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$f" 2>/dev/null || echo "?")
  printf "%s  %s  %.1fs\n" "$(du -h "$f" | cut -f1)" "$f" "$d"
done
