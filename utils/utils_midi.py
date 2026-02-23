from mido import MidiFile, MidiTrack, Message, MetaMessage, bpm2tempo
from math import log2

PROGRESION = ["C", "G", "Am", "F", "C"]
ACORDES = {"C":  [261.63, 329.63, 392.00],
           "G":  [196.00, 246.94, 293.66],
           "Am": [220.00, 261.63, 329.63],
           "F":  [174.61, 220.00, 130.81],
           }


def frec_a_midi(frec):
    """Convert frequency to nearest MIDI note (440 Hz = A4 = 69)."""
    return int(round(69 + 12 * log2(frec / 440.0)))


def _events_to_track(track: MidiTrack, events):
    """Sort and write (t_abs, kind, note, vel) events to track; kind is 'on' or 'off'."""
    def key(e):
        t, kind, note, vel = e
        pri = 0 if kind == "off" else 1
        return (t, pri, note)

    events.sort(key=key)
    last_t = 0
    for (t, kind, note, vel) in events:
        delta = t - last_t
        if kind == "on":
            track.append(Message("note_on", note=note, velocity=vel, time=delta))
        else:
            track.append(Message("note_off", note=note, velocity=vel, time=delta))
        last_t = t


def exportar_melodia_a_midi(melodia, nombre_archivo="mensaje.mid", bpm=60, instrumento=0):
    mid = MidiFile(ticks_per_beat=480)
    track = MidiTrack()
    mid.tracks.append(track)

    track.append(Message('program_change', program=instrumento, time=0))
    track.append(MetaMessage('set_tempo', tempo=bpm2tempo(bpm), time=0))

    mel_orden = sorted(melodia, key=lambda x: (x[0], x[1]))

    for (compas, beat, frec, es_msj) in mel_orden:
        nota_midi = frec_a_midi(frec)
        if es_msj:
            duration_ticks = 210
            velocity = 60
        else:
            duration_ticks = 100
            velocity = 70

        track.append(Message('note_on', note=nota_midi, velocity=velocity, time=0))
        track.append(Message('note_off', note=nota_midi, velocity=velocity, time=duration_ticks))

    # Closing chord (tonic)
    cierre = [60, 64, 48]   # C4, E4, C3
    for nota in cierre:
        track.append(Message('note_on', note=nota, velocity=80, time=0))
    track.append(Message('note_off', note=cierre[0], velocity=70, time=240))
    track.append(Message('note_off', note=cierre[1], velocity=80, time=240))
    track.append(Message('note_off', note=cierre[2], velocity=80, time=240))

    mid.save(nombre_archivo)
