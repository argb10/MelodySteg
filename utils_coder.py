import numpy as np
from math import gcd
from typing import Tuple
from hashlib import pbkdf2_hmac

FREQS = np.array([220.00, 261.63, 293.66, 329.63, 392.00, 440.00, 523.25, 587.33]) # Am pentatónica ampliada a 8 notas

# acordes I–V–vi–IV en Cmaj
ACORDES = { "C":  [261.63, 329.63, 392.00],   # C4, E4, G4
            "G":  [196.00, 246.94, 293.66],   # G3, B3, D4
           "Am": [220.00, 261.63, 329.63],   # A3, C4/(523.25 Hz), E4
            "F":  [174.61, 220.00, 130.81],   # F3, A3 (349.23 Hz), C3
    
}
PROGRESION = [
    "C","G","Am","F","C","G", # inicio
    "Am","F","C","G","Am","F","C","G","Am","F","C","G" #desarrollo
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
    # print(f"'{c}' -> byte: {byte:08b} -> indices: {indices}")
    return indices


def txt_a_idx(texto):
    # print(f"codificando texto...: '{texto}'")
    indices = []
    for c in texto:
        indices.extend(char_a_idx(c))
    # print(f"indices: {indices}")
    return indices


def nota_en_compas(idx, clave, compases):
    a, b = clave
    compas = (idx * a + b) % compases
    # print(f"Nota idx {idx} -> compas: {compas}")
    return compas


def crear_melodia(texto, clave, compases): # se construye la melodia del msj
    indices = txt_a_idx(texto)
    melodia = []

    for i, idx in enumerate(indices):
        freq = float(FREQS[idx])
        compas = nota_en_compas(i, clave, compases)
        melodia.append((i, freq, compas))
        
    return melodia

#se unen melodia y notas de relleno
def mel_con_padding(melodia, compases):

    nota_por_compas = {}
    for i, frec, compas in melodia:
        nota_por_compas[compas] = (i, frec)

    rdo = []

    for c in range(compases):
        i, frec_msj  = nota_por_compas[c]
        n_acorde = PROGRESION[ c % len(PROGRESION)]
        acorde = ACORDES[n_acorde]
        pos_msj = i % 4

        for beat in range(4):
            if beat == pos_msj:
                rdo.append((c, beat, frec_msj, True))
            else:
                frec_relleno = acorde[beat-1]
                rdo.append((c, beat, float(frec_relleno), False))
    return rdo



def imprimir_melodia(melodia): 
    print("\n melodia generada:")
    print(f"{'nota en Hz':>10} | {'compas':>6}")
    print("-" * 22)
    for i, freq, compas in melodia:
        print(f"{freq:>10.2f} | {compas:>6}")

#LOG pruebas
