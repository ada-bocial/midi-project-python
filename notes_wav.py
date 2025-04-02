import numpy as np
from scipy.io.wavfile import write

# Funkcja do generowania tonu sinusoidalnego
def generate_tone(frequency, duration, samplerate=44100):
    t = np.linspace(0, duration, int(samplerate * duration), endpoint=False)
    tone = np.sin(2 * np.pi * frequency * t) * 32767  # Amplituda dla 16-bitowego WAV
    return tone.astype(np.int16)

# Czestotliwosci nut w oktawach małej do trzykreslnej (C do C3)
note_frequencies = {
    "C": 130.8128, "C#": 138.5913, "D": 146.8324, "D#": 155.5635, "E": 164.8138,
    "F": 174.6141, "F#": 184.9972, "G": 195.9977, "G#": 207.6523, "A": 220.0000,
    "A#": 233.0819, "B": 246.9417,
    "C1": 261.6256, "C#1": 277.1826, "D1": 293.6648, "D#1": 311.1270, "E1": 329.6276,
    "F1": 349.2282, "F#1": 369.9944, "G1": 391.9954, "G#1": 415.3047, "A1": 440.0000,
    "A#1": 466.1638, "B1": 493.8833,
    "C2": 523.2511, "C#2": 554.3653, "D2": 587.3295, "D#2": 622.2540, "E2": 659.2551,
    "F2": 698.4565, "F#2": 739.9888, "G2": 783.9909, "G#2": 830.6094, "A2": 880.0000,
    "A#2": 932.3275, "B2": 987.7666,
    "C3": 1046.5023
}



# Parametry dźwięku
duration = 0.5  # czas trwania dźwięku (w sekundach)
samplerate = 44100  # częstotliwość próbkowania

# Tworzenie folderu "sounds" do zapisania plików
import os
if not os.path.exists('sounds'):
    os.makedirs('sounds')

# Generowanie dźwięków i zapisywanie ich do plików WAV
for note, freq in note_frequencies.items():
    tone = generate_tone(freq, duration, samplerate)
    write(f"sounds/{note}.wav", samplerate, tone)

print("Dźwięki zostały wygenerowane i zapisane w folderze 'sounds'.")
