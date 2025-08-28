// Dashboard Redesign JS
// Requires Chart.js (already loaded in base layout)

(function() {
  // Ensure we reuse/destroy existing Chart instances to avoid duplicates and growth
  function destroyExistingChart(el) {
    if (!el || typeof Chart === 'undefined') return;
    if (typeof Chart.getChart === 'function') {
      const existing = Chart.getChart(el);
      if (existing) existing.destroy();
    } else if (el._chart && typeof el._chart.destroy === 'function') {
      el._chart.destroy();
      el._chart = null;
    }
  }

  function createChart(el, config) {
    const ctx = el.getContext('2d');
    const chart = new Chart(ctx, config);
    // store reference for fallback reuse
    el._chart = chart;
    return chart;
  }

  function initRevenueChart() {
    const el = document.getElementById('revenueChart');
    if (!el || typeof Chart === 'undefined') return;
    destroyExistingChart(el);
    const labels = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'];
    const data = [1200, 1800, 900, 1500, 2100, 1900, 2300];
    createChart(el, {
      type: 'line',
      data: {
        labels,
        datasets: [{
          label: 'Earnings',
          data,
          borderColor: '#1e40af',
          backgroundColor: 'rgba(30, 64, 175, 0.08)',
          tension: 0.35,
          fill: true,
          pointRadius: 0
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          y: { beginAtZero: true, grid: { color: 'rgba(0,0,0,0.05)' } },
          x: { grid: { display: false } }
        }
      }
    });
  }

  function initTopProductsChart() {
    const el = document.getElementById('topProductsChart');
    if (!el || typeof Chart === 'undefined') return;
    destroyExistingChart(el);
    const labels = ['Gateway', 'POS', 'E‑commerce', 'Mobile'];
    const data = [42, 35, 28, 20];
    createChart(el, {
      type: 'bar',
      data: {
        labels,
        datasets: [{
          label: 'Sales',
          data,
          backgroundColor: ['#0ea5e9','#22c55e','#f59e0b','#6366f1']
        }]
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { beginAtZero: true, grid: { color: 'rgba(0,0,0,0.05)' } },
          y: { grid: { display: false } }
        }
      }
    });
  }

  function initSparkline(id, points, color) {
    const el = document.getElementById(id);
    if (!el || typeof Chart === 'undefined') return;
    destroyExistingChart(el);
    createChart(el, {
      type: 'line',
      data: { labels: points.map((_, i) => i+1), datasets: [{ data: points, borderColor: color, fill: false, tension: 0.35, pointRadius: 0, borderWidth: 2 }] },
      options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { x: { display: false }, y: { display: false } } }
    });
  }

  document.addEventListener('DOMContentLoaded', function() {
    initRevenueChart();
    initTopProductsChart();

    // Simple placeholder sparklines
    initSparkline('sparkActive', [5,7,6,8,9,10,9], '#22c55e');
    initSparkline('sparkRate',   [10,10.5,11,10.8,11.2,11.4,11.6], '#1e40af');
    initSparkline('sparkConv',   [3,4,4,5,4,5,6], '#f59e0b');
    initSparkline('sparkMRR',    [600,640,700,720,760,800,820], '#10b981');

    // Period selector (placeholder)
    const period = document.getElementById('periodSelect');
    if (period) {
      period.addEventListener('change', () => {
        // In a real app, trigger fetch/update of datasets
        // For now, no-op to avoid flicker
      });
    }
  });
})();

