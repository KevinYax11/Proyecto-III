# app.py

import os
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename

# Importar los módulos de lógica de compresión
from compression_logic import huffman, rle_image, audio_comp

# Inicialización de la aplicación Flask
app = Flask(__name__)

# Configuración de la carpeta para subir archivos
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ruta principal que renderiza la interfaz gráfica
@app.route('/')
def index():
    """
    Renderiza la página principal (index.html).
    """
    return render_template('index.html')

# --- RUTAS PARA COMPRESIÓN DE TEXTO ---

@app.route('/compress_text', methods=['POST'])
def compress_text_route():
    """
    Ruta para comprimir un archivo de texto usando el algoritmo de Huffman.
    Recibe un archivo .txt y devuelve la ruta al archivo comprimido y los tamaños.
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No se encontró el archivo'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No se seleccionó ningún archivo'}), 400

    if file and file.filename.endswith('.txt'):
        # Guardar el archivo original
        filename = secure_filename(file.filename)
        original_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(original_path)

        # Definir la ruta del archivo de salida
        compressed_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{os.path.splitext(filename)[0]}.huff")

        # [cite_start]Llamar a la función de compresión de Huffman [cite: 9]
        huffman.compress(original_path, compressed_path)

        # [cite_start]Obtener tamaños para la comparación [cite: 25]
        original_size = os.path.getsize(original_path)
        compressed_size = os.path.getsize(compressed_path)

        return jsonify({
            'message': 'Archivo de texto comprimido exitosamente.',
            'original_size': original_size,
            'compressed_size': compressed_size,
            'download_url': f'/download/{os.path.basename(compressed_path)}'
        })
    else:
        return jsonify({'error': 'Formato de archivo no válido. Se esperaba un .txt'}), 400


@app.route('/decompress_text', methods=['POST'])
def decompress_text_route():
    """
    Ruta para descomprimir un archivo de texto (.huff).
    Devuelve la ruta al archivo descomprimido y los tamaños.
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No se encontró el archivo'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No se seleccionó ningún archivo'}), 400
    
    if file and file.filename.endswith('.huff'):
        # Guardar el archivo comprimido
        filename = secure_filename(file.filename)
        compressed_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(compressed_path)
        
        # Definir la ruta del archivo descomprimido
        decompressed_path = os.path.join(app.config['UPLOAD_FOLDER'], f"decompressed_{os.path.splitext(filename)[0]}.txt")
        
        # Llamar a la función de descompresión de Huffman
        huffman.decompress(compressed_path, decompressed_path)

        # Obtener tamaños para la comparación
        compressed_size = os.path.getsize(compressed_path)
        decompressed_size = os.path.getsize(decompressed_path)

        return jsonify({
            'message': 'Archivo de texto descomprimido exitosamente.',
            'original_size': compressed_size,
            'compressed_size': decompressed_size,
            'download_url': f'/download/{os.path.basename(decompressed_path)}'
        })
    else:
        return jsonify({'error': 'Formato de archivo no válido. Se esperaba un .huff'}), 400


# --- RUTAS PARA COMPRESIÓN DE IMÁGENES ---

@app.route('/compress_image', methods=['POST'])
def compress_image_route():
    """
    [cite_start]Ruta para comprimir una imagen usando Run-Length Encoding (RLE). [cite: 13]
    [cite_start]Recibe un archivo .png o .bmp y devuelve la ruta al archivo comprimido. [cite: 14]
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No se encontró el archivo'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No se seleccionó ningún archivo'}), 400

    if file and (file.filename.endswith('.png') or file.filename.endswith('.bmp')):
        filename = secure_filename(file.filename)
        original_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(original_path)

        compressed_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{os.path.splitext(filename)[0]}.rle")

        # Llamar a la función de compresión RLE para imágenes
        rle_image.compress_image(original_path, compressed_path)

        original_size = os.path.getsize(original_path)
        compressed_size = os.path.getsize(compressed_path)

        return jsonify({
            'message': 'Imagen comprimida exitosamente.',
            'original_size': original_size,
            'compressed_size': compressed_size,
            'download_url': f'/download/{os.path.basename(compressed_path)}'
        })
    else:
        return jsonify({'error': 'Formato no válido. Se esperaba .png o .bmp'}), 400


@app.route('/decompress_image', methods=['POST'])
def decompress_image_route():
    """
    [cite_start]Ruta para descomprimir una imagen (.rle) y reconstruirla. [cite: 15]
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No se encontró el archivo'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No se seleccionó ningún archivo'}), 400
        
    if file and file.filename.endswith('.rle'):
        filename = secure_filename(file.filename)
        compressed_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(compressed_path)

        decompressed_path = os.path.join(app.config['UPLOAD_FOLDER'], f"decompressed_{os.path.splitext(filename)[0]}.png")
        
        # Llamar a la función de descompresión RLE para imágenes
        rle_image.decompress_image(compressed_path, decompressed_path)

        compressed_size = os.path.getsize(compressed_path)
        decompressed_size = os.path.getsize(decompressed_path)

        return jsonify({
            'message': 'Imagen descomprimida exitosamente.',
            'original_size': compressed_size,
            'compressed_size': decompressed_size,
            'download_url': f'/download/{os.path.basename(decompressed_path)}'
        })
    else:
        return jsonify({'error': 'Formato no válido. Se esperaba .rle'}), 400

# --- RUTAS PARA COMPRESIÓN DE AUDIO ---

@app.route('/compress_audio', methods=['POST'])
def compress_audio_route():
    """
    [cite_start]Ruta para comprimir un archivo de audio WAV usando Huffman sobre los bytes. [cite: 18, 19]
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No se encontró el archivo'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No se seleccionó ningún archivo'}), 400

    if file and file.filename.endswith('.wav'):
        filename = secure_filename(file.filename)
        original_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(original_path)
        
        compressed_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{os.path.splitext(filename)[0]}.huffaudio")

        audio_comp.compress_audio(original_path, compressed_path)
        
        original_size = os.path.getsize(original_path)
        compressed_size = os.path.getsize(compressed_path)
        
        return jsonify({
            'message': 'Audio comprimido exitosamente.',
            'original_size': original_size,
            'compressed_size': compressed_size,
            'download_url': f'/download/{os.path.basename(compressed_path)}'
        })
    else:
        return jsonify({'error': 'Formato no válido. Se esperaba .wav'}), 400


@app.route('/decompress_audio', methods=['POST'])
def decompress_audio_route():
    """
    [cite_start]Ruta para descomprimir un archivo de audio (.huffaudio) y reconstruirlo a .wav. [cite: 20]
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No se encontró el archivo'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No se seleccionó ningún archivo'}), 400
        
    if file and file.filename.endswith('.huffaudio'):
        filename = secure_filename(file.filename)
        compressed_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(compressed_path)

        decompressed_path = os.path.join(app.config['UPLOAD_FOLDER'], f"decompressed_{os.path.splitext(filename)[0]}.wav")

        audio_comp.decompress_audio(compressed_path, decompressed_path)
        
        compressed_size = os.path.getsize(compressed_path)
        decompressed_size = os.path.getsize(decompressed_path)

        return jsonify({
            'message': 'Audio descomprimido exitosamente.',
            'original_size': compressed_size,
            'compressed_size': decompressed_size,
            'download_url': f'/download/{os.path.basename(decompressed_path)}'
        })
    else:
        return jsonify({'error': 'Formato no válido. Se esperaba .huffaudio'}), 400

# --- RUTA PARA DESCARGAR ARCHIVOS ---

@app.route('/download/<filename>')
def download_file(filename):
    """
    Permite al usuario descargar los archivos generados desde la carpeta 'uploads'.
    """
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)