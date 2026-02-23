import librosa
import wave  # for .wav format
import numpy as np

from scipy.fft import rfft, rfftfreq
from scipy.io import wavfile
from utils.utils_coder import FREQS
from utils.utils_coder import beat_random


def cargar_audio(ruta_archivo):
    tasa_muestreo, datos = wavfile.read(ruta_archivo)
    y, sr = librosa.load(ruta_archivo, sr=None)
    print(f"Loaded: sr={sr} Hz, duration={len(y)/sr:.2f} s")

    if len(datos.shape) == 2:
        datos = datos[:, 0]

    audio = datos.astype(np.float32) / \
        np.max(np.abs(datos))  # normalizar los datos

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

    if dif[indice] <= tolerancia:  # si encuentra frec...
        return indice
    else:
        return None


def inverso(a, m):
    """Modular multiplicative inverse of a mod m."""
    for x in range(1, m):
        if (a * x) % m == 1:
            return x
    raise ValueError(f"no se encontró el inverso mod")


def recuperar_msg_con_indx(indx_ordenados):
  # reordenar los idx
    def indices_a_char(i1, i2, i3):
        byte = (i1 << 6) | (i2 << 3) | i3
        return chr(byte)

    chars = []
    # print(f"\nidx recibidos: {indx_ordenados}")

    for i in range(0, len(indx_ordenados), 3):
        grupo = indx_ordenados[i:i+3]  # agrupo en 3
        if len(grupo) == 3:
            c = indices_a_char(*grupo)
            print(f"group {grupo} → '{c}'")
            chars.append(c)

    return "".join(chars)


# funcion para encontrar onsets y extraer frec dominante

def onsets_y_frecs(audio, sr, muestra=0.4):
    y_librosa = librosa.util.normalize(audio)
    onsets = librosa.onset.onset_detect(
        y=y_librosa, sr=sr, units='samples', backtrack=False)

    frecs_encontradas = []
    for onset in onsets:  # por cada nota, extrae la frec
        inicio = int(onset)
        fin = int(min(len(audio), onset + muestra * sr))
        segmento = audio[inicio:fin]
        if len(segmento) == 0:
            frecs_encontradas.append(0.0)
            continue
        hann = segmento * np.hanning(len(segmento))
        espec = np.abs(rfft(hann))
        freqs = rfftfreq(len(hann), 1 / sr)
        fdom = freqs[np.argmax(espec)]
        frecs_encontradas.append(fdom)

    return onsets, frecs_encontradas

# NEW


def estimar_metrica(onsets, sr, min_numerador=2, max_numerador=12):
    """Intenta inferir el numerador y compases en total(tiempos por compás) desde el patrón de duraciones. Y dev numerador y compases. 
    """
    if onsets is None or len(onsets) < 6:
        return None, None

    try:
        onsets = np.asarray(onsets, dtype=np.float64)
    except Exception:
        return None, None

    # diferencias entre inicios de notas (duracion aprox de cada nota)
    dt = np.diff(onsets) / float(sr)
    if dt.size < 5:
        return None, None

    # filtrar valores absurdos para robustez
    dt = dt[(dt > 0.05) & (dt < 1.5)]
    if dt.size < 5:
        return None, None

    dt_sorted = np.sort(dt)
    gaps = np.diff(dt_sorted)
    if gaps.size == 0:
        return None, None

    idx = int(np.argmax(gaps))
    if gaps[idx] < 0.06:
        return None, None

    umbral = float((dt_sorted[idx] + dt_sorted[idx + 1]) / 2.0)
    notas_largas = int(np.sum(dt > umbral))
    total_notas = int(dt.size)

    if notas_largas <= 0:
        return None, None

    ratio = total_notas / float(notas_largas)
    numerador = int(np.rint(ratio))
    if numerador < min_numerador or numerador > max_numerador:
        return None, None

    if abs(ratio - numerador) > 0.25:
        return None, None

    compases = notas_largas
    return numerador, compases

# NEW


def decode(clave, compases, onsets, frecs_encontradas, numerador):
    a, b = clave
    a_inv = inverso(a, compases)

    orden = np.argsort(onsets)
    # onsets_ord= np.array(onsets)[orden][:compases * numerador]
    # se guardan las frec necesarias
    frecs_ord = np.array(frecs_encontradas)[orden][:compases*numerador]

    idx_msj = []

    for c in range(compases):

        segmento = frecs_ord[c*numerador: (c+1)*numerador]

        i_original = (a_inv * (c-b)) % compases
        beat_msj = beat_random(
            i_original, clave, numerador)  # posicion nota_msj
        f_msj = segmento[beat_msj]
        idx = frec_a_indx(f_msj)
        if idx is not None:
            idx_msj.append((i_original, idx))

    idx_msj.sort(key=lambda x: x[0])
    indx_ordenados = [idx for (_, idx) in idx_msj]

    return recuperar_msg_con_indx(indx_ordenados)
