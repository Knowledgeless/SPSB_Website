document.getElementById('add-form').addEventListener('click', function () {
    const container = document.getElementById('formset-container');
    const totalForms = document.getElementById('id_post_media-TOTAL_FORMS');

    let formCount = parseInt(totalForms.value);

    let newForm = container.children[0].cloneNode(true);

    newForm.innerHTML = newForm.innerHTML.replace(/-\d+-/g, `-${formCount}-`);

    // clear values
    newForm.querySelectorAll('input, textarea, select').forEach(el => {
        if (el.type !== 'hidden') el.value = '';
        if (el.type === 'checkbox') el.checked = false;
    });

    container.appendChild(newForm);
    totalForms.value = formCount + 1;
});