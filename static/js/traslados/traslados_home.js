// static/js/traslados/traslados_home.js

document.addEventListener('DOMContentLoaded', () => {
    const tableBody = document.getElementById('transfers-list-body');
    const searchInput = document.getElementById('transfer-search-input');
    const countBadge = document.getElementById('transfers-count-badge');

    const getCookie = (name) => {
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
    };

    const csrftoken = getCookie('csrftoken');

    const parseJsonResponse = async (response) => {
        const contentType = response.headers.get('content-type') || '';

        if (!contentType.includes('application/json')) {
            throw new Error('La respuesta del servidor no es JSON. Revisa la URL, sesión o permisos.');
        }

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || data.detail || 'Ocurrió un error en el servidor.');
        }

        return data;
    };

    const getVisibleRowsCount = () => {
        const rows = document.querySelectorAll('.transfer-row');
        return Array.from(rows).filter(row => row.style.display !== 'none').length;
    };

    const updateCount = () => {
        if (!countBadge) return;

        const totalRows = document.querySelectorAll('.transfer-row').length;
        const visibleRows = getVisibleRowsCount();

        if (searchInput && searchInput.value.trim()) {
            countBadge.textContent = `${visibleRows} de ${totalRows} traslados`;
        } else {
            countBadge.textContent = `${totalRows} traslados`;
        }
    };

    const setButtonLoading = (button, isLoading) => {
        if (!button) return;

        if (isLoading) {
            button.dataset.originalText = button.innerHTML;
            button.disabled = true;
            button.classList.add('opacity-60', 'cursor-not-allowed');
            button.innerHTML = '…';
        } else {
            button.disabled = false;
            button.classList.remove('opacity-60', 'cursor-not-allowed');

            if (button.dataset.originalText) {
                button.innerHTML = button.dataset.originalText;
                delete button.dataset.originalText;
            }
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

        return parseJsonResponse(response);
    };

    const renderStatus = (estado) => {
        const estadoMap = {
            PENDIENTE: 'Pendiente',
            ENVIADO: 'Enviado',
            RECIBIDO: 'Recibido',
            CANCELADO: 'Cancelado',
            RECHAZADO: 'Rechazado',
        };

        return estadoMap[estado] || estado || '-';
    };

    const viewTransferDetail = async (transferId) => {
        try {
            const response = await fetch(`/traslados/api/transferencias/${transferId}/`, {
                method: 'GET',
                headers: {
                    Accept: 'application/json',
                },
            });

            const data = await parseJsonResponse(response);
            const detalles = data.detalles || [];

            let productosTexto = 'Sin productos registrados.';

            if (detalles.length > 0) {
                productosTexto = detalles.map((item) => {
                    const recibido = item.cantidad_recibida !== undefined
                        ? ` | Recibido: ${item.cantidad_recibida}`
                        : '';

                    return `• ${item.producto_nombre} | Lote: ${item.lote} | Cantidad: ${item.cantidad}${recibido}`;
                }).join('\n');
            }

            alert(
                `Traslado #${data.id}\n\n` +
                `Origen: ${data.sucursal_origen_nombre}\n` +
                `Destino: ${data.sucursal_destino_nombre}\n` +
                `Estado: ${renderStatus(data.estado)}\n` +
                `Solicitado por: ${data.usuario_solicita || '-'}\n` +
                `Enviado por: ${data.usuario_envia || '-'}\n` +
                `Recibido por: ${data.usuario_recibe || '-'}\n\n` +
                `Productos:\n${productosTexto}`
            );

        } catch (error) {
            alert(`Error: ${error.message}`);
        }
    };

    const handleTransferAction = async (action, transferId, button = null) => {
        let url = '';
        let confirmationMessage = '';

        if (action === 'ver') {
            await viewTransferDetail(transferId);
            return;
        }

        if (action === 'enviar') {
            url = `/traslados/api/transferencias/${transferId}/enviar/`;
            confirmationMessage = '¿Seguro que quieres enviar este traslado? El stock se descontará de la sucursal origen.';
        }

        if (action === 'recibir') {
            url = `/traslados/api/transferencias/${transferId}/recibir/`;
            confirmationMessage = '¿Seguro que quieres recibir este traslado? El stock se añadirá a la sucursal destino.';
        }

        if (action === 'eliminar') {
            url = `/traslados/api/transferencias/${transferId}/eliminar/`;
            confirmationMessage = '¿Seguro que quieres eliminar este traslado? Esta acción no se puede deshacer.';
        }

        if (!url) return;

        if (!confirm(confirmationMessage)) return;

        try {
            setButtonLoading(button, true);

            const result = await postAction(url);

            alert(result.message || result.status || 'Operación realizada correctamente.');
            window.location.reload();

        } catch (error) {
            alert(`Error: ${error.message}`);
            setButtonLoading(button, false);
        }
    };

    const applySearch = () => {
        if (!searchInput) return;

        const term = searchInput.value.toLowerCase().trim();
        const rows = document.querySelectorAll('.transfer-row');

        rows.forEach((row) => {
            const text = (row.dataset.search || '').toLowerCase();
            row.style.display = text.includes(term) ? '' : 'none';
        });

        updateCount();
    };

    if (tableBody) {
        tableBody.addEventListener('click', (event) => {
            const button = event.target.closest('.action-btn');
            if (!button) return;

            handleTransferAction(
                button.dataset.action,
                button.dataset.id,
                button
            );
        });
    }

    if (searchInput) {
        searchInput.addEventListener('input', applySearch);
    }

    updateCount();
});