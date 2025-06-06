from scipy.fft import rfft, rfftfreq
from scipy.io import wavfile
from utils_coder import FREQS
import numpy as np
import librosa
import wave # for .wav format
from utils_coder import beat_random

#file = wave.open("mensaje.wav", "r") # rb = read binary
def cargar_audio(ruta_archivo):
    tasa_muestreo, datos = wavfile.read(ruta_archivo)
    y, sr = librosa.load(ruta_archivo, sr=None)
    print(f"archivo subido con sr: {sr} Hz,\nduracion: {len(y)/sr:.2f} s")

    if len(datos.shape) == 2:
        datos = datos[:, 0]

    audio = datos.astype(np.float32) / np.max(np.abs(datos)) # normalizar los datos
    
    return y, sr, audio

# FUNCIONES DECODIFICACION 
'''def calcular_energia(audio, tasa_muestreo): 
    ventana = int(0.05 * tasa_muestreo)
    paso = int(0.01 * tasa_muestreo)

    energia = [np.sum(audio[i:i+ventana]**2) for i in range(0, len(audio)-ventana, paso)] # energia en cada 'ventana'
    tiempos = np.arange(len(energia)) * paso / tasa_muestreo
    return energia, tiempos # tiempos correspondientes a cada punto de energía
'''

def frec_a_indx(f, tolerancia=5.0):
    dif = np.abs(FREQS - f)
    indice = np.argmin(dif)

    if dif[indice] <= tolerancia:#si encuentra frec...
        return indice
    else:
        return None

def inverso(a, m):
#buscar el 'i' con el q se codificó la nota original
    for x in range(1, m):
        if (a * x) % m == 1:
            return x
    raise ValueError(f"no se encontró el inverso mod")

def recuperar_msg_con_indx(indices_ordenados):
  #reordenar los idx
    def indices_a_char(i1, i2, i3):
        byte = (i1 << 6) | (i2 << 3) | i3
        return chr(byte)

    chars = []
    #print(f"\nidx recibidos: {indices_ordenados}")

    for i in range(0, len(indices_ordenados), 3):
        grupo = indices_ordenados[i:i+3] #agrupo en 3
        if len(grupo) == 3:
            c = indices_a_char(*grupo)
            print(f"grupo {grupo} → '{c}'")
            chars.append(c)

    return "".join(chars)


# funcion para encontrar onsets y extraer frec dominante

def onsets_y_frecs(audio, sr, duracion_segmento=0.4):
    y_librosa = librosa.util.normalize(audio)
    onset_samples = librosa.onset.onset_detect(y=y_librosa, sr=sr, units='samples', backtrack=False)

    frecs_detectadas = []
    for onset in onset_samples:
        inicio = int(onset)
        fin = int(min(len(audio), onset + duracion_segmento * sr))
        segmento = audio[inicio:fin]
        if len(segmento) == 0:
            frecs_detectadas.append(0.0)
            continue
        ventana_hann = segmento * np.hanning(len(segmento))
        espec = np.abs(rfft(ventana_hann))
        freqs = rfftfreq(len(ventana_hann), 1 / sr)
        fdom = freqs[np.argmax(espec)]
        frecs_detectadas.append(fdom)

    return onset_samples, frecs_detectadas



def decode(clave, compases, onsets, frecs_encontradas):
    a, b = clave
    a_inv = inverso(a, compases)

    orden = np.argsort(onsets)
    onsets_ord = np.array(onsets)[orden]
    frecs_ord = np.array(frecs_encontradas)[orden]

    total_onsets = compases * 4
    onsets_ord = onsets_ord[:total_onsets]
    frecs_ord = frecs_ord[:total_onsets]

    #idx por idx original
    lista_idx_i_original = []

    for c in range (compases):
        ini = c * 4
        fin = ini + 4
        frecs_compas = frecs_ord[ini:fin]

        idx_original =  (a_inv *(c-b)) %compases
        beat_esperado = beat_random(idx_original, clave)
        fdom = frecs_compas[beat_esperado]
        idx = frec_a_indx(fdom)
        if idx is not None:
            lista_idx_i_original.append((idx_original, idx))

    lista_idx_i_original.sort(key=lambda x: x[0])
    indices_ordenados = [idx for (_, idx) in lista_idx_i_original]
    return recuperar_msg_con_indx(indices_ordenados)










'''
def buscar_frecs(audio, picos, duracion_nota, tasa_muestreo):
    # busca las frec dominantes 
    samples_nota = int(duracion_nota * tasa_muestreo)
    frecs_encontradas = []

    for pico in picos:
        inicio = pico * int(0.01 * tasa_muestreo)
        fin = inicio + samples_nota
        if fin > len(audio):
            continue
        segmento = audio[inicio:fin]
        señal = segmento * np.hanning(len(segmento))  # Hann ventana
        espectro = np.abs(rfft(señal))
        freqs = rfftfreq(len(señal), 1 / tasa_muestreo)
        freq_dominante = freqs[np.argmax(espectro)]
        frecs_encontradas.append(freq_dominante)

    return frecs_encontradas

def obtener_melodia(frecs_encontradas):
    frecs_filtradas = [] 
    for f in frecs_encontradas:
        if abs(f ) > 30:
            frecs_filtradas.append(f)

    melodia_detectada = []

    for f in frecs_filtradas:
        idx = frec_a_indx(f) # mapeo los indices con las freqs encontradas

        if idx is not None:
            melodia_detectada.append(idx)

    return melodia_detectada

# Este bloque detecta el compás estimado por cada nota detectada
# Basado en su tiempo de aparición en el audio

# duración_nota debe ser la misma que se usó al codificar (0.7 s)
def buscar_compases(picos, paso, tasa_muestreo, duracion_nota):
    compases_detectados = []
    for pico in picos:
        pico_a_seg = (pico *paso)/tasa_muestreo
        compas = int(pico_a_seg // duracion_nota)
        compases_detectados.append(compas)
    
    return compases_detectados


# print("compases detectados desde los picos : ", compases_detectados)
'''
# print("frame rate:", file.getframerate())  # 44100
# print("sample width:", file.getsampwidth()) # 2
# print("number of frames:", file.getnframes())
# print("parametros:", file.getparams())
# print("numero de canales:", file.getnchannels()) # 2

# duracion = file.getnframes()/ file.getframerate() # duracion audio en seg
# print("Duracion:", duracion)

# frames = file.readframes(-1)
# print("muestras:",len(frames))
