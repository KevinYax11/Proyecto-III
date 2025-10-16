# compression_logic/huffman.py

import heapq
import os
import pickle

# Clase para representar un nodo en el árbol de Huffman
class HuffmanNode:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    # Comparador para que el min-heap funcione correctamente
    def __lt__(self, other):
        return self.freq < other.freq

# Diccionario para guardar los códigos de Huffman generados
codes = {}
# Diccionario inverso para la descompresión
reverse_mapping = {}

# --- Funciones auxiliares para la compresión ---

def make_frequency_dict(text):
    """Calcula la frecuencia de cada caracter en el texto."""
    frequency = {}
    for char in text:
        if not char in frequency:
            frequency[char] = 0
        frequency[char] += 1
    return frequency

def make_heap(frequency):
    """Crea un min-heap (cola de prioridad) con los nodos de Huffman."""
    heap = []
    for key in frequency:
        node = HuffmanNode(key, frequency[key])
        heapq.heappush(heap, node)
    return heap

def merge_nodes(heap):
    """Construye el árbol de Huffman combinando los nodos de menor frecuencia."""
    while len(heap) > 1:
        node1 = heapq.heappop(heap)
        node2 = heapq.heappop(heap)
        merged = HuffmanNode(None, node1.freq + node2.freq)
        merged.left = node1
        merged.right = node2
        heapq.heappush(heap, merged)
    return heap[0] # El último nodo es la raíz del árbol

def make_codes_helper(root, current_code):
    """Función recursiva para generar los códigos a partir del árbol."""
    if root is None:
        return
    if root.char is not None:
        codes[root.char] = current_code
        reverse_mapping[current_code] = root.char
        return
    make_codes_helper(root.left, current_code + "0")
    make_codes_helper(root.right, current_code + "1")

def make_codes(root):
    """Inicia la generación de códigos."""
    make_codes_helper(root, "")

def get_encoded_text(text):
    """Codifica el texto completo usando el diccionario de códigos."""
    encoded_text = ""
    for character in text:
        encoded_text += codes[character]
    return encoded_text

def pad_encoded_text(encoded_text):
    """Añade padding al final del bitstring para que su longitud sea múltiplo de 8."""
    extra_padding = 8 - len(encoded_text) % 8
    for i in range(extra_padding):
        encoded_text += "0"
    padded_info = "{0:08b}".format(extra_padding)
    encoded_text = padded_info + encoded_text
    return encoded_text

def get_byte_array(padded_encoded_text):
    """Convierte el bitstring en un array de bytes."""
    if len(padded_encoded_text) % 8 != 0:
        print("El texto codificado no está bien rellenado")
        exit(0)
    b = bytearray()
    for i in range(0, len(padded_encoded_text), 8):
        byte = padded_encoded_text[i:i+8]
        b.append(int(byte, 2))
    return b

# --- Funciones Principales de Compresión y Descompresión ---

def compress(input_path, output_path):
    """
    [cite_start]Función principal para comprimir un archivo de texto. [cite: 8, 10]
    """
    global codes, reverse_mapping
    codes = {}
    reverse_mapping = {}

    with open(input_path, 'r', encoding='utf-8') as file:
        text = file.read()

    frequency = make_frequency_dict(text)
    heap = make_heap(frequency)
    root = merge_nodes(heap)
    make_codes(root)
    
    encoded_text = get_encoded_text(text)
    padded_encoded_text = pad_encoded_text(encoded_text)
    byte_array = get_byte_array(padded_encoded_text)

    # Guardar el árbol de Huffman (o el mapa de códigos) y los bytes comprimidos
    with open(output_path, 'wb') as output_file:
        pickle.dump((reverse_mapping, byte_array), output_file) # Guardamos el mapa inverso para facilitar la descompresión

    [cite_start]print(f"Archivo comprimido guardado en: {output_path}") # [cite: 11]

def remove_padding(padded_encoded_text):
    """Elimina el padding del bitstring descomprimido."""
    padded_info = padded_encoded_text[:8]
    extra_padding = int(padded_info, 2)
    padded_encoded_text = padded_encoded_text[8:]
    encoded_text = padded_encoded_text[:-extra_padding]
    return encoded_text

def decode_text(encoded_text):
    """Decodifica el bitstring al texto original usando el mapa inverso."""
    current_code = ""
    decoded_text = ""
    for bit in encoded_text:
        current_code += bit
        if current_code in reverse_mapping:
            character = reverse_mapping[current_code]
            decoded_text += character
            current_code = ""
    return decoded_text

def decompress(input_path, output_path):
    """
    Función principal para descomprimir un archivo.
    """
    global reverse_mapping

    with open(input_path, 'rb') as file:
        reverse_mapping, byte_array = pickle.load(file)

    bit_string = ""
    for byte in byte_array:
        bits = bin(byte)[2:].rjust(8, '0')
        bit_string += bits
    
    encoded_text = remove_padding(bit_string)
    decompressed_text = decode_text(encoded_text)

    with open(output_path, 'w', encoding='utf-8') as output_file:
        output_file.write(decompressed_text)

    print(f"Archivo descomprimido guardado en: {output_path}")