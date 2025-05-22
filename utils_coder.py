import numpy as np
from math import gcd
from typing import Tuple
from hashlib import pbkdf2_hmac

FREQS = np.array([261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25])  # C4 a C5


def kdf(pw:str, txt:str) -> Tuple[Tuple[int, int], int]:
    compases = len(txt)*3
    v_aleatorio = b"melodia"
    key = pbkdf2_hmac('sha256', pw.encode(), v_aleatorio, 100_000, dklen=2)

    a = key[0]%compases #genero 'a'
    while gcd(a,compases)!= 1:
        a = (a+1) % compases or 1
        
    
    b = key[1] #genero 'b'
    clave = (a,b)
    return clave, compases

# ==== FUNCIONES DE CODIFICACION

def char_a_idx(c):
    byte = ord(c)
    indices = [(byte >> 6) & 0b111, (byte >> 3) & 0b111, byte & 0b111]
    # print(f"[char_a_idx] '{c}' -> byte: {byte:08b} -> indices: {indices}")
    return indices


def txt_a_idx(texto):
    # print(f"[txt_a_idx] codificando texto...: '{texto}'")
    indices = []
    for c in texto:
        indices.extend(char_a_idx(c))
    # print(f"[txt_a_idx] indices: {indices}")
    return indices


def nota_en_compas(idx, clave, compases):
    a, b = clave
    compas = (idx * a + b) % compases
    # print(f"[nota_en_compas] Nota idx {idx} -> Compás: {compas}")
    return compas


def crear_melodia(texto, clave, compases):
    # print(f"[generar_melodia_con_mensaje] generando melodía para: '{texto}' con clave {clave}")
    indices = txt_a_idx(texto)
    melodia = []

    for i, idx in enumerate(indices):
        freq = FREQS[idx]
        compas = nota_en_compas(i, clave, compases)
        melodia.append((i, freq, compas))
        # print(f"[generar_melodia_con_mensaje] i={i}, index={idx} -> freq={freq} Hz, compás={compas}")

    # print(f"[generar_melodia_con_mensaje] melodia creada con {len(melodia)} notas.")
    return melodia

# === VISUALIZAR 'PARTITURA'


def imprimir_melodia(melodia):
    print("\n melodia generada:")
    print(f"{'nota en Hz':>10} | {'compas':>6}")
    print("-" * 22)
    for i, freq, compas in melodia:
        print(f"{freq:>10.2f} | {compas:>6}")
