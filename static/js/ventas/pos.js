import * as API from './pos/api.js';
import * as Cart from './pos/cart.js';
import * as UI from './pos/ui.js';
import * as Customer from './pos/customer.js';
import * as Caja from './pos/caja.js';

document.addEventListener('DOMContentLoaded', () => {
    const state = {
        tipoComprobante: 'TICKET',
        selectedCustomer: null,
        paymentMethod: 'EFECTIVO',
        ventaEnProceso: false,
        scannerActivo: false,
        scannerStream: null,
        scannerDetector: null,
        scannerLoopId: null,
        ultimoCodigoEscaneado: '',
        ultimoEscaneoTime: 0,
    };

    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';

    const dom = {
        searchInput: document.getElementById('product-search-input'),
        productGrid: document.getElementById('product-grid'),
        cartItemsContainer: document.getElementById('cart-items'),
        comprobanteSelector: document.getElementById('comprobante-selector'),

        customerSearchInput: document.getElementById('customer-search-input'),
        customerSuggestions: document.getElementById('customer-suggestions'),
        customerDisplay: document.getElementById('customer-display'),
        customerNameSpan: document.getElementById('customer-name'),
        clearCustomerBtn: document.getElementById('clear-customer-btn'),

        newCustomerModal: document.getElementById('new-customer-modal'),
        newCustomerForm: document.getElementById('new-customer-form'),
        cancelModalBtn: document.getElementById('modal-cancel-btn'),

        alertModal: document.getElementById('alert-modal'),

        proceedToPaymentBtn: document.getElementById('proceed-to-payment-btn'),
        paymentModal: document.getElementById('payment-modal'),
        paymentForm: document.getElementById('payment-form'),
        paymentModalCloseBtn: document.getElementById('payment-modal-close-btn'),
        paymentTotalDisplay: document.getElementById('payment-total-display'),
        paymentMethodSelector: document.getElementById('payment-method-selector'),
        efectivoDetails: document.getElementById('efectivo-details'),
        yapeDetails: document.getElementById('yape-details'),
        montoRecibidoInput: document.getElementById('monto-recibido'),
        vueltoDisplay: document.getElementById('vuelto-display'),
        confirmPaymentBtn: document.getElementById('confirm-payment-btn'),

        posContainer: document.getElementById('pos-main-container'),

        aperturaCajaModal: document.getElementById('apertura-caja-modal'),
        aperturaCajaForm: document.getElementById('apertura-caja-form'),
        montoInicialInput: document.getElementById('monto-inicial'),
        confirmAperturaBtn: document.getElementById('confirm-apertura-btn'),

        cierreCajaModal: document.getElementById('cierre-caja-modal'),
        cierreCajaForm: document.getElementById('cierre-caja-form'),
        cierreModalCloseBtn: document.getElementById('cierre-modal-close-btn'),
        showCierreModalBtn: document.getElementById('show-cierre-modal-btn'),
        confirmCierreBtn: document.getElementById('confirm-cierre-btn'),

        mobileProductSearchInput: document.getElementById('mobile-product-search-input'),
        mobileProductGrid: document.getElementById('mobile-product-grid'),
        mobileCartItems: document.getElementById('mobile-cart-items'),
        mobileCartTotal: document.getElementById('mobile-cart-total'),
        mobilePayBtn: document.getElementById('mobile-pay-btn'),

        toggleScannerBtn: document.getElementById('toggle-scanner-btn'),
        scannerCameraBox: document.getElementById('scanner-camera-box'),
        barcodeVideo: document.getElementById('barcode-video'),
        scannerStatus: document.getElementById('scanner-status'),
        barcodeManualInput: document.getElementById('barcode-manual-input'),
        barcodeSearchBtn: document.getElementById('barcode-search-btn'),
    };

    function debounce(fn, delay = 300) {
        let timeout;
        return (...args) => {
            clearTimeout(timeout);
            timeout = setTimeout(() => fn(...args), delay);
        };
    }

    function getErrorMessage(error, fallback = 'Ocurrió un error.') {
        if (error instanceof Error && error.message) return error.message;
        if (error?.error) return error.error;
        if (error?.detail) return error.detail;
        if (error?.non_field_errors) return error.non_field_errors.join('\n');

        if (error && typeof error === 'object') {
            return Object.entries(error)
                .map(([field, value]) => `• ${field}: ${JSON.stringify(value)}`)
                .join('\n');
        }

        return fallback;
    }

    function numberValue(value) {
        const number = Number(value || 0);
        return Number.isFinite(number) ? number : 0;
    }

    function money(value) {
        return numberValue(value).toFixed(2);
    }

    function getStockDisponible(item) {
        return numberValue(
            item.stock_disponible ??
            item.stock_total ??
            item.cantidad_disponible ??
            0
        );
    }

    function renderProductInitial(target = dom.productGrid) {
        if (!target) return;

        target.innerHTML = `
            <div class="col-span-full flex min-h-[320px] flex-col items-center justify-center rounded-[2rem] border border-dashed border-slate-200 bg-white p-8 text-center">
                <div class="flex h-16 w-16 items-center justify-center rounded-3xl bg-emerald-50 text-emerald-500">
                    <svg class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8">
                        <path d="M21 21l-4.35-4.35m1.85-5.15a7 7 0 11-14 0 7 7 0 0114 0z" />
                    </svg>
                </div>
                <h3 class="mt-5 text-sm font-black uppercase tracking-[0.18em] text-slate-400">
                    Busca productos
                </h3>
                <p class="mt-2 max-w-xs text-sm text-slate-400">
                    Escribe nombre, código de barras, SKU o laboratorio.
                </p>
            </div>
        `;
    }

    function renderProductLoading(target = dom.productGrid, label = 'Buscando productos') {
        if (!target) return;

        target.innerHTML = `
            <div class="col-span-full flex min-h-[260px] flex-col items-center justify-center rounded-[2rem] border border-slate-200 bg-white p-8 text-center">
                <div class="h-10 w-10 animate-spin rounded-full border-4 border-slate-200 border-t-emerald-500"></div>
                <p class="mt-4 text-sm font-black uppercase tracking-[0.18em] text-slate-400">
                    ${label}
                </p>
            </div>
        `;
    }

    function renderProductError(target, message) {
        if (!target) return;

        target.innerHTML = `
            <div class="col-span-full flex min-h-[260px] flex-col items-center justify-center rounded-[2rem] border border-rose-200 bg-rose-50 p-8 text-center">
                <p class="text-sm font-black text-rose-600">${message}</p>
            </div>
        `;
    }

    function updateFullUI() {
        const cart = Cart.getCart();
        const totals = Cart.getCartTotals(state.tipoComprobante);

        if (dom.cartItemsContainer) {
            UI.renderCart(dom.cartItemsContainer, cart, totals);
        }

        if (dom.mobileCartItems) {
            UI.renderCart(dom.mobileCartItems, cart, totals);
        }

        if (dom.mobileCartTotal) {
            dom.mobileCartTotal.textContent = `S/ ${money(totals.total)}`;
        }

        UI.updateTotalsUI(totals);
    }

    async function buscarProductos(term, target = dom.productGrid) {
        const query = String(term || '').trim();

        if (query.length < 2) {
            renderProductInitial(target);
            return;
        }

        try {
            renderProductLoading(target);
            const data = await API.buscarProductosAPI(query);
            UI.renderProductGrid(target, data.results || data || []);
        } catch (error) {
            renderProductError(target, getErrorMessage(error, 'No se pudieron cargar productos.'));
        }
    }

    async function buscarPorCodigoBarra(code) {
        const codigo = String(code || '').trim();

        if (!codigo) {
            UI.showAlert(dom.alertModal, 'Ingresa o escanea un código válido.', 'Código vacío');
            return;
        }

        try {
            if (dom.scannerStatus) {
                dom.scannerStatus.textContent = `Buscando código ${codigo}...`;
            }

            const data = await API.buscarProductosAPI(codigo);
            const productos = data.results || data || [];

            if (!productos.length) {
                if (dom.scannerStatus) {
                    dom.scannerStatus.textContent = 'Producto no encontrado.';
                }

                UI.showAlert(
                    dom.alertModal,
                    `No se encontró ningún producto con el código ${codigo}.`,
                    'Producto no encontrado'
                );
                return;
            }

            const producto = productos[0];

            const agregado = Cart.addToCart(producto, (msg, title) => {
                UI.showAlert(dom.alertModal, msg, title);
            });

            if (agregado) {
                updateFullUI();

                if (dom.scannerStatus) {
                    dom.scannerStatus.textContent = `Agregado: ${producto.nombre}`;
                }

                if (dom.barcodeManualInput) {
                    dom.barcodeManualInput.value = '';
                }
            }
        } catch (error) {
            UI.showAlert(
                dom.alertModal,
                getErrorMessage(error, 'No se pudo buscar el código.'),
                'Error de escaneo'
            );
        }
    }

    const buscarProductosDebounced = debounce((value) => {
        buscarProductos(value, dom.productGrid);
    }, 300);

    const buscarProductosMobileDebounced = debounce((value) => {
        buscarProductos(value, dom.mobileProductGrid);
    }, 300);

    const buscarClientesDebounced = debounce((value) => {
        Customer.buscarCliente(value, dom, state);
    }, 300);

    function validarCarritoAntesDePago() {
        const cart = Cart.getCart();

        if (!cart.length) {
            UI.showAlert(dom.alertModal, 'El carrito está vacío.', 'Venta vacía');
            return false;
        }

        for (const item of cart) {
            const cantidad = numberValue(item.quantity);
            const stockDisponible = getStockDisponible(item);

            if (cantidad <= 0) {
                UI.showAlert(dom.alertModal, `Cantidad inválida para ${item.nombre}.`, 'Cantidad inválida');
                return false;
            }

            if (stockDisponible > 0 && cantidad > stockDisponible) {
                UI.showAlert(
                    dom.alertModal,
                    `Stock insuficiente para ${item.nombre}. Disponible: ${stockDisponible}, requerido: ${cantidad}.`,
                    'Stock insuficiente'
                );
                return false;
            }
        }

        return true;
    }

    async function handleFinalizarVenta(e) {
        e.preventDefault();

        if (state.ventaEnProceso) return;
        if (!validarCarritoAntesDePago()) return;

        state.ventaEnProceso = true;
        dom.confirmPaymentBtn.disabled = true;
        dom.confirmPaymentBtn.textContent = 'Procesando...';

        try {
            const cart = Cart.getCart();
            const totals = Cart.getCartTotals(state.tipoComprobante);

            const montoRecibido = state.paymentMethod === 'EFECTIVO'
                ? numberValue(dom.montoRecibidoInput.value)
                : totals.total;

            if (state.paymentMethod === 'EFECTIVO' && montoRecibido < totals.total) {
                throw new Error('El monto recibido no puede ser menor al total de la venta.');
            }

            const detalles = cart.map(item => ({
                producto: item.id,
                cantidad: numberValue(item.quantity),
                precio_unitario: numberValue(item.precio_unitario),
                monto_descuento_linea: numberValue(item.monto_descuento_linea),
                unidad_venta: item.unidad_venta || 'UNIDAD',
            }));

            const ventaData = {
                cliente: state.selectedCustomer ? state.selectedCustomer.id : null,
                tipo_comprobante: state.tipoComprobante,
                metodo_pago: state.paymentMethod,
                monto_recibido: montoRecibido,
                vuelto: state.paymentMethod === 'EFECTIVO'
                    ? Math.max(montoRecibido - totals.total, 0)
                    : 0,
                detalles,
            };

            const nuevaVenta = await API.finalizarVentaAPI(ventaData, csrftoken);

            if (state.tipoComprobante === 'BOLETA' || state.tipoComprobante === 'FACTURA') {
                try {
                    const comprobante = await API.crearComprobanteElectronicoAPI({
                        venta_id: nuevaVenta.id,
                        tipo_comprobante: state.tipoComprobante,
                        ambiente: 'BETA',
                    }, csrftoken);

                    nuevaVenta.comprobante_electronico = comprobante.comprobante;
                } catch (feError) {
                    nuevaVenta.error_facturacion = getErrorMessage(
                        feError,
                        'La venta se registró, pero no se pudo crear el comprobante electrónico.'
                    );
                }
            }

            resetPOS();

            UI.showActionDialog(
                dom.alertModal,
                `Venta #${nuevaVenta.id} registrada correctamente.`,
                '¡Venta completada!',
                nuevaVenta
            );

        } catch (error) {
            UI.showAlert(
                dom.alertModal,
                getErrorMessage(error, 'No se pudo registrar la venta.'),
                'Error de registro'
            );

        } finally {
            state.ventaEnProceso = false;
            dom.confirmPaymentBtn.disabled = false;
            dom.confirmPaymentBtn.textContent = 'Confirmar venta';
        }
    }

    function resetPOS() {
        Cart.clearCart();
        Customer.limpiarCliente(state, dom);

        if (dom.paymentModal) dom.paymentModal.classList.add('hidden');
        if (dom.searchInput) dom.searchInput.value = '';
        if (dom.mobileProductSearchInput) dom.mobileProductSearchInput.value = '';
        if (dom.barcodeManualInput) dom.barcodeManualInput.value = '';

        renderProductInitial(dom.productGrid);
        renderProductInitial(dom.mobileProductGrid);
        updateFullUI();
    }

    function handleProductClick(e) {
        const card = e.target.closest('.add-to-cart-btn');

        if (!card || card.disabled) return;

        try {
            const productoJson = card.dataset.productoJson;

            if (!productoJson) {
                throw new Error('No se encontraron datos del producto.');
            }

            const producto = JSON.parse(productoJson);

            const agregado = Cart.addToCart(producto, (msg, title) => {
                UI.showAlert(dom.alertModal, msg, title);
            });

            if (agregado) {
                updateFullUI();
            }

        } catch (error) {
            UI.showAlert(
                dom.alertModal,
                getErrorMessage(error, 'No se pudo agregar el producto.'),
                'Error'
            );
        }
    }

    function handleCartClick(e) {
        const target = e.target;
        const itemElement = target.closest('[data-item-id]');

        if (!itemElement) return;

        const itemId = Number(itemElement.dataset.itemId);
        const currentItem = Cart.getCart().find(item => Number(item.id) === itemId);

        if (!currentItem) return;

        if (target.closest('.qty-minus')) {
            const currentQty = numberValue(currentItem.quantity);

            if (currentQty > 1) {
                Cart.updateCartItem(itemId, 'quantity', currentQty - 1);
                updateFullUI();
            }

            return;
        }

        if (target.closest('.qty-plus')) {
            const currentQty = numberValue(currentItem.quantity);
            const stockDisponible = getStockDisponible(currentItem);

            if (stockDisponible > 0 && currentQty + 1 > stockDisponible) {
                UI.showAlert(
                    dom.alertModal,
                    `Solo quedan ${stockDisponible} unidades disponibles de ${currentItem.nombre}.`,
                    'Stock insuficiente'
                );
                return;
            }

            Cart.updateCartItem(itemId, 'quantity', currentQty + 1);
            updateFullUI();
            return;
        }

        if (target.closest('.remove-item-btn')) {
            Cart.removeFromCart(itemId);
            updateFullUI();
            return;
        }

        if (target.classList.contains('discount-checkbox')) {
            Cart.updateCartItem(itemId, 'hasDiscount', target.checked);
            updateFullUI();
        }
    }

    function handleCartInput(e) {
        const target = e.target;
        const itemElement = target.closest('[data-item-id]');

        if (!itemElement) return;

        const itemId = Number(itemElement.dataset.itemId);
        const currentItem = Cart.getCart().find(item => Number(item.id) === itemId);

        if (!currentItem) return;

        if (target.classList.contains('quantity-input')) {
            const stockDisponible = getStockDisponible(currentItem);
            let cantidad = numberValue(target.value);

            if (cantidad < 1) cantidad = 1;

            if (stockDisponible > 0 && cantidad > stockDisponible) {
                cantidad = stockDisponible;

                UI.showAlert(
                    dom.alertModal,
                    `Solo quedan ${stockDisponible} unidades disponibles de ${currentItem.nombre}.`,
                    'Stock insuficiente'
                );
            }

            Cart.updateCartItem(itemId, 'quantity', cantidad);
            updateFullUI();
            return;
        }

        if (target.classList.contains('discount-input')) {
            Cart.updateCartItem(itemId, 'monto_descuento_linea', target.value);
            updateFullUI();
        }
    }

    function handleComprobanteClick(e) {
        const button = e.target.closest('.comprobante-btn');

        if (!button) return;

        if (state.selectedCustomer && button.dataset.tipo === 'TICKET') {
            UI.showAlert(
                dom.alertModal,
                'No se puede emitir un Ticket a un cliente identificado.',
                'Operación no permitida'
            );
            return;
        }

        state.tipoComprobante = button.dataset.tipo;

        dom.comprobanteSelector
            ?.querySelectorAll('.comprobante-btn')
            .forEach(btn => btn.classList.remove('selected'));

        button.classList.add('selected');
        updateFullUI();
    }

    function handlePaymentMethodClick(e) {
        const button = e.target.closest('.payment-method-btn');

        if (!button) return;

        state.paymentMethod = button.dataset.method;

        dom.paymentMethodSelector
            ?.querySelectorAll('.payment-method-btn')
            .forEach(btn => btn.classList.remove('selected'));

        button.classList.add('selected');

        dom.efectivoDetails?.classList.toggle('hidden', state.paymentMethod !== 'EFECTIVO');
        dom.yapeDetails?.classList.toggle('hidden', state.paymentMethod !== 'YAPE');
    }

    function handleMontoRecibidoInput() {
        const recibido = numberValue(dom.montoRecibidoInput?.value);
        const totals = Cart.getCartTotals(state.tipoComprobante);
        const vuelto = Math.max(recibido - totals.total, 0);

        if (dom.vueltoDisplay) {
            dom.vueltoDisplay.textContent = `S/ ${vuelto.toFixed(2)}`;
        }
    }

    function abrirPago() {
        if (!validarCarritoAntesDePago()) return;

        const totals = Cart.getCartTotals(state.tipoComprobante);

        UI.abrirModalDePago(
            dom.paymentModal,
            dom.paymentTotalDisplay,
            dom.montoRecibidoInput,
            dom.vueltoDisplay,
            totals.total,
            Cart.getCart()
        );
    }

    function handleAlertClick(e) {
        if (e.target.id === 'alert-modal' || e.target.id === 'alert-ok-btn') {
            dom.alertModal.classList.add('hidden');

            if (String(e.target.textContent || '').trim().toLowerCase() === 'nueva venta') {
                resetPOS();
            }
        }
    }

    function setupCustomerSuggestionsPortal() {
        if (!dom.customerSuggestions || !dom.customerSearchInput) return;

        document.body.appendChild(dom.customerSuggestions);

        dom.customerSuggestions.className =
            'fixed z-[99999] hidden max-h-80 overflow-y-auto rounded-2xl border border-slate-200 bg-white shadow-[0_30px_90px_rgba(15,23,42,0.25)]';

        const position = () => {
            const rect = dom.customerSearchInput.getBoundingClientRect();

            dom.customerSuggestions.style.left = `${rect.left}px`;
            dom.customerSuggestions.style.top = `${rect.bottom + 8}px`;
            dom.customerSuggestions.style.width = `${rect.width}px`;
        };

        dom.customerSearchInput.addEventListener('input', position);
        dom.customerSearchInput.addEventListener('focus', position);
        window.addEventListener('resize', position);
        window.addEventListener('scroll', position, true);
    }

    async function iniciarScanner() {
        if (!dom.barcodeVideo || !dom.scannerCameraBox || !dom.toggleScannerBtn) return;

        if (!('BarcodeDetector' in window)) {
            UI.showAlert(
                dom.alertModal,
                'Tu navegador no soporta escaneo nativo. Usa el campo de código manual.',
                'Scanner no disponible'
            );
            return;
        }

        try {
            state.scannerDetector = new BarcodeDetector({
                formats: [
                    'ean_13',
                    'ean_8',
                    'upc_a',
                    'upc_e',
                    'code_128',
                    'code_39',
                    'itf',
                ],
            });

            state.scannerStream = await navigator.mediaDevices.getUserMedia({
                video: {
                    facingMode: { ideal: 'environment' },
                    width: { ideal: 1280 },
                    height: { ideal: 720 },
                },
                audio: false,
            });

            dom.barcodeVideo.srcObject = state.scannerStream;
            await dom.barcodeVideo.play();

            state.scannerActivo = true;
            dom.scannerCameraBox.classList.remove('hidden');
            dom.toggleScannerBtn.textContent = 'Detener';
            dom.scannerStatus.textContent = 'Apunta al código de barras del producto';

            escanearFrame();

        } catch (error) {
            detenerScanner();

            UI.showAlert(
                dom.alertModal,
                'No se pudo acceder a la cámara. Revisa permisos del navegador.',
                'Cámara no disponible'
            );
        }
    }

    function detenerScanner() {
        state.scannerActivo = false;

        if (state.scannerLoopId) {
            cancelAnimationFrame(state.scannerLoopId);
            state.scannerLoopId = null;
        }

        if (state.scannerStream) {
            state.scannerStream.getTracks().forEach(track => track.stop());
            state.scannerStream = null;
        }

        if (dom.barcodeVideo) {
            dom.barcodeVideo.srcObject = null;
        }

        if (dom.scannerCameraBox) {
            dom.scannerCameraBox.classList.add('hidden');
        }

        if (dom.toggleScannerBtn) {
            dom.toggleScannerBtn.textContent = 'Escanear';
        }

        if (dom.scannerStatus) {
            dom.scannerStatus.textContent = 'Apunta al código de barras del producto';
        }
    }

    async function escanearFrame() {
        if (!state.scannerActivo || !state.scannerDetector || !dom.barcodeVideo) return;

        try {
            const codes = await state.scannerDetector.detect(dom.barcodeVideo);

            if (codes.length) {
                const rawValue = String(codes[0].rawValue || '').trim();
                const now = Date.now();

                if (
                    rawValue &&
                    (
                        rawValue !== state.ultimoCodigoEscaneado ||
                        now - state.ultimoEscaneoTime > 2500
                    )
                ) {
                    state.ultimoCodigoEscaneado = rawValue;
                    state.ultimoEscaneoTime = now;

                    if (dom.scannerStatus) {
                        dom.scannerStatus.textContent = `Código detectado: ${rawValue}`;
                    }

                    await buscarPorCodigoBarra(rawValue);
                }
            }
        } catch (error) {
            if (dom.scannerStatus) {
                dom.scannerStatus.textContent = 'Buscando código...';
            }
        }

        state.scannerLoopId = requestAnimationFrame(escanearFrame);
    }

    function setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                dom.paymentModal?.classList.add('hidden');
                dom.newCustomerModal?.classList.add('hidden');
                dom.cierreCajaModal?.classList.add('hidden');
                dom.alertModal?.classList.add('hidden');
                detenerScanner();
            }

            if (e.key === 'F2') {
                e.preventDefault();
                dom.customerSearchInput?.focus();
            }

            if (e.key === 'F3') {
                e.preventDefault();
                dom.searchInput?.focus();
            }

            if (e.key === 'F4') {
                e.preventDefault();
                abrirPago();
            }

            if (e.key === 'F8') {
                e.preventDefault();
                resetPOS();
            }
        });
    }

    dom.searchInput?.addEventListener('input', e => {
        buscarProductosDebounced(e.target.value);
    });

    dom.mobileProductSearchInput?.addEventListener('input', e => {
        buscarProductosMobileDebounced(e.target.value);
    });

    dom.productGrid?.addEventListener('click', handleProductClick);
    dom.mobileProductGrid?.addEventListener('click', handleProductClick);

    dom.customerSearchInput?.addEventListener('input', e => {
        buscarClientesDebounced(e.target.value);
    });

    dom.clearCustomerBtn?.addEventListener('click', () => {
        Customer.limpiarCliente(state, dom);
    });

    dom.newCustomerForm?.addEventListener('submit', e => {
        Customer.guardarNuevoCliente(e, dom, state, csrftoken);
    });

    dom.cancelModalBtn?.addEventListener('click', () => {
        dom.newCustomerModal.classList.add('hidden');
    });

    dom.comprobanteSelector?.addEventListener('click', handleComprobanteClick);

    dom.cartItemsContainer?.addEventListener('click', handleCartClick);
    dom.cartItemsContainer?.addEventListener('input', handleCartInput);

    dom.mobileCartItems?.addEventListener('click', handleCartClick);
    dom.mobileCartItems?.addEventListener('input', handleCartInput);

    dom.proceedToPaymentBtn?.addEventListener('click', abrirPago);
    dom.mobilePayBtn?.addEventListener('click', abrirPago);

    dom.paymentForm?.addEventListener('submit', handleFinalizarVenta);

    dom.paymentModalCloseBtn?.addEventListener('click', () => {
        dom.paymentModal.classList.add('hidden');
    });

    dom.paymentMethodSelector?.addEventListener('click', handlePaymentMethodClick);
    dom.montoRecibidoInput?.addEventListener('input', handleMontoRecibidoInput);
    dom.alertModal?.addEventListener('click', handleAlertClick);

    dom.aperturaCajaForm?.addEventListener('submit', e => {
        Caja.handleAbrirCaja(e, dom, csrftoken);
    });

    dom.cierreCajaForm?.addEventListener('submit', e => {
        Caja.handleCerrarCaja(e, dom, csrftoken);
    });

    dom.showCierreModalBtn?.addEventListener('click', () => {
        dom.cierreCajaModal.classList.remove('hidden');
    });

    dom.cierreModalCloseBtn?.addEventListener('click', () => {
        dom.cierreCajaModal.classList.add('hidden');
    });

    dom.toggleScannerBtn?.addEventListener('click', () => {
        if (state.scannerActivo) {
            detenerScanner();
        } else {
            iniciarScanner();
        }
    });

    dom.barcodeSearchBtn?.addEventListener('click', () => {
        buscarPorCodigoBarra(dom.barcodeManualInput?.value);
    });

    dom.barcodeManualInput?.addEventListener('keydown', e => {
        if (e.key === 'Enter') {
            e.preventDefault();
            buscarPorCodigoBarra(e.target.value);
        }
    });

    setupCustomerSuggestionsPortal();
    setupKeyboardShortcuts();

    Caja.verificarEstadoCaja(dom);
    renderProductInitial(dom.productGrid);
    renderProductInitial(dom.mobileProductGrid);
    updateFullUI();
});