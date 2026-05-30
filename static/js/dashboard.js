document.addEventListener("DOMContentLoaded", function () {

    // News Pie Chart
    new Chart(document.getElementById('newsChart'), {
        type: 'pie',
        data: {
            labels: ['Published', 'Archived', 'Draft'],
            datasets: [{
                data: [
                    newsPublished,
                    newsArchived,
                    newsDraft
                ],
                backgroundColor: [
                    '#16a34a',
                    '#dc2626',
                    '#334155'
                ]
            }]
        }
    });

    // Volunteer Pie Chart
    new Chart(document.getElementById('volunteerChart'), {
        type: 'pie',
        data: {
            labels: ['Active', 'Past', 'Inactive'],
            datasets: [{
                data: [
                    volunteerActive,
                    volunteerPast,
                    volunteerInactive
                ],
                backgroundColor: [
                    '#2563eb',
                    '#7c3aed',
                    '#f59e0b'
                ]
            }]
        }
    });

    // Yearly Bar Chart
    new Chart(document.getElementById('yearChart'), {
        type: 'bar',
        data: {
            labels: yearLabels,
            datasets: [{
                label: 'Volunteers',
                data: yearValues,
                backgroundColor: '#2563eb'
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });

});