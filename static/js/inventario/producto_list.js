// static/js/inventario/producto_list.js

document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('product-search-input');
    const tableBody = document.getElementById('product-table-body');
    const tableRows = tableBody.getElementsByTagName('tr');

    searchInput.addEventListener('keyup', () => {
        const searchTerm = searchInput.value.toLowerCase();

        for (const row of tableRows) {
            const rowText = row.textContent.toLowerCase();

            if (rowText.includes(searchTerm)) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        }
    });
});