document.addEventListener('DOMContentLoaded', () => {
    const comprasTableBody = document.getElementById('compras-list-body');
    const modal = document.getElementById('details-modal');
    const modalCloseBtn = document.getElementById('modal-close-btn');
    const modalTitle = document.getElementById('modal-title');
    const modalProveedor = document.getElementById('modal-proveedor');
    const modalFactura = document.getElementById('modal-factura');
    const modalSucursal = document.getElementById('modal-sucursal');
    const modalFecha = document.getElementById('modal-fecha');
    const modalDetailsBody = document.getElementById('modal-details-body');
    const modalGrandTotal = document.getElementById('modal-grand-total');
    const modalTaxes = document.getElementById('modal-taxes');
    const modalPaginationControls = document.getElementById('modal-pagination-controls');
    const modalPrevBtn = document.getElementById('modal-prev-btn');
    const modalNextBtn = document.getElementById('modal-next-btn');
    const modalPageInfo = document.getElementById('modal-page-info');
    const mainPaginationControls = document.getElementById('main-pagination-controls');
    const mainPageInfo = document.getElementById('main-page-info');
    const mainPrevBtn = document.getElementById('main-prev-btn');
    const mainNextBtn = document.getElementById('main-next-btn');

    let nextUrl = null;
    let prevUrl = null;
    let allDetails = [];
    let currentPage = 1;
    const itemsPerPage = 5;

    const estadoStyles = {
        'PENDIENTE': 'bg-amber-500/20 text-amber-400',
        'PROCESADA': 'bg-emerald-500/20 text-emerald-400',
        'ANULADA': 'bg-rose-500/20 text-rose-400'
    };

    const cargarCompras = async (url = '/compras/api/compras/') => {
        comprasTableBody.innerHTML = `<tr><td colspan="8" class="text-center p-8 text-slate-400">Cargando compras...</td></tr>`;
        if (mainPaginationControls) mainPaginationControls.classList.add('hidden');

        try {
            const response = await fetch(url);
            if (!response.ok) throw new Error('No se pudieron cargar los datos.');

            const data = await response.json();
            const compras = data.results;

            comprasTableBody.innerHTML = '';

            if (compras.length === 0) {
                comprasTableBody.innerHTML = `<tr><td colspan="8" class="text-center p-8 text-slate-400">No hay compras registradas.</td></tr>`;
                return;
            }

            nextUrl = data.next;
            prevUrl = data.previous;

            compras.forEach(compra => {
                const fecha = new Date(compra.fecha_recepcion).toLocaleDateString('es-PE', {
                    year: 'numeric', month: '2-digit', day: '2-digit'
                });
                const estilo = estadoStyles[compra.estado] || 'bg-slate-500/20 text-slate-400';
                const row = `
                    <tr class="border-b border-slate-800 hover:bg-slate-800/50 text-sm">
                        <td class="p-3 font-mono text-slate-400">#${compra.id}</td>
                        <td class="p-3 text-white font-semibold">${compra.numero_factura_proveedor || 'S/N'}</td>
                        <td class="p-3 text-slate-300">${compra.proveedor_nombre}</td>
                        <td class="p-3 text-slate-300">${compra.sucursal_destino_nombre}</td>
                        <td class="p-3 text-right font-mono text-emerald-400 font-bold">S/ ${parseFloat(compra.total_compra).toFixed(2)}</td>
                        <td class="p-3"><span class="px-2 py-1 text-xs font-bold rounded-full ${estilo}">${compra.estado}</span></td>
                        <td class="p-3 text-slate-400">${fecha}</td>
                        <td class="p-3">
                            <div class="flex items-center justify-center gap-3">
                                <button type="button" title="Ver Detalles" class="text-slate-400 hover:text-blue-400 transition-colors view-details-btn" data-compra-id="${compra.id}">
                                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor"><path d="M10 12a2 2 0 100-4 2 2 0 000 4z" /><path fill-rule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.27 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clip-rule="evenodd" /></svg>
                                </button>
                                <a href="/compras/${compra.id}/editar/" title="Editar Compra" class="text-slate-400 hover:text-amber-400 transition-colors">
                                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor"><path d="M17.414 2.586a2 2 0 00-2.828 0L7 10.172V13h2.828l7.586-7.586a2 2 0 000-2.828z" /><path fill-rule="evenodd" d="M2 6a2 2 0 012-2h4a1 1 0 010 2H4v10h10v-4a1 1 0 112 0v4a2 2 0 01-2 2H4a2 2 0 01-2-2V6z" clip-rule="evenodd" /></svg>
                                </a>
                            </div>
                        </td>
                    </tr>
                `;
                comprasTableBody.innerHTML += row;
            });

            if (data.count > 10) {
                const pageNumber = new URL(url, window.location.origin).searchParams.get('page') || '1';
                const totalPages = Math.ceil(data.count / 10);
                mainPageInfo.textContent = `Página ${pageNumber} de ${totalPages}`;
                mainPrevBtn.disabled = !prevUrl;
                mainNextBtn.disabled = !nextUrl;
                mainPaginationControls.classList.remove('hidden');
            }

        } catch (error) {
            console.error('Error:', error);
            comprasTableBody.innerHTML = `<tr><td colspan="8" class="text-center p-8 text-rose-400">Error al cargar los datos.</td></tr>`;
        }
    };

    const renderizarPagina = () => {
        modalDetailsBody.innerHTML = '';
        const totalPages = Math.ceil(allDetails.length / itemsPerPage);
        modalPageInfo.textContent = `Página ${currentPage} de ${totalPages}`;
        modalPrevBtn.disabled = currentPage === 1;
        modalNextBtn.disabled = currentPage === totalPages;
        const startIndex = (currentPage - 1) * itemsPerPage;
        const pageItems = allDetails.slice(startIndex, startIndex + itemsPerPage);
        pageItems.forEach(detalle => {
            const subtotal = (detalle.cantidad_recibida * detalle.precio_unitario_compra).toFixed(2);
            const fechaVenc = detalle.fecha_vencimiento ? new Date(detalle.fecha_vencimiento + 'T00:00:00').toLocaleDateString('es-PE') : 'N/A';
            const detalleRow = `
                <tr class="border-b border-slate-800 text-sm">
                    <td class="p-3 text-white font-medium">${detalle.producto_nombre}</td>
                    <td class="p-3 text-slate-300">${detalle.lote}</td>
                    <td class="p-3 text-slate-300">${fechaVenc}</td>
                    <td class="p-3 text-slate-300 text-right">${detalle.cantidad_recibida}</td>
                    <td class="p-3 text-slate-300 text-right font-mono">S/ ${parseFloat(detalle.precio_unitario_compra).toFixed(2)}</td>
                    <td class="p-3 text-white text-right font-mono">S/ ${subtotal}</td>
                </tr>
            `;
            modalDetailsBody.innerHTML += detalleRow;
        });
    };

    const mostrarDetalles = async (compraId) => {
        modal.classList.remove('hidden');
        modalDetailsBody.innerHTML = `<tr><td colspan="6" class="p-8 text-center text-slate-400">Cargando detalles...</td></tr>`;
        modalTaxes.textContent = 'S/ 0.00';
        modalGrandTotal.textContent = 'S/ 0.00';
        modalPaginationControls.classList.add('hidden');

        try {
            const response = await fetch(`/compras/api/compras/${compraId}/`);
            if (!response.ok) throw new Error('No se pudo cargar la información.');
            const compra = await response.json();
            modalTaxes.textContent = `S/ ${parseFloat(compra.impuestos || 0).toFixed(2)}`;
            modalGrandTotal.textContent = `S/ ${parseFloat(compra.total_compra || 0).toFixed(2)}`;
            modalTitle.textContent = `Detalle de la Compra #${compra.id}`;
            modalProveedor.textContent = compra.proveedor_nombre;
            modalFactura.textContent = compra.numero_factura_proveedor;
            modalSucursal.textContent = compra.sucursal_destino_nombre;
            modalFecha.textContent = new Date(compra.fecha_recepcion).toLocaleDateString('es-PE', {
                year: 'numeric', month: 'long', day: 'numeric'
            });
            allDetails = compra.detalles || [];
            currentPage = 1;
            if (allDetails.length > 0) {
                if (allDetails.length > itemsPerPage) {
                    modalPaginationControls.classList.remove('hidden');
                }
                renderizarPagina();
            } else {
                modalDetailsBody.innerHTML = `<tr><td colspan="6" class="p-8 text-center text-slate-400">Esta compra no tiene productos detallados.</td></tr>`;
            }
        } catch (error) {
            modalDetailsBody.innerHTML = `<tr><td colspan="6" class="p-8 text-center text-rose-400">Error al cargar los detalles.</td></tr>`;
            console.error(error);
        }
    };

    comprasTableBody.addEventListener('click', e => {
        const viewButton = e.target.closest('.view-details-btn');
        if (viewButton) {
            mostrarDetalles(viewButton.dataset.compraId);
        }
    });

    modalPrevBtn.addEventListener('click', () => {
        if (currentPage > 1) {
            currentPage--;
            renderizarPagina();
        }
    });

    modalNextBtn.addEventListener('click', () => {
        const totalPages = Math.ceil(allDetails.length / itemsPerPage);
        if (currentPage < totalPages) {
            currentPage++;
            renderizarPagina();
        }
    });

    const cerrarModal = () => modal.classList.add('hidden');
    modalCloseBtn.addEventListener('click', cerrarModal);
    modal.addEventListener('click', e => {
        if (e.target === modal) {
            cerrarModal();
        }
    });

    mainPrevBtn.addEventListener('click', () => {
        if (prevUrl) {
            cargarCompras(prevUrl);
        }
    });

    mainNextBtn.addEventListener('click', () => {
        if (nextUrl) {
            cargarCompras(nextUrl);
        }
    });

    cargarCompras();
});