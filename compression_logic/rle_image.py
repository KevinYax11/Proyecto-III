# compression_logic/rle_image.py

import pickle
from PIL import Image

def compress_image(input_path, output_path):
    """
    [cite_start]Comprime una imagen utilizando el algoritmo Run-Length Encoding (RLE) pixel por pixel. [cite: 12, 13]
    """
    try:
        # Abrir la imagen y obtener sus datos
        img = Image.open(input_path)
        pixels = list(img.getdata())
        width, height = img.size
    except Exception as e:
        print(f"Error al abrir la imagen: {e}")
        return

    encoded_pixels = []
    
    if not pixels:
        return # No hay nada que comprimir

    # Implementación de RLE
    count = 1
    current_pixel = pixels[0]

    for i in range(1, len(pixels)):
        if pixels[i] == current_pixel:
            count += 1
        else:
            encoded_pixels.append((count, current_pixel))
            count = 1
            current_pixel = pixels[i]
    
    # Añadir el último grupo de píxeles
    encoded_pixels.append((count, current_pixel))

    # [cite_start]Guardar las dimensiones de la imagen y los datos RLE en un archivo [cite: 15]
    with open(output_path, 'wb') as f:
        pickle.dump({'width': width, 'height': height, 'data': encoded_pixels}, f)
    
    print(f"Imagen comprimida con RLE y guardada en: {output_path}")

def decompress_image(input_path, output_path):
    """
    [cite_start]Descomprime una imagen desde un archivo RLE y la reconstruye. [cite: 15]
    """
    try:
        with open(input_path, 'rb') as f:
            data_dict = pickle.load(f)
    except Exception as e:
        print(f"Error al leer el archivo RLE: {e}")
        return

    width = data_dict['width']
    height = data_dict['height']
    encoded_data = data_dict['data']

    # Decodificar los datos RLE para reconstruir la lista de píxeles
    decoded_pixels = []
    for count, pixel in encoded_data:
        decoded_pixels.extend([pixel] * count)

    # Crear una nueva imagen y colocar los píxeles
    img = Image.new('RGB', (width, height))
    img.putdata(decoded_pixels)
    
    # Guardar la imagen reconstruida
    img.save(output_path)
    
    print(f"Imagen descomprimida y guardada en: {output_path}")