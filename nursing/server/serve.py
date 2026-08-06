#!/usr/bin/env python3
"""간호기록 내부망 서버 — https(앱) + http(인증서 배포)를 같이 띄운다.

  https://<IP>:8443   앱 · 복사와 오프라인이 여기서만 제대로 된다
  http://<IP>:8000    인증서 받는 곳 · 폰 설정 안내

폰은 먼저 http 로 들어와 인증서를 깔고, 그 다음 https 로 옮겨간다.
인증서를 https 로 주면 「인증서를 못 믿어서 인증서를 못 받는」 닭과 달걀이 된다.
"""
import http.server, socketserver, ssl, threading, subprocess, sys, os, functools

HERE = os.path.dirname(os.path.abspath(__file__))
APP  = os.path.abspath(os.path.join(HERE, '..', 'app'))
CERT = os.path.join(HERE, 'certs')
HTTPS_PORT, HTTP_PORT = 8443, 8000


def my_ip():
    for dev in ('en0', 'en1'):
        try:
            ip = subprocess.check_output(['ipconfig', 'getifaddr', dev],
                                         stderr=subprocess.DEVNULL).decode().strip()
            if ip:
                return ip
        except Exception:
            pass
    return '127.0.0.1'


IP = sys.argv[1] if len(sys.argv) > 1 else my_ip()

GUIDE = f"""<!doctype html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>간호기록 — 폰 설정</title>
<style>
 body{{margin:0;background:#F2F5F5;color:#0E1516;font:16px/1.65 -apple-system,BlinkMacSystemFont,"Apple SD Gothic Neo",sans-serif;
   padding:env(safe-area-inset-top) 0 env(safe-area-inset-bottom)}}
 .w{{max-width:560px;margin:0 auto;padding:30px 18px 70px}}
 h1{{font-size:24px;font-weight:800;letter-spacing:-.02em;margin:0 0 6px}}
 .s{{color:#758584;font-size:14px;margin:0 0 26px}}
 ol{{padding-left:0;list-style:none;counter-reset:n;margin:0}}
 li{{counter-increment:n;background:#fff;border:1px solid #D3DCDB;border-radius:14px;
   padding:16px 18px 16px 54px;margin-bottom:11px;position:relative}}
 li::before{{content:counter(n);position:absolute;left:16px;top:16px;width:26px;height:26px;
   background:#0F5F62;color:#fff;border-radius:50%;display:flex;align-items:center;
   justify-content:center;font-size:14px;font-weight:800}}
 li b{{display:block;font-size:16.5px;font-weight:800;letter-spacing:-.015em;margin-bottom:3px}}
 li span{{font-size:14px;color:#495858}}
 a.dl{{display:block;background:#0F5F62;color:#fff;text-align:center;border-radius:13px;
   padding:16px;font-size:17px;font-weight:800;text-decoration:none;margin:22px 0}}
 a.go{{display:block;border:1.5px solid #0F5F62;color:#0F5F62;text-align:center;border-radius:13px;
   padding:15px;font-size:16px;font-weight:800;text-decoration:none;margin-top:20px}}
 .warn{{background:#FCEBE1;border:1px solid #C2410C;border-radius:12px;padding:14px 16px;
   font-size:14px;margin-top:22px}}
 code{{background:#F7F9F9;border:1px solid #E4EBEA;border-radius:5px;padding:1px 6px;font-size:13.5px}}
</style></head><body><div class="w">
<h1>간호기록 — 폰 설정</h1>
<p class="s">한 번만 하면 됩니다. 3~5분 걸립니다.</p>

<a class="dl" href="/ca.crt">① 인증서 받기</a>

<ol>
<li><b>「허용」을 누릅니다</b><span>프로파일을 다운로드할지 물어봅니다.</span></li>
<li><b>설정 → 프로파일 다운로드됨</b><span>설정 앱 맨 위에 뜹니다. 눌러서 <b>설치</b> → 암호 → <b>설치</b>.</span></li>
<li><b>설정 → 일반 → 정보 → 인증서 신뢰 설정</b>
  <span>맨 아래에 있습니다. <b>NFH 간호기록 내부망 CA</b> 를 <b>켜세요</b>.
  이 단계를 빼먹으면 안 됩니다.</span></li>
<li><b>아래 버튼으로 앱 열기</b><span>Safari로 열립니다. 자물쇠가 보이면 성공입니다.</span></li>
<li><b>홈 화면에 추가</b><span>아래 공유 <b>⬆️</b> → 「홈 화면에 추가」. 앱처럼 전체화면으로 열립니다.</span></li>
</ol>

<a class="go" href="https://{IP}:{HTTPS_PORT}/">② 간호기록 열기 (https)</a>

<div class="warn">
<b>주소를 헷갈리지 마세요</b><br>
설정용 <code>http://{IP}:{HTTP_PORT}</code><br>
실제 앱 <code>https://{IP}:{HTTPS_PORT}</code><br>
앱은 반드시 <b>https</b> 로 여세요. http 로 열면 복사와 오프라인이 안 됩니다.
</div>
</div></body></html>"""


class Guide(http.server.SimpleHTTPRequestHandler):
    """http 쪽 — 안내 페이지와 인증서만 준다."""
    def do_GET(self):
        if self.path in ('/', '/index.html'):
            b = GUIDE.encode()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(b)))
            self.end_headers()
            self.wfile.write(b)
            return
        if self.path == '/ca.crt':
            p = os.path.join(CERT, 'ca.crt')
            if os.path.exists(p):
                b = open(p, 'rb').read()
                self.send_response(200)
                # iOS 가 프로파일로 받아들이게 하는 타입
                self.send_header('Content-Type', 'application/x-x509-ca-cert')
                self.send_header('Content-Length', str(len(b)))
                self.end_headers()
                self.wfile.write(b)
                return
        self.send_error(404)

    def log_message(self, *a):
        pass


class App(http.server.SimpleHTTPRequestHandler):
    """https 쪽 — 앱 파일. 캐시를 끄지 않으면 고친 게 폰에 안 내려간다."""
    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache')
        self.send_header('Service-Worker-Allowed', '/')
        super().end_headers()

    def log_message(self, *a):
        pass


class Reuse(socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True


def main():
    crt, key = os.path.join(CERT, 'server.crt'), os.path.join(CERT, 'server.key')
    if not (os.path.exists(crt) and os.path.exists(key)):
        print('❌ 인증서가 없습니다. 먼저 ./mkcert.sh 를 돌리세요.')
        sys.exit(1)

    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.load_cert_chain(crt, key)

    https = Reuse(('0.0.0.0', HTTPS_PORT), functools.partial(App, directory=APP))
    https.socket = ctx.wrap_socket(https.socket, server_side=True)
    http_ = Reuse(('0.0.0.0', HTTP_PORT), Guide)

    threading.Thread(target=http_.serve_forever, daemon=True).start()

    print()
    print('  ┌─────────────────────────────────────────────┐')
    print(f'  │  폰 설정   http://{IP}:{HTTP_PORT}'.ljust(48) + '│')
    print(f'  │  간호기록  https://{IP}:{HTTPS_PORT}'.ljust(48) + '│')
    print('  └─────────────────────────────────────────────┘')
    print()
    print('  처음 쓰는 폰은 「폰 설정」 주소로 먼저 들어가세요.')
    print('  끄려면 Control+C')
    print()
    try:
        https.serve_forever()
    except KeyboardInterrupt:
        print('\n  서버를 껐습니다.')


if __name__ == '__main__':
    main()
