import * as API from './api.js';
import * as UI from './ui.js';

export function seleccionarCliente(cliente, state, domElements) {
    state.selectedCustomer = cliente;
    domElements.customerNameSpan.textContent = `${cliente.nombres} ${cliente.apellidos || ''}`.trim();
    domElements.customerDisplay.classList.remove('hidden');
    domElements.customerSuggestions.classList.add('hidden');
    domElements.customerSearchInput.value = '';
    if (cliente.tipo_documento === 'RUC') {
        domElements.comprobanteSelector.querySelector(`[data-tipo='FACTURA']`).click();
    } else {
        domElements.comprobanteSelector.querySelector(`[data-tipo='BOLETA']`).click();
    }
}

export function limpiarCliente(state, domElements) {
    state.selectedCustomer = null;
    domElements.customerSearchInput.value = '';
    domElements.customerDisplay.classList.add('hidden');
    domElements.customerSuggestions.classList.add('hidden');
    domElements.comprobanteSelector.querySelector(`[data-tipo='TICKET']`).click();
}

export async function buscarCliente(query, domElements, state) {
    if (query.length < 3) {
        domElements.customerSuggestions.classList.add('hidden');
        return;
    }
    try {
        const data = await API.buscarClienteAPI(query);
        const clientes = data.results || data;
        domElements.customerSuggestions.innerHTML = '';
        if (clientes.length > 0) {
            domElements.customerSuggestions.classList.remove('hidden');
            clientes.forEach(cliente => {
                const item = document.createElement('div');
                item.className = 'p-3 hover:bg-slate-700 cursor-pointer border-b border-slate-800';
                item.innerHTML = `<p class="font-semibold text-white">${cliente.nombres} ${cliente.apellidos}</p><p class="text-xs text-slate-400">${cliente.tipo_documento}: ${cliente.numero_documento}</p>`;
                item.addEventListener('click', () => seleccionarCliente(cliente, state, domElements));
                domElements.customerSuggestions.appendChild(item);
            });
        } else {
            domElements.customerSuggestions.classList.add('hidden');
            const userChoice = await UI.showConfirm(domElements.alertModal, `El cliente con documento "${query}" no existe.`, '¿Deseas registrarlo ahora?');
            if (userChoice) abrirModalNuevoCliente(domElements.newCustomerModal, query);
        }
    } catch (error) {
        console.error('Error buscando cliente:', error);
    }
}

export function abrirModalNuevoCliente(newCustomerModal, numeroDocumento) {
    newCustomerModal.querySelector('form').reset();
    const numeroInput = newCustomerModal.querySelector('#modal-numero-documento');
    numeroInput.value = numeroDocumento;
    numeroInput.dispatchEvent(new Event('input'));
    newCustomerModal.classList.remove('hidden');
    newCustomerModal.querySelector('#modal-nombres').focus();
}

export async function guardarNuevoCliente(e, domElements, state, csrftoken) {
    e.preventDefault();
    const form = domElements.newCustomerForm;
    const saveButton = form.querySelector('button[type="submit"]');
    saveButton.disabled = true;
    saveButton.textContent = 'Guardando...';

    const data = {
        tipo_documento: form.querySelector('#modal-tipo-documento').value,
        numero_documento: form.querySelector('#modal-numero-documento').value,
        nombres: form.querySelector('#modal-nombres').value,
        apellidos: form.querySelector('#modal-apellidos').value,
        direccion: form.querySelector('#modal-direccion').value,
        telefono: form.querySelector('#modal-telefono').value,
    };

    try {
        const nuevoCliente = await API.guardarNuevoClienteAPI(data, csrftoken);
        domElements.newCustomerModal.classList.add('hidden');
        UI.showAlert(domElements.alertModal, 'Cliente creado con éxito.', '¡Éxito!');
        seleccionarCliente(nuevoCliente, state, domElements);
    } catch (error) {
        let errorMessage = "Por favor, corrige los siguientes errores:\n\n";
        for (const field in error) errorMessage += `• ${field}: ${Array.isArray(error[field]) ? error[field].join(', ') : error[field]}\n`;
        UI.showAlert(domElements.alertModal, errorMessage, 'Error al crear el cliente');
    } finally {
        saveButton.disabled = false;
        saveButton.textContent = 'Guardar Cliente';
    }
}