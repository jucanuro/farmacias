document.addEventListener('DOMContentLoaded', () => {
    // ESTADO
    const compraPkElement = document.getElementById('compra-pk-data');
    // Usamos el valor del elemento HTML, si no existe o está vacío, será null.
    const compraPk = compraPkElement ? JSON.parse(compraPkElement.textContent) : null;
    
    let compraId = null;
    let lineItems = [];

    // ELEMENTOS DEL DOM
    const proveedorSelect = document.getElementById('proveedor');
    const sucursalSelect = document.getElementById('sucursal');
    const numeroFacturaInput = document.getElementById('numero_factura');
    const purchaseDetailsBody = document.getElementById('purchase-details-body');
    const productSearchInput = document.getElementById('product-search');
    const suggestionsContainer = document.getElementById('product-suggestions');
    const processButton = document.getElementById('process-button');
    const subtotalDisplay = document.getElementById('subtotal-display');
    const impuestosDisplay = document.getElementById('impuestos-display');
    const totalDisplay = document.getElementById('total-display');
    const addProductSection = document.getElementById('add-product-section');
    const pageSubtitle = document.getElementById('page-subtitle');
    
    // Obtener el token CSRF y el PK de la compra de los elementos HTML
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    const inicializarFormulario = async () => {
        // Modo Edición: Cargar datos de una compra existente
        if (compraPk) {
            await cargarCompraExistente(compraPk);
        } else {
            // Modo Creación: Los datos ya están en el HTML, solo se asigna el evento
            purchaseDetailsBody.innerHTML = '<tr><td colspan="8" class="text-center p-8 text-slate-400">Complete la información de la factura para empezar.</td></tr>';
            if(numeroFacturaInput){
                numeroFacturaInput.addEventListener('blur', crearOActualizarCompraHeader);
            }
        }
    };
    
    const cargarCompraExistente = async (pk) => {
        try {
            const response = await fetch(`/compras/api/compras/${pk}/`);
            if (!response.ok) throw new Error('Compra no encontrada.');
            
            const compra = await response.json();
            compraId = compra.id;

            proveedorSelect.innerHTML = `<option value="${compra.proveedor}" selected>${compra.proveedor_nombre}</option>`;
            sucursalSelect.innerHTML = `<option value="${compra.sucursal_destino}" selected>${compra.sucursal_destino_nombre}</option>`;
            numeroFacturaInput.value = compra.numero_factura_proveedor;
            
            const esEditable = compra.estado === 'PENDIENTE';
            proveedorSelect.disabled = true;
            sucursalSelect.disabled = true;
            numeroFacturaInput.disabled = !esEditable;

            lineItems = compra.detalles.map(d => ({
                id: d.id,
                producto: d.producto,
                producto_nombre: d.producto_nombre,
                presentacion: d.presentacion,
                unidad_seleccionada_id: d.presentacion,
                unidades_disponibles: [{ id: d.presentacion, nombre: d.presentacion_nombre }],
                cantidad_recibida: d.cantidad_recibida,
                precio_unitario_compra: d.precio_unitario_compra,
                lote: d.lote,
                fecha_vencimiento: d.fecha_vencimiento,
            }));

            if (!esEditable) {
                processButton.disabled = true;
                processButton.textContent = `Compra ${compra.estado}`;
                processButton.classList.replace('bg-emerald-500', 'bg-slate-600');
                if (addProductSection) {
                    addProductSection.style.display = 'none';
                }
                if (pageSubtitle) {
                    pageSubtitle.textContent = `Esta compra ya fue ${compra.estado.toLowerCase()} y no puede ser modificada.`;
                }
            } else {
                if (pageSubtitle) {
                     pageSubtitle.textContent = `Modifica los detalles de la compra registrada.`;
                }
                 numeroFacturaInput.addEventListener('blur', crearOActualizarCompraHeader);
            }
            renderTableRows(!esEditable);
        } catch (error) {
            console.error(error);
            purchaseDetailsBody.innerHTML = `<tr><td colspan="8" class="text-center p-8 text-rose-400">Error: ${error.message}</td></tr>`;
        }
    };

    const crearOActualizarCompraHeader = async () => {
        if (!proveedorSelect.value || !sucursalSelect.value || !numeroFacturaInput.value) { return; }
        const url = compraId ? `/compras/api/compras/${compraId}/` : `/compras/api/compras/`;
        const method = compraId ? 'PATCH' : 'POST';
        const data = {
            proveedor: proveedorSelect.value,
            sucursal_destino: sucursalSelect.value,
            numero_factura_proveedor: numeroFacturaInput.value,
        };
        try {
            const response = await fetch(url, {
                method: method,
                headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrftoken },
                body: JSON.stringify(data)
            });
            if (!response.ok) throw await response.json();
            const savedCompra = await response.json();
            if (!compraId) {
                compraId = savedCompra.id;
                proveedorSelect.disabled = true;
                sucursalSelect.disabled = true;
                numeroFacturaInput.disabled = true;
                purchaseDetailsBody.innerHTML = '<tr><td colspan="8" class="text-center p-8 text-slate-400">Encabezado guardado. Ya puedes añadir productos.</td></tr>';
            }
        } catch (error) {
            let errorMessage = 'No se pudo crear o actualizar la compra.\n\n';
            for (const field in error) { if (Array.isArray(error[field])) { errorMessage += `${field}: ${error[field].join(', ')}\n`; } }
            alert(errorMessage);
        }
    };

    productSearchInput.addEventListener('input', (e) => {
        const query = e.target.value;
        if (query.length < 2) { suggestionsContainer.classList.add('hidden'); return; }
        fetch(`/inventario/api/productos/autocomplete/?search=${query}`, { credentials: 'include' })
            .then(res => res.ok ? res.json() : Promise.reject(res))
            .then(data => {
                suggestionsContainer.innerHTML = '';
                if (data.results && data.results.length > 0) {
                    suggestionsContainer.classList.remove('hidden');
                    data.results.forEach(product => {
                        const div = document.createElement('div');
                        div.className = 'p-3 hover:bg-slate-700 cursor-pointer border-b border-slate-800';
                        div.innerHTML = `<p class="font-semibold text-white">${product.nombre} ${product.concentracion || ''}</p><p class="text-xs text-slate-400">${product.laboratorio_nombre}</p>`;
                        div.dataset.product = JSON.stringify(product);
                        div.addEventListener('click', handleSuggestionClick);
                        suggestionsContainer.appendChild(div);
                    });
                } else { suggestionsContainer.classList.add('hidden'); }
            }).catch(err => console.error('Error en autocomplete:', err));
    });

    const handleSuggestionClick = (e) => {
        if (!compraId) { alert('Por favor, primero completa y guarda la información de la factura.'); return; }
        const productData = JSON.parse(e.currentTarget.dataset.product);
        lineItems.push({
            producto: productData.id,
            producto_nombre: `${productData.nombre} ${productData.concentracion || ''}`,
            unidades_disponibles: productData.unidades_jerarquia || [],
            lote: '', fecha_vencimiento: '', cantidad_recibida: '', precio_unitario_compra: '',
        });
        productSearchInput.value = '';
        suggestionsContainer.classList.add('hidden');
        renderTableRows(processButton.disabled);
    };

    const guardarDetalle = async (itemIndex) => {
        const item = lineItems[itemIndex];
        if (!item || !item.lote || !item.fecha_vencimiento || !(parseFloat(item.cantidad_recibida) > 0) || !(parseFloat(item.precio_unitario_compra) >= 0)) return;

        const esNuevo = !item.id;
        const url = esNuevo ? `/compras/api/detalles-compra/` : `/compras/api/detalles-compra/${item.id}/`;
        const method = esNuevo ? 'POST' : 'PATCH';
        const data = {
            producto: item.producto, lote: item.lote, fecha_vencimiento: item.fecha_vencimiento,
            cantidad_recibida: item.cantidad_recibida, precio_unitario_compra: item.precio_unitario_compra,
            presentacion: item.unidad_seleccionada_id,
        };
        if (esNuevo) data.compra = compraId;

        try {
            const response = await fetch(url, { method: method, headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrftoken }, body: JSON.stringify(data) });
            if (!response.ok) throw await response.json();
            const savedDetalle = await response.json();
            Object.assign(lineItems[itemIndex], savedDetalle);
            renderTableRows(processButton.disabled);
        } catch (error) { console.error(`Error guardando detalle:`, error); }
    };

    const eliminarDetalle = async (itemIndex) => {
        if (!confirm('¿Estás seguro?')) return;
        const item = lineItems[itemIndex];
        if (item && item.id) {
            try {
                await fetch(`/compras/api/detalles-compra/${item.id}/`, { method: 'DELETE', headers: { 'X-CSRFToken': csrftoken }});
            } catch (error) { alert('No se pudo eliminar el item de la base de datos.'); return; }
        }
        lineItems.splice(itemIndex, 1);
        renderTableRows(processButton.disabled);
    };

    async function procesarCompra() {
        if (!compraId) { alert('No hay una compra activa para procesar.'); return; }
        if (!confirm('¿Estás seguro de que deseas procesar esta compra? El stock se actualizará y ya no podrás editarla.')) return;

        processButton.disabled = true; processButton.textContent = 'Procesando...';
        try {
            const response = await fetch(`/compras/api/compras/${compraId}/procesar/`, { method: 'POST', headers: { 'X-CSRFToken': csrftoken }});
            if (!response.ok) throw await response.json();
            const result = await response.json();
            alert(result.status || '¡Compra procesada con éxito!');
            window.location.href = comprasHomeUrl;
        } catch (error) {
            alert('Error: ' + (error.error || 'No se pudo procesar la compra.'));
            processButton.disabled = false;
            processButton.textContent = 'Finalizar y Procesar'; // Corregí el texto del botón
        }
    }
    
    function renderTableRows(isReadOnly = false) {
        purchaseDetailsBody.innerHTML = '';
        if(lineItems.length === 0) {
             const message = compraId ? "Añade productos a la compra." : "Complete la información de la factura para empezar.";
             purchaseDetailsBody.innerHTML = `<tr><td colspan="8" class="text-center p-8 text-slate-400">${message}</td></tr>`;
             updateTotalsUI(); // Limpiar totales si no hay items
             return;
        }

        lineItems.forEach((item, index) => {
            const row = document.createElement('tr');
            row.dataset.index = index;
            const guardadoIndicator = item.id ? 'border-l-4 border-emerald-500' : 'border-l-4 border-amber-500';
            row.className = `transition-all duration-300 ${guardadoIndicator}`;
            const subtotal = (parseFloat(item.cantidad_recibida) || 0) * (parseFloat(item.precio_unitario_compra) || 0);

            let unitOptionsHTML = '';
            if (item.unidades_disponibles && item.unidades_disponibles.length > 0) {
                item.unidades_disponibles.forEach(unit => {
                    const isSelected = item.unidad_seleccionada_id == unit.id;
                    unitOptionsHTML += `<option value="${unit.id}" ${isSelected ? 'selected' : ''}>${unit.nombre}</option>`;
                });
            } else { unitOptionsHTML = '<option value="">N/A</option>'; }
            
            const disabledAttr = isReadOnly ? 'disabled' : '';

            row.innerHTML = `
                <td class="p-2 align-middle"><p class="text-white font-medium text-sm">${item.producto_nombre}</p></td>
                <td class="p-2 align-middle"><select name="unidad_seleccionada_id" class="form-select py-1 data-field" ${disabledAttr}>${unitOptionsHTML}</select></td>
                <td class="p-2 align-middle"><input type="text" name="lote" class="form-input py-1 data-field" value="${item.lote || ''}" placeholder="Lote" ${disabledAttr}></td>
                <td class="p-2 align-middle"><input type="date" name="fecha_vencimiento" class="form-input py-1 data-field" value="${item.fecha_vencimiento || ''}" ${disabledAttr}></td>
                <td class="p-2 align-middle"><input type="number" name="cantidad_recibida" class="form-input py-1 text-right data-field" value="${item.cantidad_recibida || ''}" min="0" placeholder="0" ${disabledAttr}></td>
                <td class="p-2 align-middle"><input type="number" name="precio_unitario_compra" class="form-input py-1 text-right data-field" value="${item.precio_unitario_compra || ''}" step="0.01" min="0" placeholder="0.00" ${disabledAttr}></td>
                <td class="p-2 align-middle text-right font-mono text-white subtotal-cell">S/ ${subtotal.toFixed(2)}</td>
                <td class="p-2 align-middle text-center">${!isReadOnly ? `<button type="button" class="text-rose-400 hover:text-rose-300 delete-row-btn" title="Eliminar Fila">❌</button>` : ''}</td>
            `;
            purchaseDetailsBody.appendChild(row);
        });
        
        purchaseDetailsBody.querySelectorAll('.data-field').forEach(input => {
            input.addEventListener('input', e => {
                const row = e.target.closest('tr');
                const index = row.dataset.index;
                lineItems[index][e.target.name] = e.target.value;
                const cantidad = parseFloat(lineItems[index].cantidad_recibida) || 0;
                const precio = parseFloat(lineItems[index].precio_unitario_compra) || 0;
                row.querySelector('.subtotal-cell').textContent = `S/ ${(cantidad * precio).toFixed(2)}`;
                updateTotalsUI();
            });
            input.addEventListener('blur', e => guardarDetalle(e.target.closest('tr').dataset.index));
        });

        purchaseDetailsBody.querySelectorAll('.delete-row-btn').forEach(button => {
            button.addEventListener('click', e => eliminarDetalle(e.target.closest('tr').dataset.index));
        });
        updateTotalsUI();
    }
    
    function updateTotalsUI() {
        const subtotal = lineItems.reduce((acc, item) => acc + ((parseFloat(item.cantidad_recibida) || 0) * (parseFloat(item.precio_unitario_compra) || 0)), 0);
        const impuestos = subtotal * 0.18;
        const total = subtotal + impuestos;
        subtotalDisplay.textContent = `S/ ${subtotal.toFixed(2)}`;
        impuestosDisplay.textContent = `S/ ${impuestos.toFixed(2)}`;
        totalDisplay.textContent = `S/ ${total.toFixed(2)}`;
    }
    
    document.addEventListener('click', (e) => { 
        if (productSearchInput && !productSearchInput.contains(e.target) && !suggestionsContainer.contains(e.target)) { 
            suggestionsContainer.classList.add('hidden'); 
        } 
    });

    if (processButton) {
        processButton.addEventListener('click', procesarCompra);
    }
    
    inicializarFormulario();
});