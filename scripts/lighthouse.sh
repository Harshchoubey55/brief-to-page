#!/usr/bin/env bash
# Run Lighthouse (mobile preset) three times against the built page and keep
# the median run. Needs Node and Chrome.
#
#   ./scripts/lighthouse.sh first-pass
#   ./scripts/lighthouse.sh final
set -euo pipefail

label="${1:?give the run a label, e.g. first-pass}"
port=8765
out="reports/lighthouse/$label"
mkdir -p "$out"

python3 -m http.server "$port" --directory docs >/dev/null 2>&1 &
server=$!
trap 'kill $server' EXIT
sleep 1

for i in 1 2 3; do
  npx --yes lighthouse@12 "http://localhost:$port/" \
    --quiet \
    --chrome-flags="--headless=new --no-sandbox" \
    --only-categories=performance,accessibility,best-practices,seo \
    --output=json --output=html \
    --output-path="$out/run-$i"
done

python3 scripts/lighthouse_summary.py "$out"
