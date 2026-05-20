document.addEventListener("DOMContentLoaded", function () {

    const container = document.getElementById('formset-container');
    const addButton = document.getElementById('add-form');

    // =========================
    // STATUS SYSTEM (PRO CMS)
    // =========================
    function initStatusSystem() {
        const buttons = document.querySelectorAll('.status-btn');

        buttons.forEach(btn => {
            const input = btn.querySelector('input[type="radio"]');

            // Initial state (for edit page)
            if (input && input.checked) {
                btn.classList.add('active');
            }

            btn.addEventListener('click', function (e) {
                e.preventDefault();
                e.stopPropagation();

                // 🔥 AJAX-style immediate feedback
                // Remove active from all buttons
                buttons.forEach(b => {
                    b.classList.remove('active');
                    const bInput = b.querySelector('input[type="radio"]');
                    if (bInput) bInput.checked = false;
                });

                // Add active to clicked button with visual feedback
                this.classList.add('active');
                if (input) {
                    input.checked = true;
                    input.dispatchEvent(new Event('change', { bubbles: true }));
                }

                // Visual feedback - pulse animation
                this.style.transform = 'scale(0.95)';
                setTimeout(() => {
                    this.style.transform = '';
                }, 150);
            });
        });
    }

    initStatusSystem();



    // =========================
    // CATEGORY SYSTEM (AJAX-STYLE)
    // =========================
    function initCategorySystem() {
        document.querySelectorAll('.category-pill').forEach(pill => {
            const input = pill.querySelector('input[type="radio"]');

            // Initial state (for edit page)
            if (input && input.checked) {
                pill.classList.add('active');
            }

            pill.addEventListener('click', function (e) {
                e.preventDefault();
                e.stopPropagation();

                // 🔥 AJAX-style immediate feedback
                // Remove active from all pills
                document.querySelectorAll('.category-pill').forEach(p => {
                    p.classList.remove('active');
                    const pInput = p.querySelector('input[type="radio"]');
                    if (pInput) pInput.checked = false;
                });

                // Add active to clicked pill
                this.classList.add('active');
                if (input) {
                    input.checked = true;
                    // Trigger change event for form validation
                    input.dispatchEvent(new Event('change', { bubbles: true }));
                }

                // Clear new category input
                const newCatInput = document.querySelector('[name="new_category"]');
                if (newCatInput) {
                    newCatInput.value = '';
                    newCatInput.dispatchEvent(new Event('input', { bubbles: true }));
                }

                // Visual feedback - ensure styles are applied
                this.style.transform = 'scale(0.98)';
                setTimeout(() => {
                    this.style.transform = '';
                }, 150);
            });
        });
    }

    initCategorySystem();


    const newCatInput = document.querySelector('[name="new_category"]');
    if (newCatInput) {
        newCatInput.addEventListener('input', function () {
            if (this.value.trim()) {
                // AJAX-style: immediately clear all active pills
                document.querySelectorAll('.category-pill').forEach(p => {
                    p.classList.remove('active');
                    const pInput = p.querySelector('input[type="radio"]');
                    if (pInput) pInput.checked = false;
                });
            }
        });
    }

    // =========================
    // BANNER CHECKBOX SYSTEM (SINGLE SELECTION)
    // =========================
    function initBannerSystem() {
        // Use event delegation to handle dynamically added forms
        container?.addEventListener('change', function (e) {
            if (e.target.classList.contains('banner-checkbox')) {
                handleBannerCheckboxChange(e.target);
            }
        });

        // Also handle initial state
        document.querySelectorAll('.banner-checkbox').forEach(checkbox => {
            if (checkbox.checked) {
                highlightBannerSection(checkbox);
            }
        });
    }

    function handleBannerCheckboxChange(checkbox) {
        // If this checkbox is now checked, uncheck all others
        if (checkbox.checked) {
            document.querySelectorAll('.banner-checkbox').forEach(cb => {
                if (cb !== checkbox) {
                    cb.checked = false;
                    removeBannerHighlight(cb);
                }
            });
            // Highlight this section
            highlightBannerSection(checkbox);
        } else {
            removeBannerHighlight(checkbox);
        }
    }

    function highlightBannerSection(checkbox) {
        const sectionBlock = checkbox.closest('.section-block');
        if (sectionBlock) {
            sectionBlock.classList.add('banner-section-active');
            // Add visual indicator
            const indicator = sectionBlock.querySelector('.banner-indicator');
            if (!indicator) {
                const badge = document.createElement('div');
                badge.className = 'banner-indicator';
                badge.innerHTML = '<i class="fas fa-crown"></i> Banner Image';
                sectionBlock.prepend(badge);
            }
        }
    }

    function removeBannerHighlight(checkbox) {
        const sectionBlock = checkbox.closest('.section-block');
        if (sectionBlock) {
            sectionBlock.classList.remove('banner-section-active');
            const indicator = sectionBlock.querySelector('.banner-indicator');
            if (indicator) {
                indicator.remove();
            }
        }
    }

    initBannerSystem();


    if (addButton && container) {
        addButton.addEventListener('click', function (e) {
            e.preventDefault();

            const totalForms = document.getElementById('id_post_media-TOTAL_FORMS');
            const maxForms = document.getElementById('id_post_media-MAX_NUM_FORMS');
            
            let formCount = parseInt(totalForms.value, 10);
            let maxFormCount = maxForms ? parseInt(maxForms.value, 10) : 1000;

            if (formCount >= maxFormCount) {
                alert('Maximum number of forms reached!');
                return;
            }

            // Clone the first form if it exists, otherwise create a new one
            let template = container.querySelector('.formset-item');
            if (!template) {
                console.error('No formset item template found');
                return;
            }

            let newForm = template.cloneNode(true);

            // Replace all form indices with the new count
            const oldIndex = formCount - 1;
            newForm.innerHTML = newForm.innerHTML.replace(
                new RegExp(`(id|name)="([^"]*)-${oldIndex}-([^"]*)"`, 'g'),
                `$1="$2-${formCount}-$3"`
            );

            // Also replace data attributes if any
            newForm.innerHTML = newForm.innerHTML.replace(
                new RegExp(`data-formset-form-num="${oldIndex}"`, 'g'),
                `data-formset-form-num="${formCount}"`
            );

            // Reset all inputs
            newForm.querySelectorAll('input, textarea, select').forEach(el => {
                if (el.type === 'checkbox' || el.type === 'radio') {
                    el.checked = false;
                } else if (el.name && (el.name.endsWith('-DELETE') || el.name.endsWith('-id'))) {
                    // Don't change DELETE and id fields for new forms
                    if (el.name.endsWith('-DELETE')) {
                        el.checked = false;
                    } else {
                        el.value = '';
                    }
                } else {
                    el.value = '';
                }
            });

            // Clear preview images
            newForm.querySelectorAll('img.preview-img').forEach(img => img.remove());

            // Clear banner indicators
            newForm.querySelectorAll('.banner-indicator').forEach(el => el.remove());
            newForm.classList.remove('banner-section-active');

            // Update order field
            const orderInput = newForm.querySelector('[name$="-order"]');
            if (orderInput) orderInput.value = formCount;

            // Add to container
            container.appendChild(newForm);

            // Update total forms count
            totalForms.value = formCount + 1;

            // Trigger change event to update any listeners
            newForm.dispatchEvent(new Event('change', { bubbles: true }));
        });
    }


    // =========================
    // SORTABLE (ORDER SYSTEM)
    // =========================
    if (window.Sortable && container) {
        new Sortable(container, {
            animation: 150,
            onEnd: function () {

                document.querySelectorAll('.formset-item').forEach((item, index) => {
                    const orderInput = item.querySelector('[name$="-order"]');
                    if (orderInput) orderInput.value = index;
                });

            }
        });
    }

});