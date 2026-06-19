import * as API from './api.js';
import * as UI from './ui.js';

function togglePosLock(posContainer, bloquear) {
    if (!posContainer) return;

    posContainer.style.pointerEvents = bloquear ? 'none' : 'auto';
    posContainer.style.opacity = bloquear ? '0.2' : '1';
}

function getErrorMessage(error, fallback) {
    if (error instanceof Error && error.message) return error.message;
    if (error?.error) return error.error;
    if (error?.detail) return error.detail;
    return fallback;
}

function toMoney(value) {
    const number = Number(value || 0);
    return Number.isFinite(number) ? number.toFixed(2) : '0.00';
}

export async function verificarEstadoCaja(domElements) {
    try {
        const data = await API.verificarEstadoCajaAPI();

        domElements.aperturaCajaModal.classList.add('hidden');
        togglePosLock(domElements.posContainer, false);

        return data;
    } catch (error) {
        domElements.aperturaCajaModal.classList.remove('hidden');
        togglePosLock(domElements.posContainer, true);

        return null;
    }
}

export async function handleAbrirCaja(e, domElements, csrftoken) {
    e.preventDefault();

    const monto = domElements.montoInicialInput.value;

    if (monto === '' || Number(monto) < 0) {
        UI.showAlert(
            domElements.alertModal,
            'Por favor, ingresa un monto inicial válido.',
            'Error'
        );
        return;
    }

    domElements.confirmAperturaBtn.disabled = true;
    domElements.confirmAperturaBtn.textContent = 'Abriendo...';

    try {
        const data = await API.abrirCajaAPI(monto, csrftoken);

        UI.showAlert(
            domElements.alertModal,
            `Caja abierta con un monto inicial de S/ ${toMoney(data.monto_inicial)}`,
            '¡Éxito!'
        );

        domElements.aperturaCajaModal.classList.add('hidden');
        togglePosLock(domElements.posContainer, false);

    } catch (error) {
        UI.showAlert(
            domElements.alertModal,
            getErrorMessage(error, 'No se pudo abrir la caja.'),
            'Error de Apertura'
        );

    } finally {
        domElements.confirmAperturaBtn.disabled = false;
        domElements.confirmAperturaBtn.textContent = 'Confirmar apertura';
    }
}

export async function handleCerrarCaja(e, domElements, csrftoken) {
    e.preventDefault();

    const montoFinalInput = domElements.cierreCajaModal.querySelector('#monto-final-real');
    const observacionesInput = domElements.cierreCajaModal.querySelector('#observaciones-cierre');

    const montoFinal = montoFinalInput?.value || '';
    const observaciones = observacionesInput?.value || '';

    if (montoFinal === '' || Number(montoFinal) < 0) {
        UI.showAlert(
            domElements.alertModal,
            'Por favor, ingresa un monto final válido.',
            'Error'
        );
        return;
    }

    domElements.confirmCierreBtn.disabled = true;
    domElements.confirmCierreBtn.textContent = 'Calculando...';

    try {
        const data = await API.cerrarCajaAPI({
            monto_final_real: montoFinal,
            observaciones,
        }, csrftoken);

        domElements.cierreCajaModal.classList.add('hidden');
        mostrarResumenCierre(domElements.alertModal, data);

        domElements.alertModal.addEventListener('click', (ev) => {
            if (ev.target.id === 'alert-ok-btn') {
                verificarEstadoCaja(domElements);
            }
        }, { once: true });

    } catch (error) {
        UI.showAlert(
            domElements.alertModal,
            getErrorMessage(error, 'No se pudo cerrar la caja.'),
            'Error de Cierre'
        );

    } finally {
        domElements.confirmCierreBtn.disabled = false;
        domElements.confirmCierreBtn.textContent = 'Confirmar y cerrar caja';
    }
}

function mostrarResumenCierre(alertModal, data) {
    const montoInicial = Number(data.monto_inicial || 0);
    const montoSistema = Number(data.monto_final_sistema || 0);
    const montoReal = Number(data.monto_final_real || 0);
    const diferencia = Number(data.diferencia || 0);
    const totalVentasEfectivo = montoSistema - montoInicial;

    let diferenciaHtml = '';

    if (diferencia === 0) {
        diferenciaHtml = `
            <span class="inline-flex rounded-xl bg-emerald-50 px-3 py-1 text-sm font-black text-emerald-700">
                S/ 0.00 Cuadre perfecto
            </span>
        `;
    } else if (diferencia > 0) {
        diferenciaHtml = `
            <span class="inline-flex rounded-xl bg-emerald-50 px-3 py-1 text-sm font-black text-emerald-700">
                S/ ${toMoney(diferencia)} Sobrante
            </span>
        `;
    } else {
        diferenciaHtml = `
            <span class="inline-flex rounded-xl bg-rose-50 px-3 py-1 text-sm font-black text-rose-700">
                S/ ${toMoney(diferencia)} Faltante
            </span>
        `;
    }

    const resumen = `
        <div class="space-y-3 text-left">
            <div class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3">
                <div class="flex justify-between gap-4 text-sm">
                    <span class="font-bold text-slate-500">Monto inicial</span>
                    <span class="font-black text-slate-900">S/ ${toMoney(montoInicial)}</span>
                </div>
            </div>

            <div class="rounded-2xl border border-slate-200 bg-white px-4 py-3">
                <div class="flex justify-between gap-4 text-sm">
                    <span class="font-bold text-slate-500">Ventas en efectivo</span>
                    <span class="font-black text-slate-900">S/ ${toMoney(totalVentasEfectivo)}</span>
                </div>
            </div>

            <div class="rounded-2xl border border-slate-200 bg-white px-4 py-3">
                <div class="flex justify-between gap-4 text-sm">
                    <span class="font-bold text-slate-500">Total sistema</span>
                    <span class="font-black text-slate-900">S/ ${toMoney(montoSistema)}</span>
                </div>
            </div>

            <div class="rounded-2xl border border-slate-200 bg-white px-4 py-3">
                <div class="flex justify-between gap-4 text-sm">
                    <span class="font-bold text-slate-500">Total contado</span>
                    <span class="font-black text-slate-900">S/ ${toMoney(montoReal)}</span>
                </div>
            </div>

            <div class="rounded-2xl border border-slate-200 bg-slate-900 px-4 py-4">
                <div class="flex items-center justify-between gap-4">
                    <span class="text-sm font-black text-white">Diferencia</span>
                    ${diferenciaHtml}
                </div>
            </div>
        </div>
    `;

    UI.showAlert(alertModal, resumen, 'Resumen de Cierre de Caja');
}