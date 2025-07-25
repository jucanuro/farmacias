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
        cartItemsContainer.innerHTML = '<p class="text-center text-slate-500 pt-16">Selecciona productos...</p>';
        updateTotalsUI(totals);
        return;
    }
    const headerHTML = `<div class="flex items-center gap-3 text-xs text-slate-400 font-bold uppercase pb-2 border-b border-slate-700"><div class="w-6"></div><div class="flex-grow">Producto</div><div class="w-20 text-center">Cant.</div><div class="w-24 text-right">Subtotal</div><div class="w-6"></div></div>`;
    cartItemsContainer.innerHTML = headerHTML;
    cart.forEach(item => {
        const subtotal = (item.quantity * item.precio_unitario) - (item.monto_descuento_linea || 0);
        const cartItemHTML = `<div class="border-b border-slate-800 py-3"><div class="flex items-center gap-3 text-sm"><div class="w-6 flex justify-center flex-shrink-0"><input type="checkbox" class="form-checkbox h-3.5 w-3.5 discount-checkbox" data-item-id="${item.id}" ${item.hasDiscount ? 'checked' : ''} title="Aplicar Descuento"></div><div class="flex-grow min-w-0"><p class="text-white truncate font-semibold" title="${item.nombre}">${item.nombre}</p><p class="text-xs text-slate-400">P. Unit: S/ ${parseFloat(item.precio_unitario).toFixed(2)}</p></div><div class="w-20 flex-shrink-0"><input type="number" value="${item.quantity}" min="1" class="w-full text-center form-input !py-1 quantity-input" data-item-id="${item.id}"></div><div class="w-24 text-right text-white font-mono flex-shrink-0">S/ ${subtotal.toFixed(2)}</div><div class="w-6 flex justify-center flex-shrink-0"><button class="text-rose-400 hover:text-rose-300 remove-item-btn" data-item-id="${item.id}" title="Quitar producto"><svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" /></svg></button></div></div><div class="pl-8 pt-2 flex items-center gap-2 ${item.hasDiscount ? '' : 'hidden'}"><label class="text-xs text-slate-400">Dcto:</label><div class="relative"><span class="absolute left-2 top-1/2 -translate-y-1/2 text-slate-500 text-xs">S/</span><input type="number" value="${item.monto_descuento_linea || '0.00'}" min="0" step="0.10" class="form-input !py-0.5 !pl-5 !text-xs w-20 discount-input" data-item-id="${item.id}"></div></div></div>`;
        cartItemsContainer.innerHTML += cartItemHTML;
    });
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