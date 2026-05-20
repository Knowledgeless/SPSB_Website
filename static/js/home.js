
// ===============================
// 1. REVEAL ANIMATION (LEFT / RIGHT)
// ===============================

const revealElements = document.querySelectorAll(
    '.reveal-left, .reveal-right'
);

const revealObserver = new IntersectionObserver((entries) => {

    entries.forEach(entry => {

        if (entry.isIntersecting) {
            entry.target.classList.add('active');
        }

    });

}, {
    threshold: 0.2
});

revealElements.forEach(el => {
    revealObserver.observe(el);
});



// ===============================
// 2. COUNTER ANIMATION
// ===============================

const counters = document.querySelectorAll('.counter');

const startCounting = (counter) => {
    const target = +counter.getAttribute('data-target');
    let count = 0;

    const speed = Math.ceil(target / 100);

    const updateCount = () => {
        count += speed;

        if (count < target) {
            counter.innerText = count;
            requestAnimationFrame(updateCount);
        } else {
            counter.innerText = target;
        }
    };

    updateCount();
};


// Separate observer for counters
const counterObserver = new IntersectionObserver((entries, observer) => {

    entries.forEach(entry => {

        if (entry.isIntersecting) {
            startCounting(entry.target);
            observer.unobserve(entry.target);
        }

    });

}, {
    threshold: 0.6
});

counters.forEach(counter => {
    counterObserver.observe(counter);
});