/* Service worker voor Data & AI Radar (GitHub Pages, onder /data-ai-radar/).
 *
 * Cachestrategie:
 * - Pagina, feed.json en manifest: eerst netwerk, cache alleen als je offline bent.
 *   Een nieuwe deployment is dus direct zichtbaar zodra je online bent.
 * - Iconen: eerst cache (veranderen zelden; nieuwe build = nieuwe cache).
 * - Andere domeinen (zoals Google Fonts) worden niet onderschept.
 *
 * BUILD wordt bij elke deployment ingevuld door scripts/make_site.py. Daardoor verandert dit
 * bestand per deployment, installeert de browser de nieuwe versie en ruimt oude caches op.
 */
const BUILD = "__BUILD__";
const CACHE = `radar-${BUILD}`;
const PRECACHE = ["./", "index.html", "feed.json", "manifest.webmanifest",
  "icons/icon-192.png", "icons/icon-512.png", "icons/icon-maskable-512.png", "icons/favicon-32.png"];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE)
      .then((c) => Promise.all(PRECACHE.map((u) => c.add(new Request(u, { cache: "reload" })).catch(() => {}))))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k.startsWith("radar-") && k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

async function networkFirst(request) {
  const cache = await caches.open(CACHE);
  try {
    const fresh = await fetch(request, { cache: "no-store" });
    if (fresh.ok) cache.put(request, fresh.clone());
    return fresh;
  } catch (err) {
    const cached = await cache.match(request, { ignoreSearch: true });
    if (cached) return cached;
    if (request.mode === "navigate") {
      const shell = await cache.match("./") || await cache.match("index.html");
      if (shell) return shell;
    }
    throw err;
  }
}

async function cacheFirst(request) {
  const cache = await caches.open(CACHE);
  const cached = await cache.match(request);
  if (cached) return cached;
  const fresh = await fetch(request);
  if (fresh.ok) cache.put(request, fresh.clone());
  return fresh;
}

self.addEventListener("fetch", (event) => {
  const { request } = event;
  if (request.method !== "GET") return;
  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;
  const scope = new URL(self.registration.scope);
  if (!url.pathname.startsWith(scope.pathname)) return;
  if (url.pathname.includes("/icons/")) {
    event.respondWith(cacheFirst(request));
  } else {
    event.respondWith(networkFirst(request));
  }
});
