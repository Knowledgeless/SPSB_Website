document.addEventListener("DOMContentLoaded", function () {

    // ===============================
    // 🎨 COLOR ENGINE (UNIFIED SYSTEM)
    // ===============================
    function colorFromString(value) {
        const str = String(value).trim();

        let hash = 0;
        for (let i = 0; i < str.length; i++) {
            hash = (hash * 31 + str.charCodeAt(i)) >>> 0;
        }

        // Golden angle distribution → visually balanced colors
        const hue = (hash * 137.508) % 360;

        return `hsl(${hue}, 70%, 55%)`;
    }

    // ===============================
    // 🎨 FIXED STATIC PALETTE (for news)
    // ===============================
    const newsColors = [
        '#00bf6c',  // published
        '#ff002f',  // archived
        '#ffae00'   // draft
    ];

    // ===============================
    // 📰 NEWS DOUGHNUT CHART
    // ===============================
    const newsEl = document.getElementById('newsChart');

    if (newsEl) {
        new Chart(newsEl, {
            type: 'doughnut',
            data: {
                labels: ['Published', 'Archived', 'Draft'],
                datasets: [{
                    data: [newsPublished, newsArchived, newsDraft],
                    backgroundColor: newsColors,
                    borderWidth: 0,
                    hoverOffset: 12
                }]
            },
            options: {
                cutout: '60%',
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: 'white' }
                    }
                }
            }
        });
    }

    // ===============================
    // 👥 VOLUNTEER DOUGHNUT CHART
    // ===============================
    const volunteerEl = document.getElementById('volunteerChart');

    if (volunteerEl) {
        new Chart(volunteerEl, {
            type: 'doughnut',
            data: {
                labels: ['Active', 'Past', 'Inactive'],
                datasets: [{
                    data: [volunteerActive, volunteerPast, volunteerInactive],
                    backgroundColor: [
                        '#4F46E5',
                        '#06B6D4',
                        '#F97316'
                    ],
                    borderWidth: 0,
                    hoverOffset: 12
                }]
            },
            options: {
                cutout: '60%',
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: 'white' }
                    }
                }
            }
        });
    }

    // ===============================
    // 📊 YEARLY BAR CHART
    // ===============================
    const yearEl = document.getElementById('yearChart');

    if (yearEl) {
        new Chart(yearEl, {
            type: 'bar',
            data: {
                labels: yearLabels.map(String),

                datasets: [{
                    label: 'Volunteers',
                    data: yearValues,

                    // 🎯 AUTO UNIQUE COLOR PER YEAR
                    backgroundColor: yearLabels.map(year =>
                        colorFromString(year)
                    ),

                    borderRadius: 8
                }]
            },

            options: {
                responsive: true,

                scales: {
                    x: {
                        ticks: { color: 'white' }
                    },
                    y: {
                        ticks: { color: 'white' },
                        beginAtZero: true
                    }
                },

                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }

});