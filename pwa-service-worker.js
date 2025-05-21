const CACHE_NAME = 'sndr-cache-v1';

// Files to cache for offline use
const urlsToCache = [
  '/',
  '/login',
  '/register',
  '/static/css/style.css',
  '/static/js/notifications.js',
  '/static/js/notifications-fallback.js',
  '/static/img/icon-512x512.png',
  '/static/img/notification-icon.png',
  '/static/sound/notification.mp3',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js',
  'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css',
  'https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap'
];

// Install event - cache essential files
self.addEventListener('install', event => {
  console.log('[Service Worker] Installing Service Worker...', event);
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('[Service Worker] Caching app shell');
        return cache.addAll(urlsToCache);
      })
      .then(() => {
        console.log('[Service Worker] Install completed');
        return self.skipWaiting();
      })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
  console.log('[Service Worker] Activating Service Worker...', event);
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cache => {
          if (cache !== CACHE_NAME) {
            console.log('[Service Worker] Clearing old cache:', cache);
            return caches.delete(cache);
          }
        })
      );
    }).then(() => {
      console.log('[Service Worker] Claiming clients');
      return self.clients.claim();
    })
  );
});

// Fetch event - serve cached content when offline
self.addEventListener('fetch', event => {
  // Skip cross-origin requests
  if (event.request.url.startsWith(self.location.origin) || 
      event.request.url.includes('cdn.jsdelivr.net') || 
      event.request.url.includes('cdnjs.cloudflare.com') ||
      event.request.url.includes('fonts.googleapis.com')) {
    
    // For API calls, try network first, then cache
    if (event.request.url.includes('/api/') || 
        event.request.url.includes('/check_messages') ||
        event.request.url.includes('/subscribe')) {
      
      event.respondWith(
        fetch(event.request)
          .then(response => {
            // Clone the response so we can save a copy in cache
            const responseToCache = response.clone();
            
            caches.open(CACHE_NAME)
              .then(cache => {
                cache.put(event.request, responseToCache);
              });
            
            return response;
          })
          .catch(() => {
            // If network fails, try from cache
            return caches.match(event.request);
          })
      );
    } 
    // For regular page requests, try cache first, then network
    else {
      event.respondWith(
        caches.match(event.request)
          .then(response => {
            if (response) {
              // If found in cache, return it
              return response;
            }
            
            // Otherwise, fetch from network
            return fetch(event.request)
              .then(response => {
                // Don't cache if response is not valid
                if (!response || response.status !== 200 || response.type !== 'basic') {
                  return response;
                }
                
                // Clone response to put in cache
                const responseToCache = response.clone();
                
                caches.open(CACHE_NAME)
                  .then(cache => {
                    cache.put(event.request, responseToCache);
                  });
                
                return response;
              });
          })
      );
    }
  }
});

// Push event for notifications
self.addEventListener('push', event => {
  console.log('[Service Worker] Push received', event);
  
  let notification = {};
  
  try {
    notification = event.data.json();
  } catch (e) {
    notification = {
      title: 'New Message',
      body: 'You have a new anonymous message!',
      icon: '/static/img/notification-icon.png',
      badge: '/static/img/notification-badge.png',
      url: '/inbox'
    };
  }
  
  const options = {
    body: notification.body || 'You have a new message!',
    icon: notification.icon || '/static/img/notification-icon.png',
    badge: notification.badge || '/static/img/notification-badge.png',
    vibrate: [100, 50, 100],
    data: {
      url: notification.url || '/inbox'
    },
    actions: [
      {
        action: 'view',
        title: 'View Message',
        icon: '/static/img/view-icon.png'
      }
    ]
  };
  
  event.waitUntil(
    self.registration.showNotification(notification.title || 'Sndr', options)
  );
});

// Notification click event
self.addEventListener('notificationclick', event => {
  console.log('[Service Worker] Notification click:', event);
  
  event.notification.close();
  
  // Open the clicked notification
  if (event.action === 'view' || !event.action) {
    const urlToOpen = event.notification.data && event.notification.data.url 
      ? new URL(event.notification.data.url, self.location.origin).href
      : '/inbox';
      
    event.waitUntil(
      clients.matchAll({
        type: 'window',
        includeUncontrolled: true
      })
      .then(clientList => {
        // Check if a window is already open
        for (let client of clientList) {
          if (client.url === urlToOpen && 'focus' in client) {
            return client.focus();
          }
        }
        
        // Otherwise, open a new window
        if (clients.openWindow) {
          return clients.openWindow(urlToOpen);
        }
      })
    );
  }
});

// Handle sync events for offline functionality
self.addEventListener('sync', event => {
  console.log('[Service Worker] Background Sync', event);
  
  if (event.tag === 'sync-messages') {
    event.waitUntil(
      // Get all the messages that need to be sent from IndexedDB
      // and send them to the server
      self.clients.matchAll().then(clients => {
        clients.forEach(client => {
          client.postMessage({
            type: 'SYNC_COMPLETE',
            tag: event.tag
          });
        });
      })
    );
  }
}); 