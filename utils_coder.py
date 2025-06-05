import numpy as np
from math import gcd
from typing import Tuple
from hashlib import pbkdf2_hmac

FREQS = np.array([
    220.00,   # Am pentatónica ampliada a 8 notas
    261.63,   
    293.66,   
    329.63,   
    392.00,   
    440.00,   
    523.25,   
    587.33,   
])

# acordes I–V–vi–IV en Cmaj
CHORD_NOTES = {
    "C":  [261.63, 659.26, 392.00],   # C4, E3, G4
    "G":  [196.00, 246.94, 392.00],   # G3, B3 (246.94), G4 (493.88)
    "Am": [220.00, 523.25, 329.63],   # A3, C4 (659.26), E4
    "F":  [174.61, 698.46, 523.25],   # F3, F4 (349.23), C5
}
PROGRESION = [
    "C","G","Am","F","C","G",
    "Am","F","C","G","Am","F","C","G","Am","F","C","G",
]


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

# FUNCIONES DE CODIFICACION

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


def crear_melodia(texto, clave, compases): # se construye la melodia del msj
    indices = txt_a_idx(texto)
    melodia = []

    for i, idx in enumerate(indices):
        freq = float(FREQS[idx])
        compas = nota_en_compas(i, clave, compases)
        melodia.append((i, freq, compas))
        
    return melodia

# funcion para mezclar con notas de relleno,
# el beat 0 -> nota msj, los demás notas del acorde arpegiadas
def mezclar_msj_arpegio(melodia: list, compases: int):

    nota_por_compas = { compas: freq for (_, freq, compas) in melodia }
    resultado = []

    for k in range(compases):
        freq_mensaje = nota_por_compas[k]
        nombre_acorde = PROGRESION[k % len(PROGRESION)]
        acorde = CHORD_NOTES[nombre_acorde]

        for beat in range(4):
            if beat == 0:
                resultado.append((k, beat, freq_mensaje, True))
            else:
                freq_arpegio = acorde[beat - 1]
                resultado.append((k, beat, float(freq_arpegio), False))

    return resultado


def imprimir_melodia(melodia): 
    print("\n melodia generada:")
    print(f"{'nota en Hz':>10} | {'compas':>6}")
    print("-" * 22)
    for i, freq, compas in melodia:
        print(f"{freq:>10.2f} | {compas:>6}")
