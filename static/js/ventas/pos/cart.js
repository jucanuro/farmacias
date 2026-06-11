// static/js/ventas/pos/cart.js

let cart = [];
const TASA_IGV = 0.18;

export function getCart() {
    return cart;
}

export function addToCart(producto, showAlert) {
    const existingItem = cart.find(item => item.id === producto.id);
    
    if (existingItem) {
        existingItem.quantity++;
    } else {
        if (typeof producto.precio_venta === 'undefined' || producto.precio_venta === null || producto.precio_venta <= 0) {
            showAlert(`El producto "${producto.nombre}" no tiene un precio de venta válido.`, 'Error');
            return false; 
        }
        cart.push({ ...producto, quantity: 1, precio_unitario: producto.precio_venta, hasDiscount: false, monto_descuento_linea: 0 });
    }
    
    return true; 
}

export function updateCartItem(itemId, field, value) {
    const item = cart.find(i => i.id === itemId);
    if (!item) return;

    if (field === 'quantity') item.quantity = parseInt(value) || 1;
    if (field === 'monto_descuento_linea') item.monto_descuento_linea = parseFloat(value) || 0;
    if (field === 'hasDiscount') {
        item.hasDiscount = value;
        if (!item.hasDiscount) item.monto_descuento_linea = 0;
    }
}

export function removeFromCart(itemId) {
    cart = cart.filter(i => i.id !== itemId);
}

export function getCartTotals(tipoComprobante) {

    const total = cart.reduce(
        (acc, item) =>
            acc +
            (item.quantity * (item.precio_unitario || 0)) -
            (item.monto_descuento_linea || 0),
        0
    );

    const subtotal =
        (tipoComprobante === 'BOLETA' || tipoComprobante === 'FACTURA')
            ? total / (1 + TASA_IGV)
            : total;

    const impuestos =
        (tipoComprobante === 'BOLETA' || tipoComprobante === 'FACTURA')
            ? total - subtotal
            : 0;

    return {
        subtotal: Number(subtotal.toFixed(2)),
        impuestos: Number(impuestos.toFixed(2)),
        total: Number(total.toFixed(2))
    };
}

export function clearCart() {
    cart = [];
}