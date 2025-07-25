// static/js/traslados/traslado_form.js

document.addEventListener('DOMContentLoaded', () => {
    const sucursalOrigenSelect = document.getElementById('sucursal-origen');
    const stockSearchInput = document.getElementById('stock-search');
    const suggestionsContainer = document.getElementById('stock-suggestions');
    const transferDetailsBody = document.getElementById('transfer-details-body');
    const saveTransferBtn = document.getElementById('save-transfer-btn');

    let transferItems = []; // Almacena los productos a transferir

    // Habilita/deshabilita el buscador de stock
    sucursalOrigenSelect.addEventListener('change', () => {
        if (sucursalOrigenSelect.value) {
            stockSearchInput.disabled = false;
            stockSearchInput.placeholder = 'Buscar producto en stock de origen...';
        } else {
            stockSearchInput.disabled = true;
            stockSearchInput.placeholder = 'Seleccione una sucursal de origen primero';
        }
    });

    // Lógica de autocompletado para el stock
    stockSearchInput.addEventListener('input', async (e) => {
        const query = e.target.value;
        const sucursalId = sucursalOrigenSelect.value;

        if (query.length < 2 || !sucursalId) {
            suggestionsContainer.classList.add('hidden');
            return;
        }

        try {
            // Asegúrate que la URL apunte a la API de inventario
            const response = await fetch(`/inventario/api/stock/buscar/?sucursal_id=${sucursalId}&search=${query}`);
            const data = await response.json(); // Recibimos el objeto completo

            // --- CORRECCIÓN AQUÍ ---
            // Accedemos al array de productos que está dentro de 'data.results'
            const stockItems = data.results;
            // ---------------------

            suggestionsContainer.innerHTML = '';
            if (stockItems && stockItems.length > 0) {
                suggestionsContainer.classList.remove('hidden');
                stockItems.forEach(stock => {
                    const item = document.createElement('div');
                    item.className = 'p-3 hover:bg-slate-700 cursor-pointer border-b border-slate-800 last:border-b-0';
                    item.innerHTML = `
                        <p class="font-semibold text-white">${stock.producto_nombre}</p>
                        <p class="text-xs text-slate-400">Lote: ${stock.lote} | Disp: ${stock.cantidad} | Venc: ${stock.fecha_vencimiento}</p>
                    `;
                    item.addEventListener('click', () => addStockItemToTransfer(stock));
                    suggestionsContainer.appendChild(item);
                });
            } else {
                suggestionsContainer.classList.add('hidden');
            }
        } catch (error) {
            console.error("Error buscando stock:", error);
        }
    });
    
    // Añade un item a la tabla de transferencia
    function addStockItemToTransfer(stockItem) {
        // Evita añadir el mismo lote dos veces
        if (transferItems.some(item => item.stock_origen_id === stockItem.id)) {
            alert('Este lote ya ha sido añadido a la transferencia.');
            return;
        }

        const item = {
            stock_origen_id: stockItem.id,
            producto_nombre: stockItem.producto_nombre,
            lote: stockItem.lote,
            cantidad_disponible: stockItem.cantidad,
            cantidad: 1 // Cantidad por defecto
        };
        transferItems.push(item);
        renderTransferTable();
        
        stockSearchInput.value = '';
        suggestionsContainer.classList.add('hidden');
    }

    // Dibuja la tabla con los items
    function renderTransferTable() {
        transferDetailsBody.innerHTML = '';
        transferItems.forEach((item, index) => {
            const row = document.createElement('tr');
            // He añadido la clase 'align-middle' a cada <td> para centrar todo verticalmente
            row.innerHTML = `
                <td class="p-2 align-middle">${item.producto_nombre}</td>
                <td class="p-2 align-middle">${item.lote}</td>
                <td class="p-2 align-middle text-center font-semibold">${item.cantidad_disponible}</td>
                <td class="p-2 align-middle text-center">
                    <input type="number" class="form-input py-1 w-24 text-center bg-slate-900 border-slate-700" value="${item.cantidad}" min="1" max="${item.cantidad_disponible}" data-index="${index}">
                </td>
                <td class="p-2 align-middle text-center">
                    <button class="text-rose-400 hover:text-rose-300 transition-colors" data-index="${index}" title="Eliminar Producto">
                        <button class="text-rose-400 hover:text-rose-300 transition-colors text-2xl font-bold" data-index="${index}" title="Eliminar Producto">
                            &times;
                        </button>
                    </button>
                </td>
            `;
            transferDetailsBody.appendChild(row);
        });
    }

    // Listener para actualizar cantidad o eliminar item
    transferDetailsBody.addEventListener('change', (e) => {
        if (e.target.type === 'number') {
            const index = e.target.dataset.index;
            transferItems[index].cantidad = parseInt(e.target.value);
        }
    });
    transferDetailsBody.addEventListener('click', (e) => {
        if (e.target.tagName === 'BUTTON') {
            const index = e.target.dataset.index;
            transferItems.splice(index, 1);
            renderTransferTable();
        }
    });

    // Lógica para guardar el traslado
    saveTransferBtn.addEventListener('click', async () => {
        const data = {
            sucursal_origen: document.getElementById('sucursal-origen').value,
            sucursal_destino: document.getElementById('sucursal-destino').value,
            observaciones: document.getElementById('observaciones').value,
            detalles_write: transferItems.map(item => ({
                stock_origen_id: item.stock_origen_id,
                cantidad: item.cantidad
            }))
        };

        // Aquí harías el fetch POST a tu API de /traslados/api/transferencias/
        console.log("Enviando al backend:", data);
        
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        const successUrl = document.getElementById('transfer-form').dataset.successUrl;

        try {
            const response = await fetch('/traslados/api/transferencias/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrftoken },
                body: JSON.stringify(data)
            });
            if (!response.ok) throw await response.json();
            
            alert('¡Solicitud de traslado creada con éxito!');
            window.location.href = successUrl; 

        } catch(error) {
            console.error("Error al crear la transferencia:", error);
            alert('Error: ' + JSON.stringify(error));
        }
    });
});