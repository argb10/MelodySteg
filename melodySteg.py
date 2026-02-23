#!/usr/bin/env python3
import argparse
import sys
import os
import re
from typing import Optional, Tuple
from utils.utils_coder import kdf_from_compases
from utils.utils_midi import exportar_melodia_a_midi
from utils.utils_coder import (
    kdf,
    crear_melodia,
    imprimir_melodia,
    mel_con_padding,
    log_dispersion
)
from utils.utils_audio import midi_a_wav
from utils.utils_decoder import cargar_audio, onsets_y_frecs, estimar_metrica, decode


def validar_entrada(prompt: str) -> int:
    while True:
        respuesta = input(prompt).strip()
        if respuesta.lower() == "exit":
            print("Exiting...")
            sys.exit(0)
        if respuesta.isdigit():
            return int(respuesta)
        print("Invalid input; enter an integer.")


def print_help():
    print("""
Usage:
    python melodySteg.py --modo sender/receiver

Sender mode:
    - Enter a message at the prompt.
    - The program encodes the message and generates 'mensaje.wav'.
    - It also generates 'claves.txt' with parameters needed to decode (numerator, measures).

Receiver mode:
    - Provide the 'mensaje.wav' file and 'claves.txt'.
    - Enter the WAV path and password when prompted to decode the message.

Requirements:
    - Python 3
    - Dependencies: pip install -r requirements.txt and a SoundFont
""")


def banner():
    print(r'''
___  ___     _           _       _____ _             
|  \/  |    | |         | |     /  ___| |            
| .  . | ___| | ___   __| |_   _\ `--.| |_ ___  __ _ 
| |\/| |/ _ \ |/ _ \ / _` | | | |`--. \ __/ _ \/ _` |
| |  | |  __/ | (_) | (_| | |_| /\__/ / ||  __/ (_| |
\_|  |_/\___|_|\___/ \__,_|\__, \____/ \__\___|\__, |
                            __/ |               __/ |
                           |___/               |___/
Hide messages using audio
  python melodySteg.py --help  |  --modo sender/receiver
''')


def cargar_meta_desde_archivo(ruta: str) -> Optional[Tuple[int, int]]:
    """Read numerator and measures from keys file (e.g. claves.txt)."""
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            contenido = f.read()
    except FileNotFoundError:
        return None

    m = re.search(
        r"numerador\s*->\s*(\d+).*?compases\s*->\s*(\d+)",
        contenido,
        flags=re.IGNORECASE | re.DOTALL
    )
    if not m:
        return None

    numerador = int(m.group(1))
    compases = int(m.group(2))
    return numerador, compases


def emisor():
    entrada = input("Enter message to encode: ")
    pw = input("Enter password: ")
    print("\nChoose instrument (0-127)")
    print("0  - Piano")
    print("46 - Acoustic guitar")

    try:
        instr = int(input("Enter instrument number: "))
    except ValueError:
        instr = 0
    if not 0 <= instr <= 127:
        print("Invalid input; using Piano (0).")
        instr = 0

    compas = input("Enter time signature numerator (e.g. 4 for 4/4): ").strip()
    try:
        numerador = int(compas.split('/')[0])
    except (ValueError, IndexError):
        print("Invalid time signature; using 4/4.")
        numerador = 4

    clave, compases = kdf(pw, entrada)
    a, b = clave
    print(f"\nKey: a->{a}, b->{b}, measures->{compases}\n")

    melodia = crear_melodia(entrada, clave, compases)
    mel_final = mel_con_padding(melodia, compases, clave, numerador)
    exportar_melodia_a_midi(mel_final, bpm=60, instrumento=instr)
    imprimir_melodia(melodia)

    midi_a_wav("mensaje.mid", "mensaje.wav",
               "/usr/share/sounds/sf2/FluidR3_GM.sf2")

    with open("claves.txt", "w", encoding="utf-8") as f:
        f.write(f"datos: numerador->{numerador}, compases->{compases}\n")

    print("Created: mensaje.wav, claves.txt")
    log_dispersion(entrada, melodia, mel_final)




def receptor(ruta_claves: str = "claves.txt", ruta_wav: Optional[str] = None, pw: Optional[str] = None):
    print("- Receiver -")
    if ruta_wav is None:
        ruta_wav = input("Enter path to .wav file: ").strip()
    if pw is None:
        pw = input("Enter password: ").strip()

    y, sr, audio = cargar_audio(ruta_wav)
    onsets, frecs = onsets_y_frecs(audio, sr)

    numerador = None
    compases = None

    if ruta_claves and os.path.exists(ruta_claves):
        meta = cargar_meta_desde_archivo(ruta_claves)
        if meta:
            numerador, compases = meta
            print(f"Loaded from '{ruta_claves}': numerator={numerador}, measures={compases}")
        else:
            print(f"'{ruta_claves}' could not be parsed. Estimating from audio.")
    else:
        print("No keys file found. Estimating parameters...")

    if numerador is None or compases is None:
        numerador_inf, compases_inf = estimar_metrica(onsets, sr)
        if numerador is None:
            numerador = numerador_inf
        if compases is None:
            compases = compases_inf
        print(f"Estimated: numerator={numerador}, measures={compases}")

    if numerador is None:
        raise ValueError("Could not estimate numerator")

    compases_max = len(onsets) // numerador
    if compases is None or compases > compases_max:
        compases = compases_max

    if compases <= 0:
        raise ValueError("Not enough onsets")

    clave = kdf_from_compases(pw, compases)

    msj_final = decode(clave, compases, onsets, frecs, numerador)
    print(f"\nDecoded message: {msj_final}")
    return msj_final


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--modo', choices=['sender', 'receiver'])
    parser.add_argument('--help', action='store_true')
    parser.add_argument('--wav', help="Path to .wav file")
    parser.add_argument('--claves', default="claves.txt", help="Path to claves.txt")
    parser.add_argument('--pw', help="Password for key derivation (a,b)")

    args = parser.parse_args()

    banner()

    if args.help:
        print_help()
        return

    if args.modo:
        if args.modo == 'sender':
            emisor()
        elif args.modo == 'receiver':
            receptor(ruta_claves=args.claves, ruta_wav=args.wav, pw=args.pw)
        return

    while True:
        modo = input("\nSelect mode (sender/receiver) or 'exit': ").strip().lower()
        if modo == 'sender':
            emisor()
            break
        elif modo == 'receiver':
            receptor(ruta_claves=args.claves)
            break
        elif modo == "exit":
            print("Exiting...")
            sys.exit(0)
        else:
            print("Invalid input. Enter 'sender', 'receiver', or 'exit'.")


if __name__ == "__main__":
    main()
