#!/bin/bash
# NFH 간호기록 — 내부망 서버 (맥미니용)
# 병원 내부망에서만 접근된다. 인터넷 연결 불필요.

PORT=8000
DIR="$(cd "$(dirname "$0")/../app" && pwd)"

cd "$DIR" || exit 1
echo "NFH 간호기록 서버"
echo "  폴더 : $DIR"
echo "  주소 : http://$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null || echo '???'):$PORT"
echo "  중지 : Control + C"
echo ""
exec /usr/bin/python3 -m http.server "$PORT" --bind 0.0.0.0
