document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('transfer-form');
    const sucursalOrigenSelect = document.getElementById('sucursal-origen');
    const sucursalDestinoSelect = document.getElementById('sucursal-destino');
    const observacionesInput = document.getElementById('observaciones');
    const stockSearchInput = document.getElementById('stock-search');
    const suggestionsContainer = document.getElementById('stock-suggestions');
    const transferDetailsBody = document.getElementById('transfer-details-body');
    const saveTransferBtn = document.getElementById('save-transfer-btn');

    let transferItems = [];

    const getCsrfToken = () => {
        const input = document.querySelector('[name=csrfmiddlewaretoken]');
        return input ? input.value : '';
    };

    const parseJsonResponse = async (response) => {
        const contentType = response.headers.get('content-type') || '';

        if (!contentType.includes('application/json')) {
            const text = await response.text();
            throw new Error('La respuesta del servidor no es JSON. Revisa si la URL existe o si la sesión expiró.');
        }

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || data.detail || 'Ocurrió un error en el servidor.');
        }

        return data;
    };

    const resetProducts = () => {
        transferItems = [];
        renderTransferTable();
        stockSearchInput.value = '';
        suggestionsContainer.innerHTML = '';
        suggestionsContainer.classList.add('hidden');
    };

    const enableStockSearch = () => {
        if (sucursalOrigenSelect.value) {
            stockSearchInput.disabled = false;
            stockSearchInput.placeholder = 'Buscar producto en stock de origen...';
        } else {
            stockSearchInput.disabled = true;
            stockSearchInput.placeholder = 'Seleccione una sucursal de origen primero';
        }
    };

    sucursalOrigenSelect.addEventListener('change', () => {
        enableStockSearch();
        resetProducts();
    });

    stockSearchInput.addEventListener('input', async (event) => {
        const query = event.target.value.trim();
        const sucursalId = sucursalOrigenSelect.value;

        if (query.length < 2 || !sucursalId) {
            suggestionsContainer.innerHTML = '';
            suggestionsContainer.classList.add('hidden');
            return;
        }

        try {
            const url = `/inventario/api/stock/buscar/?sucursal_id=${encodeURIComponent(sucursalId)}&search=${encodeURIComponent(query)}`;
            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    Accept: 'application/json'
                }
            });

            const data = await parseJsonResponse(response);
            const stockItems = data.results || data;

            suggestionsContainer.innerHTML = '';

            if (!stockItems || stockItems.length === 0) {
                suggestionsContainer.classList.add('hidden');
                return;
            }

            suggestionsContainer.classList.remove('hidden');

            stockItems.forEach((stock) => {
                const item = document.createElement('button');
                item.type = 'button';
                item.className = 'block w-full border-b border-slate-100 px-4 py-3 text-left transition hover:bg-emerald-50 last:border-b-0';
                item.innerHTML = `
                    <p class="text-sm font-black text-slate-900">${stock.producto_nombre || '-'}</p>
                    <p class="mt-1 text-xs font-semibold text-slate-500">
                        Lote: ${stock.lote || '-'} | Disponible: ${stock.cantidad || 0} | Vence: ${stock.fecha_vencimiento || '-'}
                    </p>
                `;

                item.addEventListener('click', () => addStockItemToTransfer(stock));
                suggestionsContainer.appendChild(item);
            });

        } catch (error) {
            console.error('Error buscando stock:', error);
            suggestionsContainer.innerHTML = `
                <div class="px-4 py-3 text-sm font-semibold text-rose-500">
                    ${error.message}
                </div>
            `;
            suggestionsContainer.classList.remove('hidden');
        }
    });

    function addStockItemToTransfer(stockItem) {
        if (transferItems.some(item => String(item.stock_origen) === String(stockItem.id))) {
            alert('Este lote ya fue agregado al traslado.');
            return;
        }

        transferItems.push({
            producto: stockItem.producto || stockItem.producto_id,
            stock_origen: stockItem.id,
            producto_nombre: stockItem.producto_nombre,
            lote: stockItem.lote,
            cantidad_disponible: Number(stockItem.cantidad || 0),
            cantidad: 1
        });

        renderTransferTable();

        stockSearchInput.value = '';
        suggestionsContainer.innerHTML = '';
        suggestionsContainer.classList.add('hidden');
    }

    function renderTransferTable() {
        transferDetailsBody.innerHTML = '';

        if (transferItems.length === 0) {
            transferDetailsBody.innerHTML = `
                <tr>
                    <td colspan="5" class="px-4 py-10 text-center text-sm font-semibold text-slate-400">
                        Aún no agregaste productos al traslado.
                    </td>
                </tr>
            `;
            return;
        }

        transferItems.forEach((item, index) => {
            const row = document.createElement('tr');
            row.className = 'border-b border-slate-100 last:border-b-0';

            row.innerHTML = `
                <td class="px-3 py-4">
                    <p class="text-sm font-black text-slate-900">${item.producto_nombre || '-'}</p>
                </td>

                <td class="px-3 py-4">
                    <span class="inline-flex rounded-xl border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs font-bold text-slate-600">
                        ${item.lote || '-'}
                    </span>
                </td>

                <td class="px-3 py-4 text-center">
                    <span class="text-sm font-black text-emerald-600">${item.cantidad_disponible}</span>
                </td>

                <td class="px-3 py-4 text-center">
                    <input
                        type="number"
                        min="1"
                        max="${item.cantidad_disponible}"
                        value="${item.cantidad}"
                        data-index="${index}"
                        class="transfer-quantity-input w-24 rounded-xl border border-slate-200 bg-white px-3 py-2 text-center text-sm font-bold text-slate-700 outline-none focus:border-emerald-400 focus:ring-4 focus:ring-emerald-100"
                    >
                </td>

                <td class="px-3 py-4 text-center">
                    <button
                        type="button"
                        data-index="${index}"
                        class="remove-transfer-item inline-flex h-9 w-9 items-center justify-center rounded-xl border border-rose-100 bg-rose-50 text-lg font-black text-rose-500 transition hover:bg-rose-100"
                    >
                        ×
                    </button>
                </td>
            `;

            transferDetailsBody.appendChild(row);
        });
    }

    transferDetailsBody.addEventListener('input', (event) => {
        const input = event.target.closest('.transfer-quantity-input');

        if (!input) return;

        const index = Number(input.dataset.index);
        let value = Number(input.value || 0);
        const max = transferItems[index].cantidad_disponible;

        if (value < 1) value = 1;
        if (value > max) value = max;

        input.value = value;
        transferItems[index].cantidad = value;
    });

    transferDetailsBody.addEventListener('click', (event) => {
        const button = event.target.closest('.remove-transfer-item');

        if (!button) return;

        const index = Number(button.dataset.index);
        transferItems.splice(index, 1);
        renderTransferTable();
    });

    saveTransferBtn.addEventListener('click', async () => {
        const sucursalOrigen = sucursalOrigenSelect.value;
        const sucursalDestino = sucursalDestinoSelect.value;

        if (!sucursalOrigen) {
            alert('Selecciona la sucursal de origen.');
            return;
        }

        if (!sucursalDestino) {
            alert('Selecciona la sucursal de destino.');
            return;
        }

        if (sucursalOrigen === sucursalDestino) {
            alert('La sucursal de origen y destino no pueden ser la misma.');
            return;
        }

        if (transferItems.length === 0) {
            alert('Agrega al menos un producto al traslado.');
            return;
        }

        const data = {
            sucursal_origen: sucursalOrigen,
            sucursal_destino: sucursalDestino,
            observaciones: observacionesInput.value,
            detalles: transferItems.map(item => ({
                producto: item.producto,
                stock_origen: item.stock_origen,
                cantidad: item.cantidad
            }))
        };

        try {
            saveTransferBtn.disabled = true;
            saveTransferBtn.textContent = 'Guardando...';

            const response = await fetch('/traslados/api/transferencias/crear/', {
                method: 'POST',
                headers: {
                    Accept: 'application/json',
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                },
                body: JSON.stringify(data)
            });

            await parseJsonResponse(response);

            alert('Traslado creado correctamente.');
            window.location.href = form.dataset.successUrl;

        } catch (error) {
            alert(`Error: ${error.message}`);
        } finally {
            saveTransferBtn.disabled = false;
            saveTransferBtn.textContent = 'Crear traslado';
        }
    });

    enableStockSearch();
    renderTransferTable();
});