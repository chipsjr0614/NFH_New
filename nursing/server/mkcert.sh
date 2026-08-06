#!/bin/bash
# 자체 서명 인증서 만들기 — 병원 내부망은 인터넷이 막혀 있어 Let's Encrypt 를 못 쓴다.
#
#   ./mkcert.sh              → 이 맥의 IP 를 자동으로 잡는다
#   ./mkcert.sh 192.168.0.35 → IP 를 직접 준다
#
# 만들어지는 것 (certs/ 안)
#   ca.crt      폰에 설치할 인증서       ← 이것만 폰으로 보낸다
#   ca.key      CA 개인키 (맥에만 둔다)
#   server.crt  서버 인증서
#   server.key  서버 개인키
set -e
cd "$(dirname "$0")"

IP="${1:-$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null)}"
if [ -z "$IP" ]; then
  echo "❌ IP 를 못 찾았습니다. 직접 주세요:  ./mkcert.sh 192.168.0.35"; exit 1
fi

mkdir -p certs && cd certs
echo "▸ IP  $IP"

# ── ① CA (한 번 만들면 10년 쓴다. 폰에 설치하는 건 이것) ──
if [ ! -f ca.key ]; then
  openssl genrsa -out ca.key 2048 2>/dev/null
  openssl req -x509 -new -nodes -key ca.key -sha256 -days 3650 -out ca.crt \
    -subj "/CN=NFH 간호기록 내부망 CA/O=NFH" 2>/dev/null
  echo "▸ CA 만듦 (10년)"
else
  echo "▸ CA 이미 있음 — 그대로 씀 (폰 재설치 안 해도 됨)"
fi

# ── ② 서버 인증서 ──
# ★ iOS 는 398일 넘는 서버 인증서를 거부한다. 그래서 397일.
#   1년에 한 번 이 스크립트를 다시 돌리면 된다 (CA 는 그대로라 폰은 안 건드림).
# ★ iOS 는 CN 을 안 본다. SAN 에 IP 가 반드시 있어야 한다.
cat > san.cnf <<EOF
[req]
distinguished_name=dn
[dn]
[ext]
subjectAltName=IP:$IP,DNS:localhost
keyUsage=critical,digitalSignature,keyEncipherment
extendedKeyUsage=serverAuth
basicConstraints=critical,CA:FALSE
EOF

openssl genrsa -out server.key 2048 2>/dev/null
openssl req -new -key server.key -out server.csr -subj "/CN=$IP" 2>/dev/null
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial \
  -out server.crt -days 397 -sha256 -extfile san.cnf -extensions ext 2>/dev/null
rm -f server.csr san.cnf ca.srl

echo "▸ 서버 인증서 만듦 (397일 — 매년 이 스크립트만 다시 돌리세요)"
echo
echo "확인:"
openssl x509 -in server.crt -noout -dates -ext subjectAltName | sed 's/^/   /'
echo
echo "다음 → ./serve.sh 로 서버를 켜세요"
