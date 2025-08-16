// This script runs immediately to prevent sidebar flash/shake on page load
(function() {
    // Get saved sidebar state
    var isCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
    
    if (isCollapsed) {
        // Add a class to the HTML element so CSS can apply the collapsed state immediately
        document.documentElement.classList.add('sidebar-preload-collapsed');
    }
})();
