// console.log("not working");

document.addEventListener('DOMContentLoaded', function () {
    
        //for sticky navbar after scroll
        const nav = document.querySelector(".my-nav");
        window.addEventListener("scroll", function () {
            if (window.scrollY > 50) {
                nav.classList.add("sticky-active");
            } else {
                nav.classList.remove("sticky-active");
            }
        });
});