// static/js/scripts.js

document.addEventListener('DOMContentLoaded', function() {

    // Función para actualizar el nombre del archivo en la interfaz
    const updateFileName = (fileInputId, fileNameId) => {
        const fileInput = document.getElementById(fileInputId);
        const fileNameSpan = document.getElementById(fileNameId);
        fileInput.addEventListener('change', function() {
            if (fileInput.files.length > 0) {
                fileNameSpan.textContent = `Archivo: ${fileInput.files[0].name}`;
            } else {
                fileNameSpan.textContent = '';
            }
        });
    };

    // Inicializar la actualización de nombres de archivo para cada sección
    updateFileName('text-file-input', 'text-file-name');
    updateFileName('image-file-input', 'image-file-name');
    updateFileName('audio-file-input', 'audio-file-name');

    // Función genérica para manejar las solicitudes de compresión/descompresión
    const handleRequest = async (url, fileInputId, resultDivId) => {
        const fileInput = document.getElementById(fileInputId);
        const resultDiv = document.getElementById(resultDivId);
        
        if (fileInput.files.length === 0) {
            resultDiv.innerHTML = `<p>Error: Por favor, selecciona un archivo primero.</p>`;
            resultDiv.className = 'result error';
            resultDiv.style.display = 'block';
            return;
        }

        const file = fileInput.files[0];
        const formData = new FormData();
        formData.append('file', file);
        
        resultDiv.innerHTML = `<div class="loader"></div><p>Procesando solicitud...</p>`;
        resultDiv.className = 'result';
        resultDiv.style.display = 'block';

        try {
            const response = await fetch(url, {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (response.ok) {
                const formatBytes = (bytes, decimals = 2) => {
                    if (bytes === 0) return '0 Bytes';
                    const k = 1024;
                    const dm = decimals < 0 ? 0 : decimals;
                    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
                    const i = Math.floor(Math.log(bytes) / Math.log(k));
                    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
                };
                
                // Calcular el porcentaje de reducción
                const reduction = (1 - (data.compressed_size / data.original_size)) * 100;
                const reductionText = data.original_size > 0 ? `(Reducción del ${reduction.toFixed(2)}%)` : '';

                resultDiv.innerHTML = `
                    <p><strong>Operación completada con éxito.</strong></p>
                    <p>Tamaño Original: <strong>${formatBytes(data.original_size)}</strong></p>
                    <p>Tamaño Final: <strong>${formatBytes(data.compressed_size)}</strong> ${reductionText}</p>
                    <a href="${data.download_url}" class="download-link" download>Descargar Resultado</a>
                `;
                resultDiv.className = 'result';
            } else {
                resultDiv.innerHTML = `<p>Error: ${data.error || 'Ocurrió un error desconocido.'}</p>`;
                resultDiv.className = 'result error';
            }
        } catch (error) {
            resultDiv.innerHTML = `<p>Error de conexión con el servidor. Inténtalo de nuevo.</p>`;
            resultDiv.className = 'result error';
            console.error('Error:', error);
        }
    };

    // --- Asignar eventos a los botones ---
    document.getElementById('compress-text-btn').addEventListener('click', () => handleRequest('/compress_text', 'text-file-input', 'text-result'));
    document.getElementById('decompress-text-btn').addEventListener('click', () => handleRequest('/decompress_text', 'text-file-input', 'text-result'));

    document.getElementById('compress-image-btn').addEventListener('click', () => handleRequest('/compress_image', 'image-file-input', 'image-result'));
    document.getElementById('decompress-image-btn').addEventListener('click', () => handleRequest('/decompress_image', 'image-file-input', 'image-result'));

    document.getElementById('compress-audio-btn').addEventListener('click', () => handleRequest('/compress_audio', 'audio-file-input', 'audio-result'));
    document.getElementById('decompress-audio-btn').addEventListener('click', () => handleRequest('/decompress_audio', 'audio-file-input', 'audio-result'));
});