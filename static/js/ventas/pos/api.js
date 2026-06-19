// static/js/ventas/pos/api.js

async function parseResponse(response, fallbackMessage = 'Error de servidor') {
    const contentType = response.headers.get('content-type') || '';

    let data = null;

    if (contentType.includes('application/json')) {
        data = await response.json();
    } else {
        data = { error: await response.text() };
    }

    if (!response.ok) {
        throw data || { error: fallbackMessage };
    }

    return data;
}

export async function buscarProductosAPI(query) {
    const search = encodeURIComponent(query || '');

    const response = await fetch(`/inventario/api/productos/?search=${search}`, {
        method: 'GET',
        headers: {
            Accept: 'application/json',
        },
    });

    return await parseResponse(response, 'Error al buscar productos');
}

export async function buscarClienteAPI(query) {
    const search = encodeURIComponent(query || '');

    const response = await fetch(`/clientes/api/clientes/?search=${search}`, {
        method: 'GET',
        headers: {
            Accept: 'application/json',
        },
    });

    return await parseResponse(response, 'Error buscando cliente');
}

export async function guardarNuevoClienteAPI(data, csrftoken) {
    const response = await fetch('/clientes/api/clientes/', {
        method: 'POST',
        headers: {
            Accept: 'application/json',
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify(data),
    });

    return await parseResponse(response, 'Error al guardar cliente');
}

export async function finalizarVentaAPI(ventaData, csrftoken) {
    const response = await fetch('/ventas/api/ventas/registrar/', {
        method: 'POST',
        headers: {
            Accept: 'application/json',
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify(ventaData),
    });

    return await parseResponse(response, 'Error al registrar venta');
}

export async function verificarEstadoCajaAPI() {
    const response = await fetch('/ventas/api/caja/estado/', {
        method: 'GET',
        headers: {
            Accept: 'application/json',
        },
    });

    if (response.status === 404) {
        throw new Error('CERRADA');
    }

    return await parseResponse(response, 'Error verificando estado de caja');
}

export async function abrirCajaAPI(monto, csrftoken) {
    const response = await fetch('/ventas/api/caja/abrir/', {
        method: 'POST',
        headers: {
            Accept: 'application/json',
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({
            monto_inicial: monto,
        }),
    });

    return await parseResponse(response, 'Error al abrir caja');
}

export async function cerrarCajaAPI(data, csrftoken) {
    const response = await fetch('/ventas/api/caja/cerrar/', {
        method: 'POST',
        headers: {
            Accept: 'application/json',
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify(data),
    });

    return await parseResponse(response, 'Error al cerrar caja');
}

export async function crearComprobanteElectronicoAPI(data, csrftoken) {
    const response = await fetch('/facturacion/api/comprobantes/crear-desde-venta/', {
        method: 'POST',
        headers: {
            Accept: 'application/json',
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify(data),
    });

    return await parseResponse(response, 'Error al crear comprobante electrónico');
}

export async function generarXMLAPI(comprobanteId, csrftoken) {
    const response = await fetch(`/facturacion/api/comprobantes/${comprobanteId}/generar-xml/`, {
        method: 'POST',
        headers: {
            Accept: 'application/json',
            'X-CSRFToken': csrftoken,
        },
    });

    return await parseResponse(response, 'Error al generar XML');
}