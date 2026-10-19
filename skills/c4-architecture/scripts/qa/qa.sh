#!/bin/sh
# Visual QA for a served C4 page: text overflow/collisions, horizontal scroll at 1440/1024, screenshots.
# Usage: qa.sh URL OUTDIR     (URL must be http(s); serve the page first, e.g. python3 -m http.server)
# Prints a JSON report. Pass = overflow [] , collisions [] , scrollWidth equal to each viewport width.
set -eu
[ $# -eq 2 ] || { echo "usage: $0 URL OUTDIR" >&2; exit 2; }
url=$1; out=$(mkdir -p "$2" && cd "$2" && pwd)
here=$(cd "$(dirname "$0")" && pwd)
work=$(mktemp -d "${TMPDIR:-/tmp}/c4qa.XXXXXX"); tmp=$work/qa.js
trap 'playwright-cli -s=c4qa close >/dev/null 2>&1 || true; rm -rf "$work"' EXIT
sed -e "s|__URL__|$url|g" -e "s|__OUT__|$out|g" "$here/qa.js" > "$tmp"
cd "$work"  # playwright-cli writes its .playwright-cli/ logs into the cwd; keep them out of OUTDIR
playwright-cli -s=c4qa open >/dev/null
# keep only the returned JSON (run-code also echoes the script and page info)
playwright-cli -s=c4qa run-code --filename="$tmp" | awk '/^### Result/{on=1;next} /^### /{on=0} on' | python3 -c '
import json, sys
raw = sys.stdin.read().strip()
try:
    r = json.loads(json.loads(raw))
except ValueError:
    sys.exit("qa.js failed:\n" + raw)
print(json.dumps(r, indent=1))
ok = not r["overflow"] and not r["collisions"] and all(int(w) == v for w, v in r["scrollWidth"].items())
print("PASS" if ok else "FAIL", "-", len(r["shots"]), "shots in", sys.argv[1])
sys.exit(0 if ok else 1)
' "$out"
