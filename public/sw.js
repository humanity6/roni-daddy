const CACHE_NAME = 'pimp-my-case-v1';
const urlsToCache = [
  '/',
  '/welcome',
  '/phone-brand',
  '/phone-model',
  '/template-selection',
  '/phone-preview',
  '/text-input',
  '/font-selection',
  '/text-color-selection',
  '/phone-back-preview',
  '/retry',
  '/payment',
  '/queue',
  '/completion',
  '/manifest.json',
  '/ui-mockups/logo.png',
  '/phone-template.png',
  '/phone-template-dark-edges.png',
  '/phone-template-white-edges.png'
];

// Install event - cache resources
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('Opened cache');
        return cache.addAll(urlsToCache);
      })
  );
});

// Fetch event - serve from cache when offline
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        // Return cached version or fetch from network
        if (response) {
          return response;
        }
        return fetch(event.request);
      }
    )
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            console.log('Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

// Handle push notifications (for order updates)
self.addEventListener('push', (event) => {
  const options = {
    body: event.data ? event.data.text() : 'Your phone case order has been updated!',
    icon: '/ui-mockups/logo.png',
    badge: '/ui-mockups/logo.png',
    vibrate: [100, 50, 100],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: '1'
    },
    actions: [
      {
        action: 'view',
        title: 'View Order',
        icon: '/ui-mockups/logo.png'
      },
      {
        action: 'close',
        title: 'Close',
        icon: '/ui-mockups/logo.png'
      }
    ]
  };

  event.waitUntil(
    self.registration.showNotification('PIMP MY CASE®', options)
  );
});

// Handle notification clicks
self.addEventListener('notificationclick', (event) => {
  event.notification.close();

  if (event.action === 'view') {
    event.waitUntil(
      clients.openWindow('/queue')
    );
  }
}); 