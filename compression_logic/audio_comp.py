# compression_logic/audio_comp.py

import wave
import pickle
from . import huffman # Reutilizamos el módulo de Huffman

def compress_audio(input_path, output_path):
    """
    Comprime un archivo de audio .wav tratando sus frames como datos binarios
    [cite_start]y aplicando el algoritmo de Huffman. [cite: 16, 18, 19]
    """
    try:
        # Abrir el archivo WAV y leer sus frames y parámetros
        with wave.open(input_path, 'rb') as audio_file:
            params = audio_file.getparams()
            frames = audio_file.readframes(params.nframes)
    except Exception as e:
        print(f"Error al leer el archivo WAV: {e}")
        return

    # Usamos la lógica de Huffman para comprimir los bytes de los frames
    frequency = huffman.make_frequency_dict(frames)
    heap = huffman.make_heap(frequency)
    root = huffman.merge_nodes(heap)
    
    # Limpiamos los diccionarios globales de Huffman antes de usarlos
    huffman.codes = {}
    huffman.reverse_mapping = {}
    
    huffman.make_codes(root)

    encoded_text = ""
    for byte_val in frames:
        encoded_text += huffman.codes[byte_val]
    
    padded_encoded_text = huffman.pad_encoded_text(encoded_text)
    byte_array = huffman.get_byte_array(padded_encoded_text)
    
    # [cite_start]Guardamos los parámetros del WAV y los datos comprimidos en un archivo [cite: 20]
    with open(output_path, 'wb') as f:
        pickle.dump({'params': params, 'codes': huffman.reverse_mapping, 'data': byte_array}, f)

    print(f"Audio comprimido guardado en: {output_path}")

def decompress_audio(input_path, output_path):
    """
    [cite_start]Descomprime un archivo de audio y lo reconstruye a formato .wav. [cite: 20]
    """
    try:
        with open(input_path, 'rb') as f:
            data_dict = pickle.load(f)
    except Exception as e:
        print(f"Error al leer el archivo de audio comprimido: {e}")
        return
    
    params = data_dict['params']
    reverse_mapping = data_dict['codes']
    byte_array = data_dict['data']

    # Convertir el array de bytes de nuevo a un bit string
    bit_string = ""
    for byte in byte_array:
        bits = bin(byte)[2:].rjust(8, '0')
        bit_string += bits
        
    # Usar la lógica de descompresión de Huffman
    encoded_text = huffman.remove_padding(bit_string)

    # Establecer el mapa de decodificación
    huffman.reverse_mapping = reverse_mapping
    decoded_bytes_list = huffman.decode_text(encoded_text)
    
    # Convertir la lista de enteros de bytes a un objeto 'bytes'
    decoded_frames = bytes(decoded_bytes_list)
    
    # Escribir el nuevo archivo .wav reconstruido
    with wave.open(output_path, 'wb') as audio_file:
        audio_file.setparams(params)
        audio_file.writeframes(decoded_frames)

    print(f"Audio descomprimido y guardado en: {output_path}")