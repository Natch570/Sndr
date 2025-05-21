// PWA installation helper DISABLED for UptoDown Android app version
// This file is kept for reference but all installation functionality is disabled

// Empty event listener to prevent errors
window.addEventListener('beforeinstallprompt', (e) => {
  // Prevent default browser install behavior
  e.preventDefault();
  // Do nothing for UptoDown version
  console.log('PWA installation disabled for UptoDown version');
});

// Log installation attempts but take no action
window.addEventListener('appinstalled', (evt) => {
  console.log('App installation detected, but this is the UptoDown version');
});

// For backwards compatibility, provide empty functions
function installApp() {
  console.log('Installation disabled for UptoDown Android app version');
}

function manualInstall() {
  console.log('Manual installation disabled for UptoDown Android app version');
}

// No initialization on DOM load
document.addEventListener('DOMContentLoaded', function() {
  console.log('UptoDown Android app version - PWA installation disabled');
}); 