import numpy as np  
import librosa
import matplotlib.pyplot as plt

def fft(y, sr):
    fft_dom = np.fft.rfft(y)
    freqs_vect = np.fft.rfftfreq(len(y), d=1/sr)
    amplitudes = np.abs(fft_dom)

    plt.figure(figsize=(10, 6))
    plt.plot(freqs_vect, amplitudes)
    plt.title("FFT")
    plt.xlabel("frecuencia hz")
    plt.ylabel("amplitud")
    plt.grid(True)
    plt.show()
    return fft_dom, freqs_vect, amplitudes


def stft(y):
    D = np.abs(librosa.stft(y))
    D_db = librosa.amplitude_to_db(D, ref=np.max)

    plt.figure(figsize=(10, 6))
    librosa.display.specshow(D_db, x_axis='time', y_axis='log', sr=sr)
    plt.colorbar(format="%+2.0f dB")
    plt.title("STFT")
    plt.show()


    return D_db

# graficos del wav generado
y, sr = librosa.load('mensaje.wav', sr=None)
fft(y, sr)
stft(y)

# fft_dom = np.fft.rfft(y)  # FFT en y
# freqs_vect = np.fft.rfftfreq(len(y), d=1/sr)  #-> vector con las frecs correspondientes

# amplitudes = np.abs(fft_dom)

# D = np.abs(librosa.stft(y))
# D_db = librosa.amplitude_to_db(D, ref=np.max)#pasar amplitud a dB

# duracion_nota = 0.7
# tasa_muestreo = 44100
# paso = int(0.01 * tasa_muestreo)  #desplazar entre frames