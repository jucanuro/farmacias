import * as API from './api.js';
import * as UI from './ui.js';

function togglePosLock(posContainer, bloquear) {
    if (!posContainer) return;
    posContainer.style.pointerEvents = bloquear ? 'none' : 'auto';
    posContainer.style.opacity = bloquear ? '0.2' : '1';
}

export async function verificarEstadoCaja(domElements) {
    try {
        await API.verificarEstadoCajaAPI();
        domElements.aperturaCajaModal.classList.add('hidden');
        togglePosLock(domElements.posContainer, false);
    } catch (error) {
        domElements.aperturaCajaModal.classList.remove('hidden');
        togglePosLock(domElements.posContainer, true);
    }
}

export async function handleAbrirCaja(e, domElements, csrftoken) {
    e.preventDefault();
    const monto = domElements.montoInicialInput.value;
    if (monto === '' || parseFloat(monto) < 0) {
        UI.showAlert(domElements.alertModal, 'Por favor, ingresa un monto inicial válido.', 'Error');
        return;
    }
    domElements.confirmAperturaBtn.disabled = true;
    domElements.confirmAperturaBtn.textContent = 'Abriendo...';
    try {
        const data = await API.abrirCajaAPI(monto, csrftoken);
        UI.showAlert(domElements.alertModal, `Caja abierta con un monto inicial de S/ ${parseFloat(data.monto_inicial).toFixed(2)}`, '¡Éxito!');
        domElements.aperturaCajaModal.classList.add('hidden');
        togglePosLock(domElements.posContainer, false);
    } catch (error) {
        UI.showAlert(domElements.alertModal, error.error || 'No se pudo abrir la caja.', 'Error de Apertura');
    } finally {
        domElements.confirmAperturaBtn.disabled = false;
        domElements.confirmAperturaBtn.textContent = 'Confirmar Apertura';
    }
}

export async function handleCerrarCaja(e, domElements, csrftoken) {
    e.preventDefault();
    const montoFinal = domElements.cierreCajaModal.querySelector('#monto-final-real').value;
    const observaciones = domElements.cierreCajaModal.querySelector('#observaciones-cierre').value;
    if (montoFinal === '' || parseFloat(montoFinal) < 0) {
        UI.showAlert(domElements.alertModal, 'Por favor, ingresa un monto final válido.', 'Error');
        return;
    }
    domElements.confirmCierreBtn.disabled = true;
    domElements.confirmCierreBtn.textContent = 'Calculando...';
    try {
        const data = await API.cerrarCajaAPI({ monto_final_real: montoFinal, observaciones: observaciones }, csrftoken);
        domElements.cierreCajaModal.classList.add('hidden');
        mostrarResumenCierre(domElements.alertModal, data);
        
        // Listener para volver a bloquear el POS después de ver el resumen
        domElements.alertModal.addEventListener('click', (ev) => {
            if (ev.target.id === 'alert-ok-btn') {
                verificarEstadoCaja(domElements);
            }
        }, { once: true });

    } catch (error) {
        UI.showAlert(domElements.alertModal, error.error || 'No se pudo cerrar la caja.', 'Error de Cierre');
    } finally {
        domElements.confirmCierreBtn.disabled = false;
        domElements.confirmCierreBtn.textContent = 'Confirmar y Cerrar Caja';
    }
}

function mostrarResumenCierre(alertModal, data) {
    const montoInicial = parseFloat(data.monto_inicial).toFixed(2);
    const montoSistema = parseFloat(data.monto_final_sistema).toFixed(2);
    const montoReal = parseFloat(data.monto_final_real).toFixed(2);
    const diferencia = parseFloat(data.diferencia);
    let diferenciaHtml;
    if (diferencia === 0) {
        diferenciaHtml = `<strong style="color: #10b981;">S/ 0.00 (Cuadre perfecto)</strong>`;
    } else if (diferencia > 0) {
        diferenciaHtml = `<strong style="color: #10b981;">S/ ${diferencia.toFixed(2)} (Sobrante)</strong>`;
    } else {
        diferenciaHtml = `<strong style="color: #f43f5e;">S/ ${diferencia.toFixed(2)} (Faltante)</strong>`;
    }
    const resumen = `
        <div style="text-align: left; font-size: 0.95rem; line-height: 1.6;">
            <strong>Monto Inicial:</strong><span style="float: right;">S/ ${montoInicial}</span><br>
            <strong>Total Ventas (Efectivo):</strong><span style="float: right;">S/ ${(montoSistema - montoInicial).toFixed(2)}</span><br>
            <hr style="border-color: #4b5563; margin: 4px 0;">
            <strong>Total en Sistema:</strong><span style="float: right;">S/ ${montoSistema}</span><br>
            <strong>Total Contado (Real):</strong><span style="float: right;">S/ ${montoReal}</span><br>
            <hr style="border-color: #4b5563; margin: 4px 0;">
            <strong>Diferencia:</strong><span style="float: right;">${diferenciaHtml}</span>
        </div>`;
    UI.showAlert(alertModal, resumen, 'Resumen de Cierre de Caja');
}