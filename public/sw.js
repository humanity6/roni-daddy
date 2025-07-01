const CACHE_NAME = 'pimp-my-case-v1';
const urlsToCache = [
  '/',
  '/manifest.json',
  '/phone-template.png'
  // Removed routes that might not exist to prevent caching errors
];

// Install event - cache resources with error handling
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('Opened cache');
        // Cache resources individually to handle failures gracefully
        return Promise.allSettled(
          urlsToCache.map(url => 
            fetch(url).then(response => {
              if (response.ok) {
                return cache.put(url, response);
              }
              console.warn(`Failed to cache ${url}: ${response.status}`);
            }).catch(error => {
              console.warn(`Failed to fetch ${url}:`, error);
            })
          )
        );
      })
      .catch(error => {
        console.error('Cache installation failed:', error);
      })
  );
});

// Fetch event - serve from cache when offline
self.addEventListener('fetch', (event) => {
  // Skip caching for API requests
  if (event.request.url.includes(':8000') || event.request.url.includes('api')) {
    return;
  }

  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        // Return cached version or fetch from network
        if (response) {
          return response;
        }
        return fetch(event.request).catch(() => {
          // Return a fallback response for offline scenarios
          if (event.request.destination === 'document') {
            return caches.match('/');
          }
        });
      })
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