    document.addEventListener('DOMContentLoaded', function () {
        const toastElList = document.querySelectorAll('.toast');

        toastElList.forEach(function (toastEl) {
            const delay = 4000; // 3 seconds

            // Set progress animation duration dynamically
            const progressBar = toastEl.querySelector('.toast-progress');
            if (progressBar) {
                progressBar.style.animationDuration = delay + 'ms';
            }

            const toast = new bootstrap.Toast(toastEl, {
                delay: delay,
                autohide: true
            });

            toast.show();
        });
    });