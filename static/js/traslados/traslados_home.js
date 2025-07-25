// static/js/traslados/traslados_home.js

document.addEventListener('DOMContentLoaded', () => {
    
    // Función para leer el token de seguridad desde las cookies
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    const csrftoken = getCookie('csrftoken');

    const tableBody = document.getElementById('transfers-list-body');

    const estadoStyles = {
        'PENDIENTE': 'bg-amber-500/20 text-amber-400',
        'EN_TRANSITO': 'bg-sky-500/20 text-sky-400',
        'RECIBIDO': 'bg-emerald-500/20 text-emerald-400',
        'CANCELADO': 'bg-rose-500/20 text-rose-400'
    };

    const fetchTransfers = async () => {
        try {
            const response = await fetch('/traslados/api/transferencias/');
            if (!response.ok) throw new Error('No se pudieron cargar los traslados.');
            
            const data = await response.json();
            const transfers = data.results || data;
            
            tableBody.innerHTML = '';
            if (transfers.length === 0) {
                tableBody.innerHTML = `<tr><td colspan="7" class="text-center p-8 text-slate-400">No hay traslados registrados.</td></tr>`;
                return;
            }

            transfers.forEach(transfer => {
                const fecha = new Date(transfer.fecha_creacion).toLocaleDateString('es-PE', { day: '2-digit', month: '2-digit', year: 'numeric' });
                const estilo = estadoStyles[transfer.estado] || 'bg-slate-500/20 text-slate-400';
                
                let actionButtons = '';
                if (transfer.estado === 'PENDIENTE') {
                    actionButtons = `<button data-action="enviar" data-id="${transfer.id}" class="action-btn text-sky-400 hover:text-sky-300 font-semibold" title="Marcar como Enviado">Enviar</button>`;
                } else if (transfer.estado === 'EN_TRANSITO') {
                    actionButtons = `<button data-action="recibir" data-id="${transfer.id}" class="action-btn text-emerald-400 hover:text-emerald-300 font-semibold" title="Marcar como Recibido">Recibir</button>`;
                } else {
                    actionButtons = `<button title="Ver Detalles" class="text-slate-400 hover:text-cyan-400">Ver</button>`;
                }

                const row = `
                    <tr class="border-b border-slate-800 hover:bg-slate-800/50 text-sm">
                        <td class="p-3 font-mono text-slate-400">#${transfer.id}</td>
                        <td class="p-3 text-white">${transfer.sucursal_origen_nombre}</td>
                        <td class="p-3 text-white">${transfer.sucursal_destino_nombre}</td>
                        <td class="p-3"><span class="px-2 py-1 text-xs font-bold rounded-full ${estilo}">${transfer.estado}</span></td>
                        <td class="p-3 text-slate-400">${fecha}</td>
                        <td class="p-3 text-center">${actionButtons}</td>
                    </tr>`;
                tableBody.innerHTML += row;
            });

        } catch (error) {
            console.error(error);
            tableBody.innerHTML = `<tr><td colspan="7" class="text-center p-8 text-rose-400">Error al cargar los traslados.</td></tr>`;
        }
    };

    const handleTransferAction = async (action, transferId) => {
        const url = `/traslados/api/transferencias/${transferId}/${action}/`;
        const confirmationMessage = action === 'enviar' 
            ? '¿Estás seguro de que quieres enviar este traslado? El stock se descontará del origen.'
            : '¿Estás seguro de que quieres recibir este traslado? El stock se añadirá al destino.';

        if (!confirm(confirmationMessage)) {
            return;
        }

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken 
                },
            });
            
            const result = await response.json();
            if (!response.ok) throw new Error(result.error || 'Ocurrió un error.');

            alert(`Éxito: ${result.status}`);
            fetchTransfers();

        } catch (error) {
            alert(`Error: ${error.message}`);
        }
    };

    tableBody.addEventListener('click', (e) => {
        const target = e.target;
        if (target.classList.contains('action-btn')) {
            const action = target.dataset.action;
            const transferId = target.dataset.id;
            handleTransferAction(action, transferId);
        }
    });

    fetchTransfers();
});