document.addEventListener("DOMContentLoaded", function () {

    const container = document.getElementById('formset-container');
    const addButton = document.getElementById('add-form');

    // Handle status button clicks
    document.querySelectorAll('.status-btn').forEach(btn => {
        btn.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelectorAll('.status-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
        });
    });

    // Handle category pill clicks
    document.querySelectorAll('.category-pill').forEach(pill => {
        pill.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelectorAll('.category-pill').forEach(p => p.classList.remove('active'));
            this.classList.add('active');
            // Clear the new category input when selecting existing category
            const newCatInput = document.querySelector('[name="new_category"]');
            if (newCatInput) {
                newCatInput.value = '';
            }
        });
    });

    // Handle new category input
    const newCatInput = document.querySelector('[name="new_category"]');
    if (newCatInput) {
        newCatInput.addEventListener('input', function () {
            if (this.value.trim()) {
                // Unselect all category pills when typing new category
                document.querySelectorAll('.category-pill').forEach(p => p.classList.remove('active'));
            }
        });
    }

    addButton.addEventListener('click', function () {
        const totalForms = document.getElementById('id_post_media-TOTAL_FORMS');
        let formCount = parseInt(totalForms.value, 10);

        let newForm = container.children[0].cloneNode(true);
        newForm.innerHTML = newForm.innerHTML.replace(/-\d+-/g, `-${formCount}-`);

        newForm.querySelectorAll('input, textarea').forEach(el => {
            if (el.type === 'checkbox') {
                el.checked = false;
            } else if (el.name && el.name.endsWith('-DELETE')) {
                el.checked = false;
            } else {
                el.value = '';
            }
        });

        newForm.querySelectorAll('img.preview-img').forEach(img => img.remove());

        const orderInput = newForm.querySelector('[name$="-order"]');
        if (orderInput) {
            orderInput.value = formCount;
        }

        const mediaInput = newForm.querySelector('[name$="-media"]');
        if (mediaInput) {
            mediaInput.value = '';
        }

        container.appendChild(newForm);
        totalForms.value = formCount + 1;
    });

    if (window.Sortable) {
        new Sortable(container, {
            animation: 150,
            onEnd: function () {
                document.querySelectorAll('.formset-item').forEach((item, index) => {
                    const orderInput = item.querySelector('[name$="-order"]');
                    if (orderInput) {
                        orderInput.value = index;
                    }
                });
            }
        });
    }

});


        let newForm = container.children[0].cloneNode(true);

        newForm.innerHTML = newForm.innerHTML.replace(/-\d+-/g, `-${formCount}-`);

        // CLEAR VALUES
        newForm.querySelectorAll('input, textarea').forEach(el => {
            if (el.type === "checkbox") el.checked = false;
            else el.value = "";
        });

        newForm.querySelector(".preview-container").innerHTML = "";

        container.appendChild(newForm);
        totalForms.value = formCount + 1;

        // 🔥 INIT NEW FORM
        initDropArea(newForm);
    });

    // SORTABLE
    if (window.Sortable) {
        new Sortable(document.getElementById('formset-container'), {
            animation: 150,
            onEnd: function () {
                document.querySelectorAll('.formset-item').forEach((item, index) => {
                    const orderInput = item.querySelector('[name$="order"]');
                    if (orderInput) orderInput.value = index;
                });
            }
        });
    }

});