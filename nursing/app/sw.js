/* 간호기록 오프라인 캐시
 *
 * 맥미니가 꺼져도, Wi-Fi 가 끊겨도 앱이 열리게 한다.
 * https 에서만 동작한다 — Service Worker 는 보안 컨텍스트를 요구한다.
 *
 * ★ 「네트워크 먼저」 방식이다.
 *   앱을 하루에도 여러 번 고치므로, 서버가 살아 있으면 늘 새 파일을 쓴다.
 *   서버가 죽었거나 Wi-Fi 가 없을 때만 캐시를 꺼낸다.
 *   캐시 먼저 쓰면 고친 것이 폰에 안 내려간다.
 */
const CACHE = 'nfh-v1';

self.addEventListener('install', e => {
  self.skipWaiting();                       // 새 버전을 기다리지 않고 바로 쓴다
});

self.addEventListener('activate', e => {
  e.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)));
    await self.clients.claim();
  })());
});

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;

  e.respondWith((async () => {
    try {
      const res = await fetch(req);           // ① 서버가 살아 있으면 새 것
      if (res && res.ok) {
        const c = await caches.open(CACHE);
        c.put(req, res.clone());              //    받은 김에 저장해 둔다
      }
      return res;
    } catch (err) {
      const hit = await caches.match(req);    // ② 서버가 죽었으면 저장해 둔 것
      if (hit) return hit;
      // 목록 페이지를 찾는 중이면 앱이라도 내준다
      const app = await caches.match('간호기록V7.html');
      if (app && req.mode === 'navigate') return app;
      throw err;
    }
  })());
});
