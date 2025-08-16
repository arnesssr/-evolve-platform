document.addEventListener("DOMContentLoaded", function () {
  new Chart(document.getElementById('referralChart'), {
    type: 'line',
    data: {
      labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
      datasets: [{
        label: 'Referrals',
        data: [10, 15, 12, 20, 18],
        borderColor: '#0a2463',
        fill: true,
        tension: 0.4
      }]
    }
  });

  new Chart(document.getElementById('salesChart'), {
    type: 'doughnut',
    data: {
      labels: ['Payroll', 'SACCO', 'ERP'],
      datasets: [{
        data: [40, 30, 30],
        backgroundColor: ['#0a2463', '#1e3b8a', '#3e78b2']
      }]
    }
  });
});
