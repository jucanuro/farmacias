let cart = [];

const TASA_IGV = 0.18;

export function getCart() {
    return cart;
}

export function addToCart(producto, showAlert) {
    const existingItem = cart.find(
        item => item.id === producto.id
    );

    const stockDisponible =
        Number(
            producto.stock_total ??
            producto.stock_disponible ??
            producto.cantidad_disponible ??
            0
        );

    if (stockDisponible <= 0) {
        showAlert(
            `El producto "${producto.nombre}" no tiene stock disponible.`,
            'Sin stock'
        );

        return false;
    }

    const precioVenta =
        Number(
            producto.precio_venta ??
            producto.precio ??
            0
        );

    if (precioVenta <= 0) {
        showAlert(
            `El producto "${producto.nombre}" no tiene un precio válido.`,
            'Error'
        );

        return false;
    }

    if (existingItem) {

        if (
            Number(existingItem.quantity) + 1 >
            stockDisponible
        ) {
            showAlert(
                `Stock insuficiente para "${producto.nombre}". Disponible: ${stockDisponible}`,
                'Stock insuficiente'
            );

            return false;
        }

        existingItem.quantity++;

    } else {

        cart.push({
            ...producto,

            quantity: 1,

            stock_disponible: stockDisponible,

            precio_unitario: precioVenta,

            hasDiscount: false,

            monto_descuento_linea: 0,
        });
    }

    return true;
}

export function updateCartItem(itemId, field, value) {
    const item = cart.find(
        i => i.id === itemId
    );

    if (!item) return;

    if (field === 'quantity') {

        let cantidad = parseInt(value) || 1;

        const stockDisponible =
            Number(item.stock_disponible || 0);

        if (cantidad < 1) {
            cantidad = 1;
        }

        if (
            stockDisponible > 0 &&
            cantidad > stockDisponible
        ) {
            cantidad = stockDisponible;
        }

        item.quantity = cantidad;
    }

    if (field === 'monto_descuento_linea') {

        const descuento =
            parseFloat(value) || 0;

        const subtotal =
            item.quantity *
            item.precio_unitario;

        item.monto_descuento_linea =
            descuento > subtotal
                ? subtotal
                : descuento;
    }

    if (field === 'hasDiscount') {

        item.hasDiscount = value;

        if (!value) {
            item.monto_descuento_linea = 0;
        }
    }
}

export function removeFromCart(itemId) {
    cart = cart.filter(
        i => i.id !== itemId
    );
}

export function getCartTotals(tipoComprobante) {

    const total = cart.reduce(
        (acc, item) => {

            const subtotalLinea =
                (Number(item.quantity) *
                    Number(item.precio_unitario || 0))
                -
                Number(item.monto_descuento_linea || 0);

            return acc + subtotalLinea;

        },
        0
    );

    const aplicaIGV =
        tipoComprobante === 'BOLETA' ||
        tipoComprobante === 'FACTURA';

    const subtotal = aplicaIGV
        ? total / (1 + TASA_IGV)
        : total;

    const impuestos = aplicaIGV
        ? total - subtotal
        : 0;

    return {
        subtotal: Number(subtotal.toFixed(2)),
        impuestos: Number(impuestos.toFixed(2)),
        total: Number(total.toFixed(2))
    };
}

export function getCantidadItems() {
    return cart.reduce(
        (acc, item) =>
            acc + Number(item.quantity || 0),
        0
    );
}

export function clearCart() {
    cart = [];
}