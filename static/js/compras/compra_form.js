document.addEventListener('DOMContentLoaded', () => {
    const tbody = document.getElementById('purchase-details-body');
    const template = document.getElementById('purchase-row-template');
    const addBtn = document.getElementById('add-row-btn');
    const form = document.getElementById('purchase-form');

    const subtotalDisplay = document.getElementById('subtotal-display');
    const impuestosDisplay = document.getElementById('impuestos-display');
    const totalDisplay = document.getElementById('total-display');

    const productos = JSON.parse(document.getElementById('productos-data')?.textContent || '[]');

    if (!tbody || !template || !form) return;

    const money = (value) => `S/ ${Number(value || 0).toFixed(2)}`;

    const normalize = (value) =>
        String(value || '')
            .toLowerCase()
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '')
            .trim();

    const productLabel = (producto) => {
        if (!producto) return '';
        return `${producto.nombre || ''}${producto.concentracion ? ' - ' + producto.concentracion : ''}`.trim();
    };

    function updateTotals() {
        let subtotal = 0;

        tbody.querySelectorAll('.purchase-row').forEach(row => {
            const cantidad = Number(row.querySelector('[name="cantidad_recibida"]')?.value || 0);
            const precio = Number(row.querySelector('[name="precio_unitario_compra"]')?.value || 0);
            const lineSubtotal = cantidad * precio;

            subtotal += lineSubtotal;

            const lineSubtotalEl = row.querySelector('.line-subtotal');
            if (lineSubtotalEl) lineSubtotalEl.textContent = money(lineSubtotal);
        });

        const impuestos = subtotal * 0.18;
        const total = subtotal + impuestos;

        if (subtotalDisplay) subtotalDisplay.textContent = money(subtotal);
        if (impuestosDisplay) impuestosDisplay.textContent = money(impuestos);
        if (totalDisplay) totalDisplay.textContent = money(total);
    }

    function setDefaultPresentation(row) {
        const select = row.querySelector('.presentation-select');
        if (!select) return;

        const cajaOption = [...select.options].find(opt =>
            normalize(opt.textContent) === 'caja'
        );

        if (cajaOption) {
            select.value = cajaOption.value;
            return;
        }

        const unidadOption = [...select.options].find(opt =>
            normalize(opt.textContent) === 'unidad'
        );

        if (unidadOption) {
            select.value = unidadOption.value;
        }
    }

    function fillProductDefaults(row, producto) {
        row.querySelector('.product-id-input').value = producto.id;
        row.querySelector('.product-search-input').value = productLabel(producto);

        const loteInput = row.querySelector('[name="lote"]');
        const fechaInput = row.querySelector('[name="fecha_vencimiento"]');
        const precioInput = row.querySelector('[name="precio_unitario_compra"]');
        const cantidadInput = row.querySelector('[name="cantidad_recibida"]');

        if (loteInput) loteInput.value = producto.lote || '';
        if (fechaInput) fechaInput.value = producto.fecha_vencimiento || '';
        if (precioInput) precioInput.value = '';

        if (cantidadInput && !cantidadInput.value) {
            cantidadInput.value = '1';
        }

        setDefaultPresentation(row);

        const suggestions = row.querySelector('.product-suggestions');
        if (suggestions) suggestions.classList.add('hidden');

        updateTotals();

        cantidadInput?.focus();
        cantidadInput?.select();
    }

    function renderSuggestions(row, results) {
        const suggestions = row.querySelector('.product-suggestions');
        if (!suggestions) return;

        suggestions.innerHTML = '';

        if (!results.length) {
            suggestions.innerHTML = `
                <div class="px-4 py-3 text-sm font-bold text-slate-400">
                    Sin resultados
                </div>
            `;
            suggestions.classList.remove('hidden');
            return;
        }

        results.forEach(producto => {
            const button = document.createElement('button');
            button.type = 'button';
            button.className = 'block w-full px-4 py-3 text-left transition-colors hover:bg-emerald-50';
            button.innerHTML = `
                <p class="text-sm font-black text-slate-900">${productLabel(producto)}</p>
                <p class="text-xs font-semibold text-slate-400">
                    ${producto.laboratorio || 'Sin laboratorio'}
                    ${producto.precio ? ' · S/ ' + Number(producto.precio || 0).toFixed(2) : ''}
                </p>
            `;

            button.addEventListener('click', () => fillProductDefaults(row, producto));
            suggestions.appendChild(button);
        });

        suggestions.classList.remove('hidden');
    }

    function searchProducts(term) {
        const q = normalize(term);

        if (q.length < 2) return [];

        return productos
            .filter(producto => {
                const haystack = normalize([
                    producto.nombre,
                    producto.concentracion,
                    producto.laboratorio,
                    producto.lote
                ].join(' '));

                return haystack.includes(q);
            })
            .slice(0, 12);
    }

    function bindProductSearch(row) {
        const input = row.querySelector('.product-search-input');
        const hidden = row.querySelector('.product-id-input');
        const suggestions = row.querySelector('.product-suggestions');

        if (!input || !hidden || !suggestions) return;

        input.addEventListener('input', () => {
            hidden.value = '';

            const results = searchProducts(input.value);

            if (!results.length && normalize(input.value).length < 2) {
                suggestions.classList.add('hidden');
                suggestions.innerHTML = '';
                return;
            }

            renderSuggestions(row, results);
        });

        input.addEventListener('focus', () => {
            if (normalize(input.value).length >= 2) {
                renderSuggestions(row, searchProducts(input.value));
            }
        });

        input.addEventListener('keydown', (event) => {
            if (event.key !== 'Enter') return;

            const firstSuggestion = suggestions.querySelector('button');
            if (firstSuggestion && !suggestions.classList.contains('hidden')) {
                event.preventDefault();
                firstSuggestion.click();
            }
        });
    }

    function bindRow(row) {
        row.querySelectorAll('.calc-field').forEach(input => {
            input.addEventListener('input', updateTotals);
        });

        row.querySelector('.remove-row-btn')?.addEventListener('click', () => {
            row.remove();
            updateTotals();
        });

        bindProductSearch(row);
        setDefaultPresentation(row, null);
    }

    function addRow() {
        const clone = template.content.cloneNode(true);
        const row = clone.querySelector('.purchase-row');

        tbody.appendChild(clone);
        bindRow(row);
        updateTotals();

        row.querySelector('.product-search-input')?.focus();
    }

    addBtn?.addEventListener('click', addRow);

    tbody.querySelectorAll('.purchase-row').forEach(bindRow);

    if (!tbody.querySelector('.purchase-row')) {
        addRow();
    }

    document.addEventListener('click', (event) => {
        document.querySelectorAll('.product-suggestions').forEach(box => {
            if (!box.closest('.product-search-wrapper')?.contains(event.target)) {
                box.classList.add('hidden');
            }
        });
    });

    form.addEventListener('submit', (event) => {
        const rows = [...tbody.querySelectorAll('.purchase-row')];

        const validRows = rows.filter(row => row.querySelector('.product-id-input')?.value);

        if (!validRows.length) {
            event.preventDefault();
            alert('Agrega al menos un producto válido.');
            return;
        }

        const invalidProduct = rows.some(row => {
            const searchInput = row.querySelector('.product-search-input');
            const hiddenInput = row.querySelector('.product-id-input');

            return searchInput?.value.trim() && !hiddenInput?.value;
        });

        if (invalidProduct) {
            event.preventDefault();
            alert('Hay productos escritos pero no seleccionados. Selecciona el producto desde la lista de sugerencias.');
            return;
        }
    });

    updateTotals();
});