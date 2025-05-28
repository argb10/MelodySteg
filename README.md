# MelodySteg

Script que permite el envío de mensajes de texto mediante generación de ondas de audio.
Utiliza un esquema de codificación para convertir el texto en frecuencias de audio haciendo uso de un algortimo esteganográfico.

# Características


# Cómo funciona

1. Codificación de texto: cada carácter se mapea a una frecuencia única
2. Transmisión: La aplicación devuelve un fichero .wav al usuario con su mensaje integrado
3. Recepción: El receptor decodifica las frecuencias de vuelta al texto, habiendo obtenido previamente una  clave (a,b) y el numero de compases generados.
4. Visualización: Incluye gráficos y espectrograma que permiten analizar el wav generado. La salida del programa devuelve el mensaje decodificado al receptor.

# Requisitos
    
    pip install -r requirements.txt

requiere que el programa externo 'fluidsynth' esté instalado -> apt-get install fluidsynth

al igual que una soundfont ->  sudo apt install fluid-soundfont-gm
