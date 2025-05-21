// Notifications Script
let pushSubscription = null;

// Function to convert URL Base64 to Uint8Array
function urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding)
        .replace(/-/g, '+')
        .replace(/_/g, '/');
    
    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);
    
    for (let i = 0; i < rawData.length; ++i) {
        outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
}

// Application Server Public Key
const applicationServerPublicKey = 'BPGqX5Vf4teDWVXYBU_1kSztDWSzA1PzUx5vY6isS_dsDeTEwZHfB9G_RV9J_n7lrIXRQrIxiFMxtptHXe5A6yQ';

// Register Service Worker
async function registerServiceWorker() {
    if ('serviceWorker' in navigator && 'PushManager' in window) {
        try {
            const registration = await navigator.serviceWorker.register('/service-worker.js');
            console.log('ServiceWorker registered with scope:', registration.scope);
            return registration;
        } catch (error) {
            console.error('ServiceWorker registration failed:', error);
            showNotificationError('Error registering service worker. This may be due to running on HTTP instead of HTTPS.');
        }
    } else {
        console.warn('Push notifications not supported by this browser');
        showNotificationError('Your browser does not support push notifications.');
    }
}

// Subscribe to Push Notifications
async function subscribeToPushNotifications(registration) {
    try {
        // Check if already subscribed
        pushSubscription = await registration.pushManager.getSubscription();
        
        if (pushSubscription) {
            console.log('User is already subscribed');
            showNotificationSuccess('You are already subscribed to notifications!');
            return pushSubscription;
        }
        
        // Subscribe user
        pushSubscription = await registration.pushManager.subscribe({
            userVisibleOnly: true,
            applicationServerKey: urlBase64ToUint8Array(applicationServerPublicKey)
        });
        
        console.log('User is now subscribed');
        showNotificationSuccess('Notifications enabled successfully!');
        
        // Send subscription to server
        await sendSubscriptionToServer(pushSubscription);
        
        return pushSubscription;
    } catch (error) {
        console.error('Failed to subscribe user:', error);
        if (error.name === 'NotAllowedError') {
            showNotificationError('You denied notification permissions. You can change this in your browser settings. <a href="#" onclick="showPermissionHelp(); return false;">Learn how</a>');
        } else {
            showNotificationError('Error enabling notifications. This may be because you\'re using HTTP instead of HTTPS.');
        }
    }
}

// Send subscription to server
async function sendSubscriptionToServer(subscription) {
    try {
        const response = await fetch('/subscribe', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                subscription: subscription
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to store subscription on server');
        }
        
        return response.json();
    } catch (error) {
        console.error('Error sending subscription to server:', error);
        showNotificationError('Could not save notification settings on the server.');
    }
}

// Show notification status message
function showNotificationStatus(message, isError = false) {
    const notificationPermission = document.getElementById('notification-permission');
    const statusElement = document.getElementById('notification-status');
    
    if (!statusElement) {
        // Create status element if it doesn't exist
        const newStatusElement = document.createElement('div');
        newStatusElement.id = 'notification-status';
        newStatusElement.className = isError ? 'alert alert-danger mt-2 mb-0' : 'alert alert-success mt-2 mb-0';
        newStatusElement.innerHTML = message;
        
        // Insert before the last button
        const lastButton = notificationPermission.querySelector('button:last-child');
        notificationPermission.insertBefore(newStatusElement, lastButton);
    } else {
        // Update existing status
        statusElement.className = isError ? 'alert alert-danger mt-2 mb-0' : 'alert alert-success mt-2 mb-0';
        statusElement.innerHTML = message;
    }
    
    // Show the notification permission element
    notificationPermission.classList.remove('d-none');
}

function showNotificationError(message) {
    showNotificationStatus(message, true);
}

function showNotificationSuccess(message) {
    showNotificationStatus(message, false);
}

// Show help for enabling permissions
function showPermissionHelp() {
    const browserName = detectBrowser();
    let helpMessage = '';
    
    switch(browserName) {
        case 'Chrome':
            helpMessage = `
                <strong>How to enable notifications in Chrome:</strong><br>
                1. Click the lock/info icon in the address bar<br>
                2. Click on "Site settings"<br>
                3. Find "Notifications" and change to "Allow"
            `;
            break;
        case 'Firefox':
            helpMessage = `
                <strong>How to enable notifications in Firefox:</strong><br>
                1. Click the permission icon in the address bar<br>
                2. Switch "Notifications" to "Allow"
            `;
            break;
        case 'Edge':
            helpMessage = `
                <strong>How to enable notifications in Edge:</strong><br>
                1. Click the lock/info icon in the address bar<br>
                2. Click on "Site permissions"<br>
                3. Find "Notifications" and change to "Allow"
            `;
            break;
        default:
            helpMessage = `
                <strong>How to enable notifications:</strong><br>
                Check your browser settings to allow notifications for this site.
            `;
    }
    
    // Create modal with help instructions
    const modalHtml = `
        <div class="modal fade" id="permissionHelpModal" tabindex="-1" aria-hidden="true">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Enable Notification Permissions</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        ${helpMessage}
                        <hr>
                        <p>After changing permissions, refresh the page and try again.</p>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Add modal to document if it doesn't exist
    if (!document.getElementById('permissionHelpModal')) {
        const modalContainer = document.createElement('div');
        modalContainer.innerHTML = modalHtml;
        document.body.appendChild(modalContainer.firstElementChild);
    }
    
    // Show the modal
    const modal = new bootstrap.Modal(document.getElementById('permissionHelpModal'));
    modal.show();
}

// Detect browser
function detectBrowser() {
    const userAgent = navigator.userAgent;
    if (userAgent.indexOf("Chrome") > -1) {
        return "Chrome";
    } else if (userAgent.indexOf("Firefox") > -1) {
        return "Firefox";
    } else if (userAgent.indexOf("Edge") > -1) {
        return "Edge";
    } else if (userAgent.indexOf("Safari") > -1) {
        return "Safari";
    } else {
        return "Unknown";
    }
}

// Initialize Push Notifications
async function initializePushNotifications() {
    const notificationPermission = document.getElementById('notification-permission');
    
    if (Notification.permission === 'granted') {
        // Register service worker if permission already granted
        const registration = await registerServiceWorker();
        if (registration) {
            await subscribeToPushNotifications(registration);
            notificationPermission.classList.add('d-none');
        }
    } else if (Notification.permission === 'denied') {
        // Show error if already denied
        showNotificationError('You denied notification permissions. You can change this in your browser settings. <a href="#" onclick="showPermissionHelp(); return false;">Learn how</a>');
    } else {
        // Show permission request dialog
        notificationPermission.classList.remove('d-none');
    }
}

// Handle Permission Button Click
function requestNotificationPermission() {
    Notification.requestPermission().then(permission => {
        if (permission === 'granted') {
            console.log('Notification permission granted');
            
            registerServiceWorker().then(registration => {
                if (registration) {
                    subscribeToPushNotifications(registration);
                }
            });
        } else if (permission === 'denied') {
            console.log('Notification permission denied');
            showNotificationError('You denied notification permissions. You can change this in your browser settings. <a href="#" onclick="showPermissionHelp(); return false;">Learn how</a>');
        } else {
            console.log('Notification permission dismissed');
            showNotificationError('You dismissed the notification permission. Please try again.');
        }
    });
}

// Make functions global for HTML access
window.showPermissionHelp = showPermissionHelp;

// Initialize on page load
document.addEventListener('DOMContentLoaded', initializePushNotifications);

// Handle permission button click
const permissionButton = document.getElementById('request-notification-permission');
if (permissionButton) {
    permissionButton.addEventListener('click', requestNotificationPermission);
} 