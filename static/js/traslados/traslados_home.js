// static/js/traslados/traslados_home.js

document.addEventListener('DOMContentLoaded', () => {
    const tableBody = document.getElementById('transfers-list-body');
    const searchInput = document.getElementById('transfer-search-input');
    const countBadge = document.getElementById('transfers-count-badge');

    function getCookie(name) {
        let cookieValue = null;

        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');

            for (let cookie of cookies) {
                cookie = cookie.trim();

                if (cookie.startsWith(name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }

        return cookieValue;
    }

    const csrftoken = getCookie('csrftoken');

    const updateCount = () => {
        const rows = document.querySelectorAll('.transfer-row');
        if (countBadge) {
            countBadge.textContent = `${rows.length} traslados`;
        }
    };

    const postAction = async (url) => {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                Accept: 'application/json',
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken,
            },
            body: JSON.stringify({}),
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Ocurrió un error.');
        }

        return data;
    };

    const viewTransferDetail = async (transferId) => {
        try {
            const response = await fetch(`/traslados/api/transferencias/${transferId}/`, {
                method: 'GET',
                headers: {
                    Accept: 'application/json',
                },
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'No se pudo cargar el detalle.');
            }

            const detalles = data.detalles || [];

            let productosTexto = 'Sin productos registrados.';

            if (detalles.length > 0) {
                productosTexto = detalles.map((item) => {
                    return `• ${item.producto_nombre} | Lote: ${item.lote} | Cantidad: ${item.cantidad}`;
                }).join('\n');
            }

            alert(
                `Traslado #${data.id}\n\n` +
                `Origen: ${data.sucursal_origen_nombre}\n` +
                `Destino: ${data.sucursal_destino_nombre}\n` +
                `Estado: ${data.estado}\n\n` +
                `Productos:\n${productosTexto}`
            );

        } catch (error) {
            alert(`Error: ${error.message}`);
        }
    };

    const handleTransferAction = async (action, transferId) => {
        let url = '';
        let confirmationMessage = '';

        if (action === 'ver') {
            viewTransferDetail(transferId);
            return;
        }

        if (action === 'enviar') {
            url = `/traslados/api/transferencias/${transferId}/enviar/`;
            confirmationMessage = '¿Seguro que quieres enviar este traslado? El stock se descontará del origen.';
        }

        if (action === 'recibir') {
            url = `/traslados/api/transferencias/${transferId}/recibir/`;
            confirmationMessage = '¿Seguro que quieres recibir este traslado? El stock se añadirá al destino.';
        }

        if (action === 'eliminar') {
            url = `/traslados/api/transferencias/${transferId}/eliminar/`;
            confirmationMessage = '¿Seguro que quieres eliminar este traslado? Esta acción no se puede deshacer.';
        }

        if (!url) return;
        if (!confirm(confirmationMessage)) return;

        try {
            const result = await postAction(url);
            alert(result.message || result.status || 'Operación realizada correctamente.');
            window.location.reload();

        } catch (error) {
            alert(`Error: ${error.message}`);
        }
    };

    const applySearch = () => {
        const term = searchInput.value.toLowerCase().trim();
        const rows = document.querySelectorAll('.transfer-row');

        rows.forEach((row) => {
            const text = row.dataset.search.toLowerCase();
            row.style.display = text.includes(term) ? '' : 'none';
        });
    };

    tableBody.addEventListener('click', (event) => {
        const button = event.target.closest('.action-btn');
        if (!button) return;

        handleTransferAction(button.dataset.action, button.dataset.id);
    });

    if (searchInput) {
        searchInput.addEventListener('keyup', applySearch);
    }

    updateCount();
});