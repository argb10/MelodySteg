# MelodySteg

Script for sending text messages via generated audio waves. It uses a steganographic encoding scheme to convert text into audio frequencies.

## How it works

1. **Text encoding**: Each character is mapped to a unique frequency.
2. **Transmission**: The application outputs a `.wav` file with the message embedded.
3. **Reception**: The receiver decodes frequencies back to text using a key (a, b) and the number of measures generated.
4. **Visualization**: Includes FFT and spectrogram plots to analyze the generated WAV. The program outputs the decoded message to the receiver.

## Python Requirements

```bash
pip install -r requirements.txt
```

## System Requirements

- **fluidsynth**: `apt-get install fluidsynth` (or equivalent)
- **SoundFont**: `apt install fluid-soundfont-gm`

## Quick Start

1. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install system dependencies**
   - On Debian/Ubuntu:
     ```bash
     sudo apt-get install fluidsynth
     sudo apt-get install fluid-soundfont-gm
     ```

3. **Encode a message into audio**
   ```bash
   python encode.py "Your secret message here"
   ```
   This will generate an output WAV file (e.g. `output.wav`).

4. **Decode a message from audio**
   ```bash
   python decode.py output.wav
   ```
   The decoded message will appear in the terminal.

5. **Visualize the audio (optional)**
   - Run the visualization tool to see a spectrogram or FFT plot:
     ```bash
     python visualize.py output.wav
     ```

For more information about key files and advanced options, see the full documentation below.