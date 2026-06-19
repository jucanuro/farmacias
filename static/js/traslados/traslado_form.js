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

    const mode = form?.dataset.mode || 'crear';
    const transferId = form?.dataset.transferId || '';

    const getCsrfToken = () => {
        const input = document.querySelector('[name=csrfmiddlewaretoken]');
        return input ? input.value : '';
    };

    const parseJsonResponse = async (response) => {
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || data.detail || 'Ocurrió un error.');
        }

        return data;
    };

    const toNumber = (value) => {
        if (value === null || value === undefined || value === '') return 0;
        const clean = String(value).replace(',', '.').trim();
        const number = Number(clean);
        return Number.isFinite(number) ? number : 0;
    };

    const normalizeStock = (stock) => {
        const disponible = toNumber(
            stock.cantidad_disponible ??
            stock.stock_disponible ??
            stock.disponible ??
            stock.cantidad_actual ??
            stock.cantidad_total ??
            stock.cantidad ??
            stock.stock ??
            0
        );

        return {
            id: stock.id,
            producto: stock.producto || stock.producto_id,
            stock_origen: stock.id,
            producto_nombre: stock.producto_nombre || stock.nombre_producto || stock.nombre || '-',
            lote: stock.lote || '-',
            fecha_vencimiento: stock.fecha_vencimiento || stock.vencimiento || '-',
            cantidad_disponible: disponible,
            cantidad: 1,
        };
    };

    const enableStockSearch = () => {
        const enabled = Boolean(sucursalOrigenSelect.value);
        stockSearchInput.disabled = !enabled;
        stockSearchInput.placeholder = enabled
            ? 'Buscar producto en stock de origen...'
            : 'Selecciona sucursal origen primero';
    };

    const clearSuggestions = () => {
        suggestionsContainer.innerHTML = '';
        suggestionsContainer.classList.add('hidden');
    };

    const resetProducts = () => {
        transferItems = [];
        renderTransferTable();
        stockSearchInput.value = '';
        clearSuggestions();
    };

    sucursalOrigenSelect.addEventListener('change', () => {
        enableStockSearch();
        resetProducts();
    });

    stockSearchInput.addEventListener('input', async (event) => {
        const query = event.target.value.trim();
        const sucursalId = sucursalOrigenSelect.value;

        if (query.length < 2 || !sucursalId) {
            clearSuggestions();
            return;
        }

        try {
            const url = `/inventario/api/stock/buscar/?sucursal_id=${encodeURIComponent(sucursalId)}&search=${encodeURIComponent(query)}`;

            const response = await fetch(url, {
                method: 'GET',
                headers: { Accept: 'application/json' },
            });

            const data = await parseJsonResponse(response);
            const stockItems = data.results || [];

            suggestionsContainer.innerHTML = '';

            if (!stockItems.length) {
                suggestionsContainer.innerHTML = `
                    <div class="px-4 py-3 text-sm font-semibold text-slate-400">
                        No se encontraron productos con stock en esta sucursal.
                    </div>
                `;
                suggestionsContainer.classList.remove('hidden');
                return;
            }

            stockItems.forEach((rawStock) => {
                const stock = normalizeStock(rawStock);

                const item = document.createElement('button');
                item.type = 'button';
                item.className = 'block w-full border-b border-slate-100 px-4 py-3 text-left transition hover:bg-emerald-50 last:border-b-0';

                item.innerHTML = `
                    <p class="text-sm font-black text-slate-900">${stock.producto_nombre}</p>
                    <p class="mt-1 text-xs font-semibold text-slate-500">
                        Lote: ${stock.lote} | Disponible: ${stock.cantidad_disponible} | Vence: ${stock.fecha_vencimiento}
                    </p>
                `;

                item.addEventListener('click', () => addStockItemToTransfer(stock));
                suggestionsContainer.appendChild(item);
            });

            suggestionsContainer.classList.remove('hidden');

        } catch (error) {
            suggestionsContainer.innerHTML = `
                <div class="px-4 py-3 text-sm font-semibold text-rose-500">
                    ${error.message}
                </div>
            `;
            suggestionsContainer.classList.remove('hidden');
        }
    });

    function addStockItemToTransfer(stock) {
        if (transferItems.some(item => String(item.stock_origen) === String(stock.stock_origen))) {
            alert('Este lote ya fue agregado al traslado.');
            return;
        }

        if (stock.cantidad_disponible <= 0) {
            alert('Este lote no tiene stock disponible.');
            return;
        }

        transferItems.push(stock);
        renderTransferTable();
        stockSearchInput.value = '';
        clearSuggestions();
    }

    function renderTransferTable() {
        const mobileBody = document.getElementById('transfer-details-mobile');

        transferDetailsBody.innerHTML = '';
        if (mobileBody) mobileBody.innerHTML = '';

        if (!transferItems.length) {
            const emptyDesktop = `
                <tr id="empty-details-row">
                    <td colspan="6" class="p-5">
                        <div class="rounded-2xl border border-dashed border-slate-300 bg-slate-50 px-4 py-7 text-center">
                            <p class="text-xs font-bold text-slate-500">Aún no agregaste productos.</p>
                            <p class="mt-1 text-[11px] text-slate-400">Busca productos disponibles en la sucursal origen.</p>
                        </div>
                    </td>
                </tr>
            `;

            const emptyMobile = `
                <div class="p-4">
                    <div class="rounded-2xl border border-dashed border-slate-300 bg-slate-50 px-4 py-7 text-center">
                        <p class="text-xs font-bold text-slate-500">Aún no agregaste productos.</p>
                        <p class="mt-1 text-[11px] text-slate-400">Busca productos disponibles en la sucursal origen.</p>
                    </div>
                </div>
            `;

            transferDetailsBody.innerHTML = emptyDesktop;
            if (mobileBody) mobileBody.innerHTML = emptyMobile;
            return;
        }

        transferItems.forEach((item, index) => {
            const row = document.createElement('tr');
            row.className = 'border-b border-slate-100 last:border-b-0';

            row.innerHTML = `
                <td class="p-3 align-middle">
                    <p class="text-xs font-black text-slate-900 truncate">${item.producto_nombre}</p>
                </td>
                <td class="p-3 align-middle">
                    <span class="inline-flex rounded-xl border border-slate-200 bg-slate-50 px-2.5 py-1 text-[11px] font-bold text-slate-600">${item.lote}</span>
                </td>
                <td class="p-3 align-middle text-center text-xs font-bold text-slate-500">${item.fecha_vencimiento}</td>
                <td class="p-3 align-middle text-center text-xs font-black text-emerald-600">${item.cantidad_disponible}</td>
                <td class="p-3 align-middle text-center">
                    <input type="number" min="1" max="${item.cantidad_disponible}" value="${item.cantidad}" data-index="${index}"
                        class="transfer-quantity-input w-24 rounded-xl border border-slate-200 bg-white px-2 py-1.5 text-center text-xs font-bold text-slate-700 outline-none focus:border-emerald-400 focus:ring-4 focus:ring-emerald-100">
                </td>
                <td class="p-3 align-middle text-right">
                    <button type="button" data-index="${index}"
                        class="remove-transfer-item inline-flex h-8 w-8 items-center justify-center rounded-xl border border-rose-100 bg-rose-50 text-base font-black text-rose-500 hover:bg-rose-100">×</button>
                </td>
            `;

            transferDetailsBody.appendChild(row);

            if (mobileBody) {
                const card = document.createElement('article');
                card.className = 'p-3';

                card.innerHTML = `
                    <div class="rounded-[1.35rem] border border-slate-200 bg-white shadow-sm overflow-hidden">
                        <div class="flex items-start justify-between gap-3 border-b border-slate-100 bg-slate-50/70 px-4 py-3">
                            <div class="min-w-0">
                                <p class="text-sm font-black text-slate-900 leading-5 truncate">
                                    ${item.producto_nombre}
                                </p>
                                <p class="mt-0.5 text-[11px] font-bold text-slate-400">
                                    Lote ${item.lote}
                                </p>
                            </div>

                            <button
                                type="button"
                                data-index="${index}"
                                class="remove-transfer-item inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-2xl border border-rose-100 bg-rose-50 text-lg font-black text-rose-500 transition hover:bg-rose-100"
                            >
                                ×
                            </button>
                        </div>

                        <div class="grid grid-cols-2 gap-2 p-3">
                            <div class="rounded-2xl border border-slate-200 bg-white px-3 py-2.5">
                                <p class="text-[10px] font-black uppercase tracking-widest text-slate-400">
                                    Vence
                                </p>
                                <p class="mt-1 text-sm font-black text-slate-800">
                                    ${item.fecha_vencimiento}
                                </p>
                            </div>

                            <div class="rounded-2xl border border-emerald-100 bg-emerald-50 px-3 py-2.5">
                                <p class="text-[10px] font-black uppercase tracking-widest text-emerald-600">
                                    Disponible
                                </p>
                                <p class="mt-1 text-sm font-black text-emerald-700">
                                    ${item.cantidad_disponible}
                                </p>
                            </div>

                            <div class="col-span-2 rounded-2xl border border-slate-200 bg-white px-3 py-3">
                                <div class="flex items-center justify-between gap-3">
                                    <div>
                                        <p class="text-[10px] font-black uppercase tracking-widest text-slate-400">
                                            Cantidad
                                        </p>
                                        <p class="mt-0.5 text-[11px] font-semibold text-slate-400">
                                            Máximo ${item.cantidad_disponible}
                                        </p>
                                    </div>

                                    <input
                                        type="number"
                                        min="1"
                                        max="${item.cantidad_disponible}"
                                        value="${item.cantidad}"
                                        data-index="${index}"
                                        class="transfer-quantity-input h-11 w-24 rounded-2xl border border-slate-200 bg-slate-50 px-3 text-center text-sm font-black text-slate-800 outline-none focus:border-emerald-400 focus:bg-white focus:ring-4 focus:ring-emerald-100"
                                    >
                                </div>
                            </div>
                        </div>
                    </div>
                `;

                mobileBody.appendChild(card);
            }
        });
    }

    transferDetailsBody.addEventListener('input', (event) => {
        const input = event.target.closest('.transfer-quantity-input');
        if (!input) return;

        const index = Number(input.dataset.index);
        let value = toNumber(input.value);
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

        if (!sucursalOrigen) return alert('Selecciona la sucursal de origen.');
        if (!sucursalDestino) return alert('Selecciona la sucursal de destino.');
        if (sucursalOrigen === sucursalDestino) return alert('La sucursal de origen y destino no pueden ser la misma.');
        if (!transferItems.length) return alert('Agrega al menos un producto al traslado.');

        const data = {
            sucursal_origen: sucursalOrigen,
            sucursal_destino: sucursalDestino,
            observaciones: observacionesInput.value,
            detalles: transferItems.map(item => ({
                producto: item.producto,
                stock_origen: item.stock_origen,
                cantidad: item.cantidad,
            })),
        };

        const isEdit = mode === 'editar' && transferId;

        const url = isEdit
            ? `/traslados/api/transferencias/${transferId}/actualizar/`
            : '/traslados/api/transferencias/crear/';

        const method = isEdit ? 'PUT' : 'POST';

        try {
            saveTransferBtn.disabled = true;
            saveTransferBtn.textContent = isEdit ? 'Actualizando...' : 'Guardando...';

            const response = await fetch(url, {
                method,
                headers: {
                    Accept: 'application/json',
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken(),
                },
                body: JSON.stringify(data),
            });

            await parseJsonResponse(response);

            alert(isEdit ? 'Traslado actualizado correctamente.' : 'Traslado creado correctamente.');
            window.location.href = form.dataset.successUrl;

        } catch (error) {
            alert(`Error: ${error.message}`);
        } finally {
            saveTransferBtn.disabled = false;
            saveTransferBtn.textContent = isEdit ? 'Guardar cambios' : 'Crear traslado';
        }
    });

    enableStockSearch();
    renderTransferTable();
});