#!p/usr/bin/env python3

import argparse
import sys
import os
import re
# import IPython.display as ipd
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


def validar_entrada(entrada):
    while True:
        respuesta = input(entrada).strip()
        if respuesta.lower() == "salir":
            print("Saliendo de la aplicación...")
            sys.exit(0)
        if respuesta.isdigit():
            return int(respuesta)
        print("Entrada no válida, debe ser un entero.")


def help():
    print("""

Uso:
    python3 main.py --modo emisor/receptor

Modo emisor:
    - Introduce un mensaje desde la terminal.
    - El programa codificará el mensaje y generará 'mensaje.wav'.
    - También generará 'clave_para_receptor.txt' con los parámetros: clave(a,b) para decodificar.

Modo receptor:
    - Recibe el archivo 'mensaje.wav' y 'clave_para_receptor.txt'.
    - El programa pedirá que ingreses los valores de clave y selecciones el .WAV para decodificar el mensaje.

Requisitos:
    - Python 3
    - Instalar dependencias: pip install -r requirements.txt y una soundfont

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
python3 main.py --help muestra guía de uso
                --modo emisor/receptor
    ''')


def cargar_meta_desde_archivo(ruta: str) -> Optional[Tuple[int, int]]:
    # ahora lee numerador y compases desde claves.txt y los inserta como parametros directamente
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
    entrada = input("Escribe el mensaje a codificar: ")
    pw = input("Escribe una contraseña: ")
    print("\nElige un instrumento (0-127)")
    print("0  - Piano")
    print("46 - Guitarra acústica")  # no si >3 char

    instr = int(input("escribe el número del instrumento: "))
    if not 0 <= instr <= 127:
        print("entrada no válida, se usará Piano (0) por defecto")
        instr = 0

    compas = input("Escribe el compás (e.g. 4/4): ").strip()
    try:
        numerador = int(compas.split('/')[0])
    except:
        print("compás no válido, usando 4/4 por defecto...")
        numerador = 4

    # clave, compases = generar_clave_compas(entrada)
    clave, compases = kdf(pw, entrada)
    a, b = clave
    # esto es un log de prueba no deberia mostrarse
    print(f"\n Clave generada: a->{a}, b->{b} y compases->{compases}\n")

    melodia = crear_melodia(entrada, clave, compases)
    mel_final = mel_con_padding(melodia, compases, clave, numerador)
    exportar_melodia_a_midi(mel_final, bpm=60, instrumento=instr)
    imprimir_melodia(melodia)

    midi_a_wav("mensaje.mid", "mensaje.wav",
               "/usr/share/sounds/sf2/FluidR3_GM.sf2")

    # with open("claves.txt", "w") as f:
    # f.write(f"\n Clave generada: a->{a}, b->{b}, compás->{numerador}\n")
    with open("claves.txt", "w", encoding="utf-8") as f:
        f.write(f"datos: numerador->{numerador}, compases->{compases}\n")

    print("Archivos creados: mensaje.wav y claves.txt")
    log_dispersion(entrada, melodia, mel_final)

#     #     # buscar las frecuencias
#     # energia, _ = calcular_energia(audio, sr)
#     # picos, _  = find_peaks(energia, height=np.max(energia)*0.3, distance=int(0.4/0.01))
#     # frecs = detectar_frecs(audio, picos, duracion_nota=0.7, tasa_muestreo=sr)
#     # melodia=obtener_melodia(frecs)

#     # compases_encontrados= buscar_compases(picos, paso=int(0.01*sr), tasa_muestreo=sr, duracion_nota=0.7)
#     # compases = len(compases_encontrados)

#     msj_final = decode(clave, compases, onsets, frecs, numerador)
#     print(f"Mensaje decodificado: {msj_final}")


def receptor(ruta_claves="claves.txt"):
    print("- Receptor -")

    ruta_wav = input("Inserte la ruta del archivo .wav: ").strip()
    pw = input("Inserte la contraseña: ").strip()

    y, sr, audio = cargar_audio(ruta_wav)
    onsets, frecs = onsets_y_frecs(audio, sr)

    numerador = None
    compases = None

    if ruta_claves and os.path.exists(ruta_claves):
        # receptor carga los parametros
        meta = cargar_meta_desde_archivo(ruta_claves)
        if meta:
            numerador, compases = meta
            print(
                f"datos tomados de '{ruta_claves}': numerador={numerador}, compases={compases}")
        else:
            print(
                f"'{ruta_claves}' existe pero no se pudo parsear. Se estimará desde el audio.")
    else:
        print("No se encontró archivo .txt. estimando  datos...")

    if numerador is None or compases is None:
        #  estimar desde audio num y compases si no los da el usuario
        numerador_inf, compases_inf = estimar_metrica(onsets, sr)
        if numerador is None:
            numerador = numerador_inf
        if compases is None:
            compases = compases_inf
        print(f"Métrica estimada: numerador={numerador}, compases={compases}")

    if numerador is None:
        raise ValueError(
            "No se pudo estimar el numerador")

    compases_max = len(onsets) // numerador
    if compases is None or compases > compases_max:
        compases = compases_max

    if compases <= 0:
        raise ValueError(
            "No hay suficientes onsets para decodificar (compases <= 0).")

    clave = kdf_from_compases(pw, compases)  # derivo la clave

    msj_final = decode(clave, compases, onsets, frecs, numerador)
    print(f"\nMensaje decodificado: {msj_final}")
    return msj_final


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--modo', choices=['emisor', 'receptor'])
    parser.add_argument('--help', action='store_true')
    # NEW
    parser.add_argument(
        '--wav', help="Ruta del archivo .wav ")
    parser.add_argument('--claves', default="claves.txt",
                        help="Ruta de claves.txt")
    parser.add_argument(
        '--pw', help="Contraseña para derivar (a,b)")

    # NEW
    args = parser.parse_args()

    banner()

    if args.help:
        help()

    # si se elige el modo directamente:
    if args.modo:
        if args.modo == 'emisor':
            emisor()
        elif args.modo == 'receptor':
            # receptor(ruta_wav=args.wav, ruta_claves=args.claves,
            #          pw=args.pw)
            receptor(ruta_claves=args.claves)
        return

    while True:
        modo = input(
            "\nSelecciona un modo para continuar (emisor/receptor) o 'salir': ").strip().lower()

        if modo == 'emisor':
            emisor()
            break
        elif modo == 'receptor':
            receptor()
            break
        elif modo == "salir":
            print("Saliendo de la aplicación...")
            sys.exit(0)
        else:
            print("Entrada no válida. Escribe si eres 'emisor/receptor' o 'salir'. ")


if __name__ == "__main__":
    main()


#   print("3  - Piano eléctrico")
#   print("35 - Tuba")
#   print("42 - Viola")
