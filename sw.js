const CACHE_NAME = 'mindbox-v1';
const urlsToCache = [
  '/',
  '/static/css/style.css',
  '/static/css/profile.css',
  '/static/js/script.js',
  '/static/js/profile.js',
  '/static/js/charts.js',
  '/public/logo.png',
  '/public/favicon.ico',
  '/manifest.json'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => response || fetch(event.request))
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});