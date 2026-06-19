function money(value) {
    const number = Number(value || 0);
    return Number.isFinite(number) ? number.toFixed(2) : '0.00';
}

function numberValue(value) {
    const number = Number(value || 0);
    return Number.isFinite(number) ? number : 0;
}

function escapeHtml(value) {
    return String(value ?? '')
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#039;');
}

function getStock(producto) {
    return numberValue(
        producto.stock_total ??
        producto.stock_disponible ??
        producto.cantidad_disponible ??
        0
    );
}

function getPrecio(producto) {
    return numberValue(
        producto.precio_venta ??
        producto.precio ??
        producto.precio_unitario ??
        0
    );
}

function getInitial(nombre) {
    return escapeHtml(nombre || 'P').charAt(0).toUpperCase();
}

export function renderProductGrid(productGrid, productos) {
    productGrid.innerHTML = '';

    const items = Array.isArray(productos) ? productos : [];

    if (!items.length) {
        productGrid.innerHTML = `
            <div class="col-span-full flex min-h-[360px] flex-col items-center justify-center rounded-[2rem] border border-dashed border-slate-200 bg-white p-8 text-center">
                <div class="flex h-16 w-16 items-center justify-center rounded-3xl bg-slate-50 text-slate-400">
                    <svg class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8">
                        <path d="M21 21l-4.35-4.35m1.85-5.15a7 7 0 11-14 0 7 7 0 0114 0z" />
                    </svg>
                </div>
                <h3 class="mt-5 text-sm font-black uppercase tracking-[0.18em] text-slate-400">Sin resultados</h3>
                <p class="mt-2 max-w-xs text-sm text-slate-400">No encontramos productos disponibles para esta búsqueda.</p>
            </div>
        `;
        return;
    }

    items.forEach(producto => {
        const stock = getStock(producto);
        const precio = getPrecio(producto);
        const sinStock = stock <= 0;
        const sinPrecio = precio <= 0;
        const disabled = sinStock || sinPrecio;

        const card = document.createElement('button');
        card.type = 'button';
        card.disabled = disabled;
        card.dataset.productoJson = JSON.stringify(producto);
        card.className = `
            add-to-cart-btn group relative overflow-hidden rounded-[1.6rem] border bg-white p-4 text-left shadow-sm transition-all duration-200
            ${disabled
                ? 'cursor-not-allowed border-slate-200 opacity-60'
                : 'border-slate-200 hover:-translate-y-0.5 hover:border-emerald-200 hover:shadow-[0_18px_45px_rgba(15,23,42,0.08)]'
            }
        `;

        const imageUrl = producto.imagen_producto || '';
        const nombre = escapeHtml(producto.nombre || 'Producto sin nombre');
        const laboratorio = escapeHtml(producto.laboratorio_nombre || 'Sin laboratorio');
        const categoria = escapeHtml(producto.categoria_nombre || '');
        const unidad = escapeHtml(producto.unidad_venta || 'UNIDAD');

        card.innerHTML = `
            <div class="absolute right-0 top-0 h-24 w-24 rounded-bl-[3rem] bg-emerald-50 transition group-hover:bg-emerald-100"></div>

            <div class="relative flex gap-4">
                <div class="flex h-20 w-20 shrink-0 items-center justify-center overflow-hidden rounded-3xl border border-slate-100 bg-slate-50">
                    ${imageUrl
                        ? `<img src="${escapeHtml(imageUrl)}" alt="${nombre}" class="h-full w-full object-cover">`
                        : `<span class="text-2xl font-black text-slate-300">${getInitial(nombre)}</span>`
                    }
                </div>

                <div class="min-w-0 flex-1">
                    <div class="flex items-start justify-between gap-3">
                        <div class="min-w-0">
                            <p class="line-clamp-2 text-sm font-black leading-5 text-slate-900" title="${nombre}">
                                ${nombre}
                            </p>
                            <p class="mt-1 truncate text-xs font-bold text-slate-400">
                                ${laboratorio}
                            </p>
                        </div>

                        <span class="shrink-0 rounded-full ${sinStock ? 'bg-rose-50 text-rose-600' : 'bg-emerald-50 text-emerald-700'} px-2.5 py-1 text-[10px] font-black uppercase tracking-widest">
                            ${sinStock ? 'Sin stock' : `${stock} disp.`}
                        </span>
                    </div>

                    <div class="mt-3 flex flex-wrap items-center gap-2">
                        ${categoria ? `
                            <span class="rounded-full bg-slate-100 px-2.5 py-1 text-[10px] font-black uppercase tracking-widest text-slate-500">
                                ${categoria}
                            </span>
                        ` : ''}

                        <span class="rounded-full bg-sky-50 px-2.5 py-1 text-[10px] font-black uppercase tracking-widest text-sky-700">
                            ${unidad}
                        </span>
                    </div>

                    <div class="mt-4 flex items-end justify-between gap-3">
                        <div>
                            <p class="text-[10px] font-black uppercase tracking-[0.16em] text-slate-400">
                                Precio sucursal
                            </p>
                            <p class="text-xl font-black text-emerald-600">
                                S/ ${money(precio)}
                            </p>
                        </div>

                        <span class="inline-flex h-10 w-10 items-center justify-center rounded-2xl ${disabled ? 'bg-slate-100 text-slate-300' : 'bg-slate-900 text-emerald-300 group-hover:bg-emerald-600 group-hover:text-white'} transition">
                            +
                        </span>
                    </div>
                </div>
            </div>
        `;

        productGrid.appendChild(card);
    });
}

export function renderCart(cartItemsContainer, cart, totals) {
    cartItemsContainer.innerHTML = '';

    const items = Array.isArray(cart) ? cart : [];

    if (!items.length) {
        cartItemsContainer.innerHTML = `
            <div class="flex min-h-[320px] flex-col items-center justify-center rounded-[2rem] border border-dashed border-slate-200 bg-white p-8 text-center">
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
        <div class="space-y-3">
            ${items.map(item => {
                const nombre = escapeHtml(item.nombre || 'Producto');
                const precio = numberValue(item.precio_unitario);
                const quantity = numberValue(item.quantity || 1);
                const descuento = numberValue(item.monto_descuento_linea || 0);
                const stock = numberValue(item.stock_disponible || item.stock_total || item.cantidad_disponible || 0);
                const subtotal = (quantity * precio) - descuento;

                return `
                    <article data-item-id="${item.id}" class="rounded-[1.4rem] border border-slate-200 bg-white p-4 shadow-sm transition hover:border-emerald-200 hover:shadow-md">
                        <div class="flex items-start justify-between gap-3">
                            <div class="min-w-0">
                                <p class="line-clamp-2 text-sm font-black leading-5 text-slate-900">
                                    ${nombre}
                                </p>
                                <div class="mt-2 flex flex-wrap items-center gap-2">
                                    <span class="rounded-full bg-slate-100 px-2.5 py-1 text-[10px] font-black text-slate-500">
                                        S/ ${money(precio)} c/u
                                    </span>
                                    <span class="rounded-full bg-emerald-50 px-2.5 py-1 text-[10px] font-black text-emerald-700">
                                        Stock ${stock}
                                    </span>
                                </div>
                            </div>

                            <button type="button" class="remove-item-btn flex h-9 w-9 shrink-0 items-center justify-center rounded-2xl bg-rose-50 text-rose-500 transition hover:bg-rose-100" title="Quitar producto">
                                ×
                            </button>
                        </div>

                        <div class="mt-4 grid grid-cols-[1fr_auto] items-center gap-3">
                            <div class="flex items-center gap-2">
                                <button type="button" class="qty-btn qty-minus flex h-9 w-9 items-center justify-center rounded-2xl border border-emerald-200 bg-white text-lg font-black text-emerald-600 hover:bg-emerald-50">
                                    −
                                </button>

                                <input
                                    type="number"
                                    value="${quantity}"
                                    min="1"
                                    max="${stock || ''}"
                                    class="quantity-input h-10 w-16 rounded-2xl border border-slate-200 bg-slate-50 text-center text-sm font-black text-slate-800 outline-none focus:border-emerald-400 focus:ring-4 focus:ring-emerald-100"
                                    data-item-id="${item.id}"
                                >

                                <button type="button" class="qty-btn qty-plus flex h-9 w-9 items-center justify-center rounded-2xl border border-emerald-200 bg-white text-lg font-black text-emerald-600 hover:bg-emerald-50">
                                    +
                                </button>
                            </div>

                            <div class="text-right">
                                <p class="text-[10px] font-black uppercase tracking-widest text-slate-400">Subtotal</p>
                                <p class="text-base font-black text-slate-900">S/ ${money(subtotal)}</p>
                            </div>
                        </div>

                        <div class="mt-3 rounded-2xl border border-slate-100 bg-slate-50 p-3">
                            <label class="flex items-center justify-between gap-3">
                                <span class="text-xs font-black uppercase tracking-widest text-slate-500">Aplicar descuento</span>
                                <input
                                    type="checkbox"
                                    class="discount-checkbox h-4 w-4 rounded border-slate-300 text-emerald-600 focus:ring-emerald-500"
                                    data-item-id="${item.id}"
                                    ${item.hasDiscount ? 'checked' : ''}
                                >
                            </label>

                            <div class="mt-3 ${item.hasDiscount ? '' : 'hidden'}">
                                <div class="flex items-center rounded-2xl border border-rose-100 bg-white px-3 py-2">
                                    <span class="text-xs font-black text-rose-400">S/</span>
                                    <input
                                        type="number"
                                        value="${descuento}"
                                        min="0"
                                        step="0.10"
                                        class="discount-input ml-2 w-full bg-transparent text-sm font-black text-rose-600 outline-none"
                                        data-item-id="${item.id}"
                                    >
                                </div>
                            </div>
                        </div>
                    </article>
                `;
            }).join('')}
        </div>
    `;

    updateTotalsUI(totals);
}

export function updateTotalsUI(totals) {
    document.getElementById('cart-subtotal').textContent = `S/ ${money(totals.subtotal)}`;
    document.getElementById('cart-taxes').textContent = `S/ ${money(totals.impuestos)}`;
    document.getElementById('cart-total').textContent = `S/ ${money(totals.total)}`;
}

export function showAlert(alertModal, message, title = 'Aviso') {
    alertModal.querySelector('#alert-title').textContent = title;
    alertModal.querySelector('#alert-message').innerHTML = String(message || '').replace(/\n/g, '<br>');
    alertModal.querySelector('#alert-buttons').innerHTML = `
        <button id="alert-ok-btn" class="rounded-2xl bg-emerald-500 px-5 py-3 text-sm font-black text-white transition hover:bg-emerald-600">
            Aceptar
        </button>
    `;
    alertModal.classList.remove('hidden');
    document.getElementById('alert-ok-btn')?.focus();
}

export function showConfirm(alertModal, message, title = 'Confirmación') {
    alertModal.querySelector('#alert-title').textContent = title;
    alertModal.querySelector('#alert-message').textContent = message;
    alertModal.querySelector('#alert-buttons').innerHTML = `
        <button id="confirm-cancel-btn" class="rounded-2xl border border-slate-200 bg-white px-5 py-3 text-sm font-black text-slate-600 hover:bg-slate-50">
            Cancelar
        </button>
        <button id="confirm-ok-btn" class="rounded-2xl bg-emerald-500 px-5 py-3 text-sm font-black text-white hover:bg-emerald-600">
            Sí, registrar
        </button>
    `;
    alertModal.classList.remove('hidden');

    return new Promise((resolve) => {
        document.getElementById('confirm-ok-btn').onclick = () => {
            alertModal.classList.add('hidden');
            resolve(true);
        };

        document.getElementById('confirm-cancel-btn').onclick = () => {
            alertModal.classList.add('hidden');
            resolve(false);
        };
    });
}

export function showActionDialog(alertModal, message, title, venta) {
    const saleId = venta?.id;
    const clienteNumero = venta?.cliente_telefono || '';

    if (!saleId) {
        showAlert(alertModal, 'Error crítico: El ID de la venta es indefinido.');
        return;
    }

    const pdfUrl = `${window.location.origin}/ventas/comprobante/${saleId}/pdf/`;
    const whatsappText = encodeURIComponent(`Hola, gracias por tu compra. Aquí tienes tu comprobante: ${pdfUrl}`);
    const whatsappUrl = `https://wa.me/${clienteNumero}?text=${whatsappText}`;

    alertModal.querySelector('#alert-title').textContent = title;
    alertModal.querySelector('#alert-message').innerHTML = `
        <div class="space-y-3 text-center">
            <div class="mx-auto flex h-16 w-16 items-center justify-center rounded-3xl bg-emerald-50 text-emerald-600">
                ✓
            </div>
            <p class="text-sm font-bold text-slate-500">${escapeHtml(message)}</p>
            <p class="text-2xl font-black text-slate-900">Venta #${saleId}</p>
        </div>
    `;

    alertModal.querySelector('#alert-buttons').innerHTML = `
        <div class="grid w-full grid-cols-1 gap-2 sm:grid-cols-3">
            <button onclick="window.open('${pdfUrl}', '_blank')" class="rounded-2xl bg-sky-500 px-4 py-3 text-sm font-black text-white transition hover:bg-sky-600">
                Imprimir
            </button>
            ${clienteNumero ? `
                <a href="${whatsappUrl}" target="_blank" class="rounded-2xl bg-green-500 px-4 py-3 text-center text-sm font-black text-white transition hover:bg-green-600">
                    WhatsApp
                </a>
            ` : ''}
            <button id="alert-ok-btn" class="rounded-2xl bg-slate-900 px-4 py-3 text-sm font-black text-white transition hover:bg-emerald-600">
                Nueva venta
            </button>
        </div>
    `;

    alertModal.classList.remove('hidden');
    document.getElementById('alert-ok-btn')?.focus();
}

export function abrirModalDePago(paymentModal, paymentTotalDisplay, montoRecibidoInput, vueltoDisplay, totalVentaFinal, cart) {
    if (!Array.isArray(cart) || !cart.length) {
        showAlert(document.getElementById('alert-modal'), 'El carrito está vacío.', 'Error');
        return;
    }

    paymentTotalDisplay.textContent = `S/ ${money(totalVentaFinal)}`;
    montoRecibidoInput.value = money(totalVentaFinal);
    montoRecibidoInput.dispatchEvent(new Event('input'));
    paymentModal.classList.remove('hidden');

    setTimeout(() => {
        montoRecibidoInput.focus();
        montoRecibidoInput.select();
    }, 100);
}