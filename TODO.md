# TODO – Future work

Items below were removed during repo cleanup but are relevant for future work. Code or logic is preserved here for reference.

---

## 1. Coder – Alternative FREQS and chord progressions

**Location:** `utils/utils_coder.py`

- **9-note FREQS** (instead of current 8): A3, B3, C4, D4, E4, F4, G4, A4. Allows different encoding density.
- **PROGRESION variants:** e.g. I–V–vi–IV, or vi–IV–I–V repeated. Currently using `["C", "G", "Am", "F", "C"]`.

```python
# Alternative 9-note set (commented out):
# FREQS = np.array([
#     220.00,  # A3
#     246.94,  # B3
#     261.63,  # C4
#     293.66,  # D4
#     329.63,  # E4
#     349.23,  # F4
#     392.00,  # G4
#     440.00,  # A4
# ])
# PROGRESION variants: "G", or "Am","F","C","G","Am","F","C","G" (vi-IV-I-V x3)
```

---

## 2. MIDI export – Alternative implementations (two-track, timing options)

**Location:** `utils/utils_midi.py`

Two experimental versions of `exportar_melodia_a_midi` were removed. Reintroduce as optional codepaths or refactor into one configurable function.

**Variant A (experiment v1):**
- Conductor track (tempo + time signature).
- Track 1: melody (message + padding); message notes ~0.7×step, padding ~0.55×step.
- Track 2 (optional): bass voice, one long note per measure (root of chord, one octave down).
- Params: `numerador`, `segunda_voz=True`, `instrumento_bajo`, `vel_bajo=45`, `step_div=2` (2=corchea, 1=negra, 4=semicorchea).
- `ticks_per_beat=480`, step = `tpb // step_div`.

**Variant B:**
- `ticks_per_beat=240`.
- Track 1: melody with configurable durations: `dur_msg_beats=0.6`, `dur_fill_beats=0.5`.
- Track 2: bass, `dur_bajo_beats=None` (full measure).
- Events written with delta times (note_on time=delta, note_off time=duration).

**Current implementation** is the single-track, fixed-duration one (message 210 ticks, padding 100 ticks, closing chord). Consider unifying with the above via a single function with optional args.

---

## 3. Decoder – Energy-based and legacy onset/freq pipeline

**Location:** `utils/utils_decoder.py`

**3.1 `calcular_energia(audio, tasa_muestreo)`**  
Still present in file as commented-out; could be used for alternative onset/segment detection.

```python
def calcular_energia(audio, tasa_muestreo):
    ventana = int(0.05 * tasa_muestreo)
    paso = int(0.01 * tasa_muestreo)
    energia = [np.sum(audio[i:i+ventana]**2) for i in range(0, len(audio)-ventana, paso)]
    tiempos = np.arange(len(energia)) * paso / tasa_muestreo
    return energia, tiempos
```

**3.2 Legacy decode pipeline (removed):**
- **buscar_frecs(audio, picos, duracion_nota, tasa_muestreo):** from each peak, take a segment of length `duracion_nota * sr`, apply Hann window, FFT, take dominant frequency. `duracion_nota` must match encoder (e.g. 0.7 s).
- **obtener_melodia(frecs_encontradas):** filter freqs > 30 Hz, map to FREQS index via `frec_a_indx`, return list of indices.
- **buscar_compases(picos, paso, tasa_muestreo, duracion_nota):** map each peak time to a measure index: `compas = int((pico * paso) / tasa_muestreo // duracion_nota)`.

This pipeline was an alternative to the current one (librosa onsets + per-onset FFT). Useful if we want energy/peak-based decoding or A/B comparison.

**3.3 Debug / inspection (removed):**  
Optional prints for WAV metadata: frame rate, sample width, number of frames, params, channels, duration, number of samples. Can be re-added behind a `--verbose` or debug flag.

---

## 4. Emisor (melodySteg.py) – Optional behaviour

- **Instruments:** Extra presets were listed (e.g. 3 – Electric piano, 35 – Tuba, 42 – Viola). Could be restored in the instrument menu.
- **claves.txt format:** An alternative format was `Clave generada: a->..., b->..., compás->...`. Current format is `datos: numerador->..., compases->...`. If a different key format is needed for compatibility or docs, support both or document migration.
- **Export experiments:** Emisor had commented calls to `exportar_melodia_a_midi(..., numerador=numerador, segunda_voz=True)` and `step_div=2, segunda_voz=True`. Re-enable once the MIDI variants in §2 are available.

---

## 5. Receiver – CLI args

`--wav` and `--pw` are now used when provided (no prompt). Any further receiver improvements (e.g. `--verbose` for decode steps, or optional key file format) can be added here.

---

## Summary

| Area        | Item                                      | Action |
|------------|-------------------------------------------|--------|
| Coder      | 9-note FREQS, PROGRESION variants         | Optional constants / config |
| MIDI       | Two-track export, configurable durations  | New/refactored export path |
| Decoder    | `calcular_energia`, buscar_frecs, obtener_melodia, buscar_compases | Alternative pipeline or debug |
| Emisor     | More instruments, alternative claves format, export experiments | Menu + config |
| Receiver   | Verbose / debug output                    | Optional flag |
