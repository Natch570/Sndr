// Fallback notification system that works without browser permissions
// Uses polling to check for new messages periodically

let lastCheckedTime = localStorage.getItem('lastMessageCheck') || 0;
let notificationSound = null;
let checkInterval = 30000; // Check every 30 seconds by default

// Initialize audio for notification sound
function initNotificationSound() {
    notificationSound = new Audio('/static/sound/notification.mp3');
}

// Check for new messages via AJAX
async function checkForNewMessages() {
    try {
        const response = await fetch('/check_messages?since=' + lastCheckedTime);
        const data = await response.json();
        
        if (data.success) {
            // Update last checked time
            lastCheckedTime = data.current_time;
            localStorage.setItem('lastMessageCheck', lastCheckedTime);
            
            // If new messages, show notification
            if (data.new_messages > 0) {
                showLocalNotification(data.new_messages);
            }
        }
    } catch (error) {
        console.error('Error checking for messages:', error);
    }
}

// Show in-app notification
function showLocalNotification(messageCount) {
    // Play sound if available
    if (notificationSound) {
        notificationSound.play().catch(e => console.log('Could not play notification sound', e));
    }
    
    // Create or update notification element
    let notificationContainer = document.getElementById('local-notification');
    
    if (!notificationContainer) {
        notificationContainer = document.createElement('div');
        notificationContainer.id = 'local-notification';
        notificationContainer.className = 'local-notification';
        document.body.appendChild(notificationContainer);
        
        // Add styles if not already defined in CSS
        if (!document.getElementById('notification-styles')) {
            const style = document.createElement('style');
            style.id = 'notification-styles';
            style.textContent = `
                .local-notification {
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    background-color: #ff69b4;
                    color: white;
                    padding: 15px;
                    border-radius: 5px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.2);
                    z-index: 9999;
                    display: flex;
                    align-items: center;
                    cursor: pointer;
                    animation: slideIn 0.3s forwards;
                }
                
                @keyframes slideIn {
                    from { transform: translateX(100px); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
                
                .local-notification-icon {
                    margin-right: 10px;
                    font-size: 20px;
                }
                
                .local-notification-count {
                    display: inline-block;
                    background-color: white;
                    color: #ff69b4;
                    border-radius: 50%;
                    width: 24px;
                    height: 24px;
                    line-height: 24px;
                    text-align: center;
                    font-weight: bold;
                    margin-left: 10px;
                }
            `;
            document.head.appendChild(style);
        }
    }
    
    // Update notification content
    const message = messageCount === 1 
        ? "You received a new message!"
        : `You received ${messageCount} new messages!`;
        
    notificationContainer.innerHTML = `
        <div class="local-notification-icon">
            <i class="fas fa-envelope"></i>
        </div>
        <div>
            ${message}
            <div class="local-notification-count">${messageCount}</div>
        </div>
    `;
    
    // Make notification clickable to go to inbox
    notificationContainer.onclick = function() {
        window.location.href = '/inbox/' + currentUsername;
        notificationContainer.remove();
    };
    
    // Auto-dismiss after 10 seconds
    setTimeout(() => {
        if (notificationContainer && notificationContainer.parentNode) {
            notificationContainer.parentNode.removeChild(notificationContainer);
        }
    }, 10000);
}

// Start the periodic check
function startMessagePolling() {
    // Set current username from global variable if available
    currentUsername = window.currentUsername || '';
    
    // Initialize notification sound
    initNotificationSound();
    
    // Check immediately on page load
    checkForNewMessages();
    
    // Then start regular interval
    setInterval(checkForNewMessages, checkInterval);
    
    console.log('Message polling started. Checking every', checkInterval/1000, 'seconds');
}

// Start polling when the page loads
document.addEventListener('DOMContentLoaded', startMessagePolling); 