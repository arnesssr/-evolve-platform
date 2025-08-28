// This script runs immediately to prevent sidebar flash/shake on page load
(function() {
    // Only apply preload collapse on desktop to avoid hiding the sidebar when loading on mobile
    var isDesktop = window.matchMedia('(min-width: 992px)').matches;
    var isCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
    if (isDesktop && isCollapsed) {
        // Add a class to the HTML element so CSS can apply the collapsed state immediately
        document.documentElement.classList.add('sidebar-preload-collapsed');
    }
})();
