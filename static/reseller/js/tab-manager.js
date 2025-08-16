// tab-manager.js

// Tab persistence
document.addEventListener('DOMContentLoaded', function() {
    // Restore active tab from localStorage
    const savedTab = localStorage.getItem('commissionActiveTab');
    if (savedTab) {
        const tabTrigger = document.querySelector(`button[data-bs-target="${savedTab}"]`);
        if (tabTrigger) {
            new bootstrap.Tab(tabTrigger).show();
        }
    }
    
    // Save active tab to localStorage
    const tabButtons = document.querySelectorAll('#commissionTabs button[data-bs-toggle="tab"]');
    tabButtons.forEach(button => {
        button.addEventListener('shown.bs.tab', function(event) {
            localStorage.setItem('commissionActiveTab', event.target.getAttribute('data-bs-target'));
        });
    });
    
    // Initialize filter functionality when DOM is ready
    const statusFilter = document.getElementById('statusFilter');
    const monthFilter = document.getElementById('monthFilter');
    
    if (statusFilter) {
        statusFilter.addEventListener('change', applyFilters);
    }
    
    if (monthFilter) {
        monthFilter.addEventListener('change', applyFilters);
    }
});

function applyFilters() {
    const status = document.getElementById('statusFilter').value;
    const month = document.getElementById('monthFilter').value;
    const params = new URLSearchParams(window.location.search);
    
    if (status) params.set('status', status);
    else params.delete('status');
    
    if (month) params.set('month', month);
    else params.delete('month');
    
    // Preserve current tab
    params.set('tab', 'transactions');
    
    window.location.search = params.toString();
}

// Refresh data
function refreshData() {
    location.reload();
}

// Download statement
function downloadStatement() {
    // Implement download logic
    console.log('Downloading commission statement...');
    window.location.href = '/reseller/commissions/download/';
}

