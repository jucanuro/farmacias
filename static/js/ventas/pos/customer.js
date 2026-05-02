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
    const term = query.trim();

    if (term.length < 3) {
        domElements.customerSuggestions.classList.add('hidden');
        domElements.customerSuggestions.innerHTML = '';
        return;
    }

    try {
        const data = await API.buscarClienteAPI(term);
        const clientes = data.results || data;

        domElements.customerSuggestions.innerHTML = '';

        if (clientes.length > 0) {
            domElements.customerSuggestions.classList.remove('hidden');

            clientes.forEach(cliente => {
                const nombreCompleto = `${cliente.nombres || ''} ${cliente.apellidos || ''}`.trim() || 'Cliente sin nombre';
                const documento = `${cliente.tipo_documento || 'DOC'}: ${cliente.numero_documento || '-'}`;
                const telefono = cliente.telefono ? cliente.telefono : 'Sin teléfono';

                const item = document.createElement('div');

                item.className = `
                    group cursor-pointer border-b border-slate-100 bg-white px-4 py-3
                    transition-all duration-200 last:border-b-0 hover:bg-slate-900
                `;

                item.innerHTML = `
                    <div class="flex items-center gap-3">
                        <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl bg-emerald-50 text-sm font-black text-emerald-700 transition group-hover:bg-emerald-500 group-hover:text-white">
                            ${nombreCompleto.charAt(0).toUpperCase()}
                        </div>

                        <div class="min-w-0 flex-1">
                            <p class="truncate text-sm font-black text-slate-900 transition group-hover:text-white">
                                ${nombreCompleto}
                            </p>

                            <div class="mt-1 flex flex-wrap items-center gap-2">
                                <span class="rounded-full bg-slate-100 px-2.5 py-1 text-[10px] font-black text-slate-500 transition group-hover:bg-white/10 group-hover:text-slate-200">
                                    ${documento}
                                </span>

                                <span class="rounded-full bg-emerald-50 px-2.5 py-1 text-[10px] font-black text-emerald-700 transition group-hover:bg-emerald-400/20 group-hover:text-emerald-200">
                                    ${telefono}
                                </span>
                            </div>
                        </div>
                    </div>
                `;

                item.addEventListener('click', () => seleccionarCliente(cliente, state, domElements));
                domElements.customerSuggestions.appendChild(item);
            });

        } else {
            domElements.customerSuggestions.classList.add('hidden');

            const userChoice = await UI.showConfirm(
                domElements.alertModal,
                `El cliente con documento "${term}" no existe.`,
                '¿Deseas registrarlo ahora?'
            );

            if (userChoice) abrirModalNuevoCliente(domElements.newCustomerModal, term);
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