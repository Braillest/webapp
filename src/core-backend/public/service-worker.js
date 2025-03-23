// This script acts as a middle man between browser and server.
// Its purpose is to intercept events between the two in such a manner that a browser can retain some functionality during a server downtime
// https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open('symfony-pwa-cache').then((cache) => {
            return cache.addAll([
                '/',
                '/offline',
                // '/build/app.css',
                // '/build/app.js',
                '/favicon.ico',
                '/icons/entropy-square-192x192.png',
                '/icons/entropy-square-256x256.png',
                '/icons/entropy-square-512x512.png'
            ]);
        })
    );
});

self.addEventListener('fetch', (event) => {
    event.respondWith(
        caches.match(event.request).then((response) => {
            return response || fetch(event.request);
        })
    );
});

self.addEventListener('push', event => {
    const data = event.data ? event.data.json() : {};
    self.registration.showNotification(data.title, {
        body: data.body,
        icon: '/icons/entropy-square-256x256.png'
    });
});
