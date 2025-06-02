#!p/usr/bin/env python3


import argparse
import sys
import numpy as np
#import IPython.display as ipd

from scipy.signal import find_peaks
from utils_midi import exportar_melodia_a_midi
from utils_coder import kdf, crear_melodia, imprimir_melodia
from utils_audio import midi_a_wav
from utils_decoder import cargar_audio, calcular_energia, detectar_frecs, obtener_melodia, buscar_compases, decode


#funcion para validar clave del receptor
def validar_entrada(entrada):
    while True:
        respuesta = input(entrada).strip()
        if respuesta.lower()== "salir":
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
    - Instalar dependencias: pip install -r requirements.txt y una sounfont

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

def emisor():
    
    entrada = input("Escribe el mensaje a codificar: ")
    pw = input("Escribe tu contraseña: ")
    print("\nElige un instrumento (0-127):")
    print("0  - Piano")
    print("32 - Guitarra")
    print("46 - Pizzicato strings")
    print("69 - Oboe")
    print("123- Tweet")
    
    instr = int(input("escribe el número del instrumento: "))

    #clave, compases = generar_clave_compas(entrada)
    clave, compases = kdf(pw, entrada)
    a,b = clave
    print(f"\n Clave generada: a->{a}, b->{b} y compases->{compases}\n")

    melodia = crear_melodia(entrada, clave, compases)
    exportar_melodia_a_midi(melodia,bpm=60, instrumento=instr)

    midi_a_wav("mensaje.mid", "mensaje.wav", "/usr/share/sounds/sf2/FluidR3_GM.sf2")

    with open("claves.txt", "w") as f:
        f.write(f"\n Clave generada: a->{a}, b->{b}\n")
    
    print("Archivos creados: mensaje.wav y claves.txt")

def receptor():
    print("Clave para decodificar el mensaje")

    a =validar_entrada("Clave a: ")
    b =validar_entrada("Clave b: ")
    #compases = validar_entrada("Numero de compases: ")


    ruta = input("Ruta del archivo .wav: ").strip()

    clave = (a,b)
    y, sr, audio = cargar_audio(ruta)

        # buscar las frecuencias
    energia, _ = calcular_energia(audio, sr)
    picos, _  = find_peaks(energia, height=np.max(energia)*0.3, distance=int(0.4/0.01))
    frecs = detectar_frecs(audio, picos, duracion_nota=0.7, tasa_muestreo=sr)
    melodia=obtener_melodia(frecs)
    
    compases_encontrados= buscar_compases(picos, paso=int(0.01*sr), tasa_muestreo=sr, duracion_nota=0.7)
    compases = len(compases_encontrados)

    msj_final = decode(clave, compases, compases_encontrados, melodia)
    print(f"Mensaje decodificado: {msj_final}")


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--modo', choices=['emisor','receptor'])
    parser.add_argument('--help', action='store_true')
    args = parser.parse_args()

    banner()

    if args.help : help()

    #si se elige el modo directamente:
    if args.modo:
        if args.modo == 'emisor': emisor()
        elif args.modo == 'receptor': receptor()
        return

    while True:
        modo = input("\nSelecciona un modo para continuar (emisor/receptor) o 'salir': ").strip().lower()
        
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