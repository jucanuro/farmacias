/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        // 1. Escanea tus templates de Django (dentro de cualquier carpeta 'templates' en el proyecto)
        // La ruta es relativa desde 'static/' (sube un nivel '..' y busca en cualquier subcarpeta 'templates')
        '../**/templates/**/*.html',

        // 2. Escanea cualquier archivo HTML directamente dentro de tu carpeta 'static/'
        // Esto incluye 'farmacias.html', 'sucursales.html', si los tienes allí.
        './*.html',

        // 3. Escanea cualquier archivo HTML en subcarpetas de 'static/' (ej. static/js/some.html)
        './**/*.html',

        // 4. Si tienes archivos JavaScript (React, Vue, JS puro) que añaden/cambian clases dinámicamente:
        // Por ejemplo, si tu JS está en static/js/
        // './js/**/*.js',
        // Si tienes componentes React/Vue en subcarpetas de static/src, ej:
        // './src/**/*.{js,jsx,ts,tsx}',
    ],
    theme: {
        extend: {
            fontFamily: {
                inter: ['Inter', 'sans-serif'], // Asegura que 'Inter' sea reconocido
            },
            // ************ ADD THIS SECTION ************
            backgroundImage: {
                // This defines a custom background image utility class
                // The SVG is a simple downward-pointing arrow, filled with white (%23ffffff)
                'custom-select-arrow-white': "url(\"data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 20 20' fill='none'%3e%3cpath d='M7 10l5 5 5-5H7z' fill='%23ffffff'/%3e%3c/svg%3e\")",
            }
            // ******************************************
        },
    },
    // ************ ADD THIS PLUGIN ************
    plugins: [
        require('@tailwindcss/forms'), // Essential for better default styling of forms (checkboxes, radio, select)
    ],
    // ******************************************
}