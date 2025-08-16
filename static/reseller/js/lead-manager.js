document.addEventListener('DOMContentLoaded', function() {
    const addLeadModal = document.getElementById('addLeadModal');
    const addLeadBtn = document.querySelector('[data-bs-target="#addLeadModal"]');
    const closeButtons = document.querySelectorAll('[data-bs-dismiss="modal"]');

    if (addLeadBtn) {
        addLeadBtn.addEventListener('click', function(e) {
            e.preventDefault();
            showModal(addLeadModal);
        });
    }

    closeButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            hideModal(addLeadModal);
        });
    });

    if (addLeadModal) {
        addLeadModal.addEventListener('click', function(e) {
            if (e.target === addLeadModal) {
                hideModal(addLeadModal);
            }
        });
    }

    function showModal(modal) {
        if (!modal) return;
        const backdrop = document.createElement('div');
        backdrop.className = 'modal-backdrop fade';
        document.body.appendChild(backdrop);

        modal.style.display = 'block';
        document.body.classList.add('modal-open');

        setTimeout(() => {
            modal.classList.add('show');
            backdrop.classList.add('show');
        }, 10);
    }

    function hideModal(modal) {
        if (!modal) return;
        const backdrop = document.querySelector('.modal-backdrop');

        modal.classList.remove('show');
        if (backdrop) backdrop.classList.remove('show');

        setTimeout(() => {
            modal.style.display = 'none';
            if (backdrop) backdrop.remove();
            document.body.classList.remove('modal-open');
        }, 150);
    }

    const leadForm = document.getElementById('leadForm');
    if (leadForm) {
        leadForm.addEventListener('submit', function(e) {
            e.preventDefault();
            saveLead();
        });
    }
});

function viewLead(leadId) {
    console.log('Viewing lead:', leadId);
}

function editLead(leadId) {
    console.log('Editing lead:', leadId);
    const modal = document.getElementById('addLeadModal');
    const modalTitle = document.getElementById('addLeadModalLabel');
    if (modalTitle) modalTitle.textContent = 'Edit Lead';

    const event = new Event('click');
    const btn = document.querySelector('[data-bs-target="#addLeadModal"]');
    if (btn) btn.dispatchEvent(event);
}

function deleteLead(leadId) {
    if (confirm('Are you sure you want to delete this lead?')) {
        console.log('Deleting lead:', leadId);
    }
}

function saveLead() {
    const form = document.getElementById('leadForm');
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }

    const formData = new FormData(form);
    const leadData = Object.fromEntries(formData);

    console.log('Saving lead:', leadData);

    const modal = document.getElementById('addLeadModal');
    const closeBtn = modal.querySelector('[data-bs-dismiss="modal"]');
    if (closeBtn) closeBtn.click();

    form.reset();

    alert('Lead saved successfully!');
}

const style = document.createElement('style');
style.textContent = `
    body.modal-open {
        overflow: hidden;
        padding-right: 15px;
    }
`;
document.head.appendChild(style);
