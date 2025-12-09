// Admin dashboard charts configuration

document.addEventListener('DOMContentLoaded', function() {
    // Check if Chart.js is loaded
    if (typeof Chart === 'undefined') {
        console.error('Chart.js is not loaded');
        return;
    }

    const chartColors = {
        blue: 'rgb(59, 130, 246)',
        green: 'rgb(34, 197, 94)',
        purple: 'rgb(168, 85, 247)',
        orange: 'rgb(249, 115, 22)',
        red: 'rgb(239, 68, 68)',
        yellow: 'rgb(234, 179, 8)',
        pink: 'rgb(236, 72, 153)',
        indigo: 'rgb(99, 102, 241)'
    };

    // Get chart data from data attributes or window object
    const registrationTrendData = window.registrationTrendData || [];
    const roleDistributionData = window.roleDistributionData || { admin: 0, doctor: 0, patient: 0 };
    const genderDistributionData = window.genderDistributionData || {};
    const bloodTypeDistributionData = window.bloodTypeDistributionData || {};

    // Daily Registration Trend Chart
    const registrationCanvas = document.getElementById('registrationTrendChart');
    if (registrationCanvas) {
        const registrationCtx = registrationCanvas.getContext('2d');
        new Chart(registrationCtx, {
            type: 'line',
            data: {
                labels: registrationTrendData.map(item => item.date),
                datasets: [{
                    label: 'New Users',
                    data: registrationTrendData.map(item => item.count),
                    borderColor: chartColors.blue,
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1,
                            font: {
                                size: 11
                            }
                        }
                    },
                    x: {
                        ticks: {
                            font: {
                                size: 11
                            }
                        }
                    }
                }
            }
        });
    }

    // Role Distribution Chart
    const roleCanvas = document.getElementById('roleDistributionChart');
    if (roleCanvas) {
        const roleCtx = roleCanvas.getContext('2d');
        new Chart(roleCtx, {
            type: 'doughnut',
            data: {
                labels: ['Admins', 'Doctors', 'Patients'],
                datasets: [{
                    data: [
                        roleDistributionData.admin,
                        roleDistributionData.doctor,
                        roleDistributionData.patient
                    ],
                    backgroundColor: [
                        chartColors.blue,
                        chartColors.green,
                        chartColors.purple
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            font: {
                                size: 11
                            },
                            padding: 10
                        }
                    }
                }
            }
        });
    }

    // Gender Distribution Chart
    const genderCanvas = document.getElementById('genderChart');
    if (genderCanvas) {
        const genderCtx = genderCanvas.getContext('2d');
        new Chart(genderCtx, {
            type: 'pie',
            data: {
                labels: Object.keys(genderDistributionData).map(g => g.charAt(0).toUpperCase() + g.slice(1)),
                datasets: [{
                    data: Object.values(genderDistributionData),
                    backgroundColor: [
                        chartColors.pink,
                        chartColors.blue,
                        chartColors.purple
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            font: {
                                size: 11
                            },
                            padding: 8
                        }
                    }
                }
            }
        });
    }

    // Blood Type Distribution Chart
    const bloodTypeCanvas = document.getElementById('bloodTypeChart');
    if (bloodTypeCanvas) {
        const bloodTypeCtx = bloodTypeCanvas.getContext('2d');
        new Chart(bloodTypeCtx, {
            type: 'bar',
            data: {
                labels: Object.keys(bloodTypeDistributionData),
                datasets: [{
                    label: 'Count',
                    data: Object.values(bloodTypeDistributionData),
                    backgroundColor: chartColors.red
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1,
                            font: {
                                size: 11
                            }
                        }
                    },
                    x: {
                        ticks: {
                            font: {
                                size: 11
                            }
                        }
                    }
                }
            }
        });
    }
});
