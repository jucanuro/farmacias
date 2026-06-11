export function renderProductGrid(productGrid, productos) {
    productGrid.innerHTML = '';
    if (productos.length === 0) {
        productGrid.innerHTML = `<p class="col-span-full text-center text-slate-500 py-16">No se encontraron productos.</p>`;
        return;
    }
    const placeholderSvg = `<svg class="w-full h-full text-slate-700" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m2.25 15.75 5.159-5.159a2.25 2.25 0 0 1 3.182 0l5.159 5.159m-1.5-1.5 1.409-1.409a2.25 2.25 0 0 1 3.182 0l2.909 2.909m-18 3.75h16.5a1.5 1.5 0 0 0 1.5-1.5V6a1.5 1.5 0 0 0-1.5-1.5H3.75A1.5 1.5 0 0 0 2.25 6v12a1.5 1.5 0 0 0 1.5 1.5Zm10.5-11.25h.008v.008h-.008V8.25Zm.375 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Z" /></svg>`;
    productos.forEach(producto => {
        const row = document.createElement('div');
        row.className = 'bg-slate-800 rounded-lg p-3 grid grid-cols-[auto_1fr_auto] items-center gap-4 cursor-pointer hover:bg-slate-700 transition-colors add-to-cart-btn';
        row.dataset.productoJson = JSON.stringify(producto);
        const imageUrl = producto.imagen_producto;
        row.innerHTML = `<div class="w-14 h-14 bg-slate-700/50 rounded-md flex items-center justify-center">${imageUrl ? `<img src="${imageUrl}" alt="${producto.nombre}" class="w-full h-full object-cover rounded-md">` : placeholderSvg}</div><div class="min-w-0"><p class="text-base font-semibold text-white truncate" title="${producto.nombre}">${producto.nombre}</p><p class="text-sm text-slate-400 truncate">${producto.laboratorio_nombre || ''}</p></div><div class="text-right"><p class="text-lg font-bold text-emerald-400 whitespace-nowrap">S/ ${parseFloat(producto.precio_venta || 0).toFixed(2)}</p><p class="text-xs text-slate-400">por unidad</p></div>`;
        productGrid.appendChild(row);
    });
}

export function renderCart(cartItemsContainer, cart, totals) {
    cartItemsContainer.innerHTML = '';

    if (cart.length === 0) {
        cartItemsContainer.innerHTML = `
            <div class="flex min-h-[320px] flex-col items-center justify-center rounded-3xl border border-dashed border-slate-200 bg-white p-8 text-center">
                <div class="flex h-16 w-16 items-center justify-center rounded-3xl bg-emerald-50 text-emerald-500">
                    <svg class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.9">
                        <path d="M3 3h2l.4 2M7 13h10l4-8H5.4" />
                        <path d="M7 13L5.4 5M7 13l-2 6h14M10 21a1 1 0 100-2 1 1 0 000 2zm7 0a1 1 0 100-2 1 1 0 000 2z" />
                    </svg>
                </div>
                <h3 class="mt-5 text-sm font-black uppercase tracking-[0.18em] text-slate-400">Ticket vacío</h3>
                <p class="mt-2 text-sm text-slate-400">Selecciona productos del catálogo para iniciar la venta.</p>
            </div>
        `;
        updateTotalsUI(totals);
        return;
    }

    cartItemsContainer.innerHTML = `
        <div class="overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-sm">
            <div class="grid grid-cols-[1fr_120px_120px_48px] items-center border-b border-slate-100 bg-slate-50 px-4 py-3 text-[10px] font-black uppercase tracking-[0.16em] text-slate-400">
                <div>Producto</div>
                <div class="text-center">Cant.</div>
                <div class="text-right">Total</div>
                <div></div>
            </div>

            <div class="divide-y divide-slate-100">
                ${cart.map(item => {
                    const subtotal = (item.quantity * item.precio_unitario) - (item.monto_descuento_linea || 0);

                    return `
                        <div class="cart-ticket-row grid grid-cols-[1fr_120px_120px_48px] items-center gap-3 px-4 py-4 transition hover:bg-emerald-50/40">
                            <div class="min-w-0">
                                <div class="flex items-start gap-3">
                                    <input 
                                        type="checkbox" 
                                        class="discount-checkbox mt-1 h-4 w-4 rounded border-slate-300 text-emerald-600 focus:ring-emerald-500" 
                                        data-item-id="${item.id}" 
                                        ${item.hasDiscount ? 'checked' : ''} 
                                        title="Aplicar descuento"
                                    >

                                    <div class="min-w-0">
                                        <p class="truncate text-sm font-black text-slate-900" title="${item.nombre}">
                                            ${item.nombre}
                                        </p>
                                        <p class="mt-1 text-xs font-bold text-slate-400">
                                            P. Unit: S/ ${parseFloat(item.precio_unitario).toFixed(2)}
                                        </p>

                                        <div class="mt-2 ${item.hasDiscount ? '' : 'hidden'}">
                                            <label class="mr-2 text-[10px] font-black uppercase tracking-[0.12em] text-rose-400">Dcto.</label>
                                            <div class="inline-flex items-center rounded-xl border border-rose-100 bg-rose-50 px-2 py-1">
                                                <span class="text-xs font-black text-rose-400">S/</span>
                                                <input 
                                                    type="number" 
                                                    value="${item.monto_descuento_linea || '0.00'}" 
                                                    min="0" 
                                                    step="0.10" 
                                                    class="discount-input ml-1 w-20 bg-transparent text-xs font-black text-rose-600 outline-none" 
                                                    data-item-id="${item.id}"
                                                >
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div class="flex items-center justify-center gap-2">
                                <button type="button" class="qty-btn qty-minus flex h-9 w-9 items-center justify-center rounded-full border border-emerald-200 bg-white text-lg font-black text-emerald-600 hover:bg-emerald-50" data-item-id="${item.id}">
                                    −
                                </button>

                                <input 
                                    type="number"
                                    value="${item.quantity}"
                                    min="1"
                                    class="quantity-input h-10 w-14 rounded-xl border border-slate-200 bg-slate-50 text-center text-sm font-black text-slate-800 outline-none focus:border-emerald-400 focus:ring-4 focus:ring-emerald-100 [appearance:textfield]"
                                    data-item-id="${item.id}"
                                >

                                <button type="button" class="qty-btn qty-plus flex h-9 w-9 items-center justify-center rounded-full border border-emerald-200 bg-white text-lg font-black text-emerald-600 hover:bg-emerald-50" data-item-id="${item.id}">
                                    +
                                </button>
                            </div>

                            <div class="text-right">
                                <p class="text-sm font-black text-slate-900">
                                    S/ ${subtotal.toFixed(2)}
                                </p>
                            </div>

                            <button 
                                type="button" 
                                class="remove-item-btn flex h-10 w-10 items-center justify-center rounded-2xl bg-rose-50 text-rose-500 transition hover:bg-rose-100" 
                                data-item-id="${item.id}" 
                                title="Quitar producto"
                            >
                                <svg class="h-5 w-5 pointer-events-none" viewBox="0 0 20 20" fill="currentColor">
                                    <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
                                </svg>
                            </button>
                        </div>
                    `;
                }).join('')}
            </div>
        </div>
    `;

    updateTotalsUI(totals);
}

export function updateTotalsUI(totals) {
    document.getElementById('cart-subtotal').textContent = `S/ ${totals.subtotal.toFixed(2)}`;
    document.getElementById('cart-taxes').textContent = `S/ ${totals.impuestos.toFixed(2)}`;
    document.getElementById('cart-total').textContent = `S/ ${totals.total.toFixed(2)}`;
}

export function showAlert(alertModal, message, title = 'Aviso') {
    alertModal.querySelector('#alert-title').textContent = title;
    alertModal.querySelector('#alert-message').innerHTML = message.replace(/\n/g, '<br>');
    alertModal.querySelector('#alert-buttons').innerHTML = `<button id="alert-ok-btn" class="px-5 py-2 rounded-lg bg-emerald-500 hover:bg-emerald-600 text-white font-bold">Aceptar</button>`;
    alertModal.classList.remove('hidden');
    document.getElementById('alert-ok-btn').focus();
}

export function showConfirm(alertModal, message, title = 'Confirmación') {
    alertModal.querySelector('#alert-title').textContent = title;
    alertModal.querySelector('#alert-message').textContent = message;
    alertModal.querySelector('#alert-buttons').innerHTML = `
        <button id="confirm-cancel-btn" class="px-5 py-2 rounded-lg bg-slate-700 hover:bg-slate-600 text-white font-medium">Cancelar</button>
        <button id="confirm-ok-btn" class="px-5 py-2 rounded-lg bg-emerald-500 hover:bg-emerald-600 text-white font-bold">Sí, Registrar</button>
    `;
    alertModal.classList.remove('hidden');
    return new Promise((resolve) => {
        document.getElementById('confirm-ok-btn').onclick = () => { alertModal.classList.add('hidden'); resolve(true); };
        document.getElementById('confirm-cancel-btn').onclick = () => { alertModal.classList.add('hidden'); resolve(false); };
    });
}

export function showActionDialog(alertModal, message, title, venta) {
    alertModal.querySelector('#alert-title').textContent = title;
    alertModal.querySelector('#alert-message').innerHTML = message.replace(/\n/g, '<br>');
    const saleId = venta.id;
    const clienteNumero = venta.cliente_telefono || '';
    if (!saleId) {
        showAlert(alertModal, "Error crítico: El ID de la venta es indefinido.");
        return;
    }
    const pdfUrl = `${window.location.origin}/ventas/comprobante/${saleId}/pdf/`;
    const whatsappText = encodeURIComponent(`Hola, gracias por tu compra. Aquí tienes tu comprobante electrónico: ${pdfUrl}`);
    const whatsappUrl = `https://wa.me/${clienteNumero}?text=${whatsappText}`;
    alertModal.querySelector('#alert-buttons').innerHTML = `
        <div class="flex flex-col sm:flex-row justify-center gap-3 w-full">
            <button onclick="window.open('${pdfUrl}', '_blank')" class="w-full px-4 py-2 rounded-lg bg-sky-500 hover:bg-sky-600 text-white font-bold transition-colors">Imprimir</button>
            ${clienteNumero ? `<a href="${whatsappUrl}" target="_blank" class="w-full text-center px-4 py-2 rounded-lg bg-green-500 hover:bg-green-600 text-white font-bold transition-colors">Enviar WhatsApp</a>` : ''}
            <button id="alert-ok-btn" class="w-full px-4 py-2 rounded-lg bg-slate-700 hover:bg-slate-600 text-white font-medium transition-colors">Nueva Venta</button>
        </div>
    `;
    alertModal.classList.remove('hidden');
    document.getElementById('alert-ok-btn')?.focus();
}

export function abrirModalDePago(paymentModal, paymentTotalDisplay, montoRecibidoInput, vueltoDisplay, totalVentaFinal, cart) {
    if (cart.length === 0) {
        showAlert(document.getElementById('alert-modal'), 'El carrito está vacío.', 'Error');
        return;
    }
    paymentTotalDisplay.textContent = `S/ ${totalVentaFinal.toFixed(2)}`;
    montoRecibidoInput.value = totalVentaFinal.toFixed(2);
    montoRecibidoInput.dispatchEvent(new Event('input'));
    paymentModal.classList.remove('hidden');
    montoRecibidoInput.focus();
    montoRecibidoInput.select();
}