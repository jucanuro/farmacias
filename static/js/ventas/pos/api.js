// static/js/ventas/pos/api.js

export async function buscarProductosAPI(query) {
    const response = await fetch(`/inventario/api/productos/?search=${query}`);
    if (!response.ok) throw new Error('Error al buscar productos');
    return await response.json();
}

export async function buscarClienteAPI(query) {
    const response = await fetch(`/clientes/api/clientes/?search=${query}`);
    if (!response.ok) throw new Error('Error buscando cliente');
    return await response.json();
}

export async function guardarNuevoClienteAPI(data, csrftoken) {
    const response = await fetch('/clientes/api/clientes/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrftoken },
        body: JSON.stringify(data),
    });
    if (!response.ok) throw await response.json();
    return await response.json();
}

export async function finalizarVentaAPI(ventaData, csrftoken) {
    const response = await fetch('/ventas/api/ventas/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrftoken },
        body: JSON.stringify(ventaData)
    });
    if (!response.ok) throw await response.json();
    return await response.json();
}

export async function verificarEstadoCajaAPI() {
    const response = await fetch('/ventas/api/caja/estado/');
    if (response.status === 404) throw new Error('CERRADA');
    if (!response.ok) throw new Error('Error de red o servidor');
    return await response.json();
}

export async function abrirCajaAPI(monto, csrftoken) {
    const response = await fetch('/ventas/api/caja/abrir/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrftoken },
        body: JSON.stringify({ monto_inicial: monto }),
    });
    if (!response.ok) throw await response.json();
    return await response.json();
}

export async function cerrarCajaAPI(data, csrftoken) {
    const response = await fetch('/ventas/api/caja/cerrar/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrftoken },
        body: JSON.stringify(data),
    });
    if (!response.ok) throw await response.json();
    return await response.json();
}