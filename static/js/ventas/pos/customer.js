import * as API from './api.js';
import * as UI from './ui.js';

function getClienteNombre(cliente) {
    return `${cliente?.nombres || ''} ${cliente?.apellidos || ''}`.trim() || 'Cliente sin nombre';
}

function getErrorMessage(error, fallback = 'Ocurrió un error.') {
    if (error instanceof Error && error.message) return error.message;
    if (error?.error) return error.error;
    if (error?.detail) return error.detail;

    if (error && typeof error === 'object') {
        return Object.entries(error)
            .map(([field, value]) => {
                const parsedValue = Array.isArray(value) ? value.join(', ') : value;
                return `• ${field}: ${parsedValue}`;
            })
            .join('\n');
    }

    return fallback;
}

function setButtonLoading(button, loading, textLoading, textNormal) {
    if (!button) return;

    button.disabled = loading;
    button.textContent = loading ? textLoading : textNormal;
}

function closeSuggestions(domElements) {
    domElements.customerSuggestions.classList.add('hidden');
    domElements.customerSuggestions.innerHTML = '';
}

function seleccionarComprobantePorCliente(cliente, domElements) {
    const tipoDocumento = cliente?.tipo_documento || '';
    const tipo = tipoDocumento === 'RUC' ? 'FACTURA' : 'BOLETA';
    const button = domElements.comprobanteSelector?.querySelector(`[data-tipo='${tipo}']`);

    if (button) button.click();
}

export function seleccionarCliente(cliente, state, domElements) {
    state.selectedCustomer = cliente;

    domElements.customerNameSpan.textContent = getClienteNombre(cliente);
    domElements.customerDisplay.classList.remove('hidden');
    domElements.customerSearchInput.value = '';

    closeSuggestions(domElements);
    seleccionarComprobantePorCliente(cliente, domElements);
}

export function limpiarCliente(state, domElements) {
    state.selectedCustomer = null;

    domElements.customerSearchInput.value = '';
    domElements.customerDisplay.classList.add('hidden');

    closeSuggestions(domElements);

    const ticketButton = domElements.comprobanteSelector?.querySelector(`[data-tipo='TICKET']`);
    if (ticketButton) ticketButton.click();
}

export async function buscarCliente(query, domElements, state) {
    const term = String(query || '').trim();

    if (term.length < 3) {
        closeSuggestions(domElements);
        return;
    }

    try {
        const data = await API.buscarClienteAPI(term);
        const clientes = Array.isArray(data.results) ? data.results : Array.isArray(data) ? data : [];

        domElements.customerSuggestions.innerHTML = '';

        if (!clientes.length) {
            closeSuggestions(domElements);

            const userChoice = await UI.showConfirm(
                domElements.alertModal,
                `El cliente con documento o nombre "${term}" no existe.`,
                '¿Deseas registrarlo ahora?'
            );

            if (userChoice) {
                abrirModalNuevoCliente(domElements.newCustomerModal, term);
            }

            return;
        }

        domElements.customerSuggestions.classList.remove('hidden');

        clientes.forEach(cliente => {
            const nombreCompleto = getClienteNombre(cliente);
            const inicial = nombreCompleto.charAt(0).toUpperCase() || 'C';
            const documento = `${cliente.tipo_documento || 'DOC'}: ${cliente.numero_documento || '-'}`;
            const telefono = cliente.telefono || 'Sin teléfono';

            const item = document.createElement('button');
            item.type = 'button';
            item.className = 'group block w-full border-b border-slate-100 bg-white px-4 py-3 text-left transition-all duration-200 last:border-b-0 hover:bg-slate-900';

            item.innerHTML = `
                <div class="flex items-center gap-3">
                    <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl bg-emerald-50 text-sm font-black text-emerald-700 transition group-hover:bg-emerald-500 group-hover:text-white">
                        ${inicial}
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

    } catch (error) {
        closeSuggestions(domElements);
        UI.showAlert(
            domElements.alertModal,
            getErrorMessage(error, 'No se pudo buscar el cliente.'),
            'Error buscando cliente'
        );
    }
}

export function abrirModalNuevoCliente(newCustomerModal, numeroDocumento) {
    const form = newCustomerModal.querySelector('form');
    const numeroInput = newCustomerModal.querySelector('#modal-numero-documento');
    const nombresInput = newCustomerModal.querySelector('#modal-nombres');

    if (form) form.reset();

    if (numeroInput) {
        numeroInput.value = numeroDocumento || '';
        numeroInput.dispatchEvent(new Event('input'));
    }

    newCustomerModal.classList.remove('hidden');

    if (nombresInput) {
        setTimeout(() => nombresInput.focus(), 80);
    }
}

export async function guardarNuevoCliente(e, domElements, state, csrftoken) {
    e.preventDefault();

    const form = domElements.newCustomerForm;
    const saveButton = form.querySelector('button[type="submit"]');

    const data = {
        tipo_documento: form.querySelector('#modal-tipo-documento')?.value || '',
        numero_documento: form.querySelector('#modal-numero-documento')?.value?.trim() || '',
        nombres: form.querySelector('#modal-nombres')?.value?.trim() || '',
        apellidos: form.querySelector('#modal-apellidos')?.value?.trim() || '',
        direccion: form.querySelector('#modal-direccion')?.value?.trim() || '',
        telefono: form.querySelector('#modal-telefono')?.value?.trim() || '',
    };

    if (!data.tipo_documento) {
        UI.showAlert(domElements.alertModal, 'Selecciona el tipo de documento.', 'Datos incompletos');
        return;
    }

    if (!data.numero_documento) {
        UI.showAlert(domElements.alertModal, 'Ingresa el número de documento.', 'Datos incompletos');
        return;
    }

    if (!data.nombres) {
        UI.showAlert(domElements.alertModal, 'Ingresa el nombre o razón social del cliente.', 'Datos incompletos');
        return;
    }

    setButtonLoading(saveButton, true, 'Guardando...', 'Guardar cliente');

    try {
        const nuevoCliente = await API.guardarNuevoClienteAPI(data, csrftoken);

        domElements.newCustomerModal.classList.add('hidden');

        UI.showAlert(
            domElements.alertModal,
            'Cliente creado con éxito.',
            '¡Éxito!'
        );

        seleccionarCliente(nuevoCliente, state, domElements);

    } catch (error) {
        UI.showAlert(
            domElements.alertModal,
            getErrorMessage(error, 'No se pudo crear el cliente.'),
            'Error al crear el cliente'
        );

    } finally {
        setButtonLoading(saveButton, false, 'Guardando...', 'Guardar cliente');
    }
}