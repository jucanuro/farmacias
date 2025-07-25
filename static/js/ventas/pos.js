import * as API from './pos/api.js';
import * as Cart from './pos/cart.js';
import * as UI from './pos/ui.js';
import * as Customer from './pos/customer.js';
import * as Caja from './pos/caja.js';

document.addEventListener('DOMContentLoaded', () => {
    // === ESTADO DE LA APLICACIÓN ===
    const state = {
        tipoComprobante: 'TICKET',
        selectedCustomer: null,
        paymentMethod: 'EFECTIVO',
    };
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';

    // === ELEMENTOS DEL DOM ===
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
        modalNumeroDocumentoInput: document.getElementById('modal-numero-documento'),
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
    };

    // === FUNCIÓN CENTRAL DE ACTUALIZACIÓN ===
    const updateFullUI = () => {
        const cart = Cart.getCart();
        const totals = Cart.getCartTotals(state.tipoComprobante);
        UI.renderCart(dom.cartItemsContainer, cart, totals);
    };

    // === MANEJADORES DE LÓGICA PRINCIPAL ===
    const handleFinalizarVenta = async (e) => {
        e.preventDefault();
        dom.confirmPaymentBtn.disabled = true;
        dom.confirmPaymentBtn.textContent = 'Procesando...';
        
        const cart = Cart.getCart();
        const totals = Cart.getCartTotals(state.tipoComprobante);

        const detalles = cart.map(item => ({
            producto: item.id,
            cantidad: item.quantity,
            precio_unitario: item.precio_unitario,
            monto_descuento_linea: item.monto_descuento_linea || 0,
            unidad_venta: 'UNIDAD'
        }));

        const ventaData = {
            cliente: state.selectedCustomer ? state.selectedCustomer.id : null,
            tipo_comprobante: state.tipoComprobante,
            metodo_pago: state.paymentMethod,
            monto_recibido: state.paymentMethod === 'EFECTIVO' ? parseFloat(dom.montoRecibidoInput.value) : totals.total,
            vuelto: state.paymentMethod === 'EFECTIVO' ? parseFloat(dom.vueltoDisplay.textContent.replace('S/ ', '')) : 0,
            detalles: detalles
        };

        try {
            const nuevaVenta = await API.finalizarVentaAPI(ventaData, csrftoken);
            resetPOS();
            UI.showActionDialog(dom.alertModal, `Venta #${nuevaVenta.id} registrada`, '¡Venta Completada!', nuevaVenta);
        } catch (error) {
            let errorMessage = "No se pudo registrar la venta.\n\n";
            if (error.non_field_errors) errorMessage = error.non_field_errors.join('\n');
            else if (typeof error === 'object') {
                for (const field in error) errorMessage += `• ${field}: ${JSON.stringify(error[field])}\n`;
            }
            UI.showAlert(dom.alertModal, errorMessage, 'Error de Registro');
        } finally {
            dom.confirmPaymentBtn.disabled = false;
            dom.confirmPaymentBtn.textContent = 'Confirmar Venta';
        }
    };
    
    const resetPOS = () => {
        Cart.clearCart();
        Customer.limpiarCliente(state, dom);
        dom.paymentModal.classList.add('hidden');
        dom.searchInput.value = '';
        dom.productGrid.innerHTML = '<p class="col-span-full text-center text-slate-500 py-16">Escribe en la barra para buscar...</p>';
        updateFullUI();
    };

    // === EVENT LISTENERS ===
    let productSearchTimeout, customerSearchTimeout;
    dom.searchInput.addEventListener('keyup', e => {
        clearTimeout(productSearchTimeout);
        productSearchTimeout = setTimeout(() => API.buscarProductosAPI(e.target.value.trim()).then(data => UI.renderProductGrid(dom.productGrid, data.results || data)).catch(console.error), 300);
    });

    dom.productGrid.addEventListener('click', e => {
        // -- PRUEBA 1: ¿Se detecta el clic en la cuadrícula? --
        console.log('Se hizo clic en la cuadrícula de productos.');

        const card = e.target.closest('.add-to-cart-btn');
        
        if (card) {
            // -- PRUEBA 2: ¿Encontramos el producto correcto? --
            console.log('Elemento del producto encontrado:', card);
            
            try {
                const productoJson = card.dataset.productoJson;
                // -- PRUEBA 3: ¿Tenemos los datos del producto? --
                console.log('Datos JSON del producto:', productoJson);
                
                if (!productoJson) {
                    throw new Error("El atributo data-producto-json está vacío o no existe.");
                }

                const producto = JSON.parse(productoJson);
                
                // -- PRUEBA 4: ¿Se va a llamar a la función para añadir al carrito? --
                console.log('Llamando a Cart.addToCart con el producto:', producto);
                
                if(Cart.addToCart(producto, (msg, title) => UI.showAlert(dom.alertModal, msg, title))) {
                    updateFullUI();
                    console.log('Producto añadido y UI actualizada.');
                }
            } catch (error) {
                console.error('¡ERROR! No se pudo procesar el producto:', error);
                UI.showAlert(dom.alertModal, 'Hubo un error al leer los datos del producto. Revisa la consola para más detalles.', 'Error Crítico');
            }

        } else {
            console.log('Clic detectado, pero no se encontró un elemento de producto con la clase .add-to-cart-btn.');
        }
    });

    dom.customerSearchInput.addEventListener('keyup', e => {
        clearTimeout(customerSearchTimeout);
        customerSearchTimeout = setTimeout(() => Customer.buscarCliente(e.target.value.trim(), dom, state), 300);
    });

    dom.clearCustomerBtn.addEventListener('click', () => Customer.limpiarCliente(state, dom));

    dom.newCustomerForm.addEventListener('submit', (e) => Customer.guardarNuevoCliente(e, dom, state, csrftoken));
    dom.cancelModalBtn.addEventListener('click', () => dom.newCustomerModal.classList.add('hidden'));
    
    dom.comprobanteSelector.addEventListener('click', e => {
        if (e.target.classList.contains('comprobante-btn')) {
            if (state.selectedCustomer && e.target.dataset.tipo === 'TICKET') {
                UI.showAlert(dom.alertModal, 'No se puede emitir un Ticket a un cliente identificado.', 'Operación no permitida');
                return;
            }
            state.tipoComprobante = e.target.dataset.tipo;
            dom.comprobanteSelector.querySelectorAll('.comprobante-btn').forEach(btn => btn.classList.remove('selected'));
            e.target.classList.add('selected');
            updateFullUI();
        }
    });

   dom.cartItemsContainer.addEventListener('change', e => {
        const target = e.target;
        const itemElement = target.closest('[data-item-id]');
        if (!itemElement) return;
        const itemId = parseInt(itemElement.dataset.itemId);

        if (target.classList.contains('quantity-input')) {
            Cart.updateCartItem(itemId, 'quantity', target.value);
        }
        if (target.classList.contains('discount-input')) {
            Cart.updateCartItem(itemId, 'monto_descuento_linea', target.value);
        }
        
        // Actualizamos la UI solo cuando terminas de editar y sales del campo
        updateFullUI();
    });

// Listener para cuando HACES CLIC en un botón (eliminar, checkbox)
    dom.cartItemsContainer.addEventListener('click', e => {
        const target = e.target;
        const itemElement = target.closest('[data-item-id]');
        if (!itemElement) return;
        const itemId = parseInt(itemElement.dataset.itemId);

        if (target.classList.contains('discount-checkbox')) {
            Cart.updateCartItem(itemId, 'hasDiscount', target.checked);
            updateFullUI();
        }
        
        if (target.closest('.remove-item-btn')) {
            Cart.removeFromCart(itemId);
            updateFullUI();
        }
    });

    dom.proceedToPaymentBtn.addEventListener('click', () => {
        const totals = Cart.getCartTotals(state.tipoComprobante);
        UI.abrirModalDePago(dom.paymentModal, dom.paymentTotalDisplay, dom.montoRecibidoInput, dom.vueltoDisplay, totals.total, Cart.getCart());
    });
    
    dom.paymentForm.addEventListener('submit', handleFinalizarVenta);
    dom.paymentModalCloseBtn.addEventListener('click', () => dom.paymentModal.classList.add('hidden'));

    dom.paymentMethodSelector.addEventListener('click', (e) => {
        if (e.target.classList.contains('payment-method-btn')) {
            state.paymentMethod = e.target.dataset.method;
            dom.paymentMethodSelector.querySelectorAll('.payment-method-btn').forEach(btn => btn.classList.remove('selected'));
            e.target.classList.add('selected');
            dom.efectivoDetails.classList.toggle('hidden', state.paymentMethod !== 'EFECTIVO');
            dom.yapeDetails.classList.toggle('hidden', state.paymentMethod !== 'YAPE');
        }
    });

    dom.montoRecibidoInput.addEventListener('input', (e) => {
        const recibido = parseFloat(e.target.value) || 0;
        const totals = Cart.getCartTotals(state.tipoComprobante);
        const vuelto = recibido - totals.total;
        dom.vueltoDisplay.textContent = `S/ ${(vuelto >= 0 ? vuelto : 0).toFixed(2)}`;
    });

    dom.alertModal.addEventListener('click', e => {
        if (e.target.id === 'alert-modal' || e.target.id === 'alert-ok-btn') {
            dom.alertModal.classList.add('hidden');
            if (e.target.textContent === 'Nueva Venta') resetPOS();
        }
    });
    
    // --- Caja Listeners ---
    dom.aperturaCajaForm.addEventListener('submit', (e) => Caja.handleAbrirCaja(e, dom, csrftoken));
    dom.cierreCajaForm.addEventListener('submit', (e) => Caja.handleCerrarCaja(e, dom, csrftoken));
    dom.showCierreModalBtn.addEventListener('click', () => dom.cierreCajaModal.classList.remove('hidden'));
    dom.cierreModalCloseBtn.addEventListener('click', () => dom.cierreCajaModal.classList.add('hidden'));

    // === CARGA INICIAL ===
    Caja.verificarEstadoCaja(dom);
    updateFullUI();
});