import tkinter as tk
from mido import Message, MidiFile, MidiTrack, MetaMessage
from tkinter import filedialog, messagebox
import pygame

class PianoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Piano MIDI Creator")

        # Inicjalizacja biblioteki pygame do odtwarzania dźwięków
        pygame.mixer.init()

        # Inicjalizacja zmiennej do przechowywania aktualnie odtwarzanego dźwięku
        self.current_sound = None

        # Inicjalizacja pliku MIDI i ścieżki
        self.midi_file = MidiFile()
        self.track = MidiTrack()
        self.midi_file.tracks.append(self.track)
        self.midi_file.ticks_per_beat = 480  # Standardowa wartość podziału na 480 ticków na ćwierćnutę

        # Dodanie domyślnego tempa (120 BPM)
        self.tempo = 500000  # 120 BPM w mikrosekundach na takt
        self.track.append(MetaMessage('set_tempo', tempo=self.tempo))

        # Lista nut, które zostały dodane (z uwzględnieniem długości nut)
        self.added_notes = []

        # Klawisze pianina (od C do C2, 3 oktawy)
        self.notes = [
            ("C", 36), ("C#", 37), ("D", 38), ("D#", 39), ("E", 40), ("F", 41), ("F#", 42), ("G", 43),
            ("G#", 44), ("A", 45), ("A#", 46), ("B", 47),
            ("C1", 48), ("C#1", 49), ("D1", 50), ("D#1", 51), ("E1", 52), ("F1", 53), ("F#1", 54), ("G1", 55),
            ("G#1", 56), ("A1", 57), ("A#1", 58), ("B1", 59),
            ("C2", 60), ("C#2", 61), ("D2", 62), ("D#2", 63), ("E2", 64), ("F2", 65), ("F#2", 66), ("G2", 67),
            ("G#2", 68), ("A2", 69), ("A#2", 70), ("B2", 71), ("C3", 72)
        ]

        # Mapowanie klawiszy na nuty (klawiatura komputerowa -> nuty)
        self.key_map = {
            "z": "C", "s": "C#", "x": "D", "d": "D#", "c": "E",
            "v": "F", "g": "F#", "b": "G", "h": "G#", "n": "A",
            "j": "A#", "m": "B", ",": "C1", "l": "C#1", ".": "D1", ";": "D#1", "/": "E1",
            "q": "F1", "2": "F#1", "w": "G1", "3": "G#1", "e": "A1",
            "4": "A#1", "r": "B1", "t": "C2", "6": "C#2", "y": "D2", "7": "D#2", "u": "E2",
            "i": "F2", "9": "F#2", "o": "G2", "0": "G#2", "p": "A2",
            "-": "A#2", "[": "B2", "]": "C3"
        }

        # Ścieżka do folderu z dźwiękami
        self.sound_folder = "sounds/"

        # Podział na białe i czarne klawisze
        self.white_notes = [note for note in self.notes if "#" not in note[0]]  # Białe klawisze
        self.black_notes = [note for note in self.notes if "#" in note[0]]  # Czarne klawisze

        # Rysowanie klawiszy na ekranie
        self.white_keys = {}  # Przechowujemy białe klawisze slowniki
        self.black_keys = {}  # Przechowujemy czarne klawisze
        self.draw_piano()  # Funkcja do rysowania pianina

        # Ustawienia GUI i mapowanie klawiszy
        self.root.bind("<KeyPress>", self.on_key_press)
        self.root.bind("<KeyRelease>", self.on_key_release)

        # Kontrolka do wyboru rodzaju nuty
        self.duration_label = tk.Label(self.root, text="Note Duration:")
        self.duration_label.grid(row=1, columnspan=3)

        self.duration_var = tk.StringVar(value="Quarter")  # Domyślnie ćwierćnuta
        self.duration_menu = tk.OptionMenu(self.root, self.duration_var, "Whole", "Half Dot", "Half", "Quarter Dot", "Quarter",
                                           "Eighth Dot", "Eighth", "Sixteenth Dot", "Sixteenth")
        self.duration_menu.grid(row=1, column=3, columnspan=3)

        # Pole do wpisania tempa
        self.tempo_label = tk.Label(self.root, text="Tempo (BPM):")
        self.tempo_label.grid(row=2, column=0, columnspan=2)
        self.tempo_entry = tk.Entry(self.root, width=10)
        self.tempo_entry.insert(0, "120")  # Domyślna wartość 120 BPM
        self.tempo_entry.grid(row=2, column=2, columnspan=2)

        # Przycisk do zapisywania pliku MIDI
        save_button = tk.Button(self.root, text="Save MIDI", width=10, height=2, command=self.save_midi)
        save_button.grid(row=2, columnspan=len(self.white_notes))

        # Przycisk do wyczyszczenia nut
        clear_button = tk.Button(self.root, text="Clear", width=10, height=2, command=self.clear_notes)
        clear_button.grid(row=3, columnspan=len(self.white_notes))

        # Przycisk do cofania ostatniej nuty
        undo_button = tk.Button(self.root, text="Undo", width=10, height=2, command=self.undo_last_note)
        undo_button.grid(row=4, columnspan=len(self.white_notes))

        # Wyświetlanie zawartości dodanych nut
        self.notes_display = tk.Label(self.root, text="Added Notes: ", width=100, height=2, anchor="w", justify="left")
        self.notes_display.grid(row=5, columnspan=len(self.white_notes), sticky="nsew", padx=5, pady=5)

        # Mapowanie czasów trwania nut na wartości
        self.note_durations = {
            "Whole": 4, "Half Dot": 3, "Half": 2, "Quarter Dot": 1.5,
            "Quarter": 1, "Eighth Dot": 0.75, "Eighth": 0.5, "Sixteenth Dot": 0.375, "Sixteenth": 0.25
        }

        self.duration_names = {v: k for k, v in self.note_durations.items()}

    def draw_piano(self):
        """
        Funkcja do rysowania pianina, z uwzględnieniem białych i czarnych klawiszy.
        """
        # Rysowanie białych klawiszy
        for i, (note_name, note_value) in enumerate(self.white_notes):
            button = tk.Button(self.root, text=note_name, bg="white", fg="black", width=5, height=10, anchor="s", padx=0, pady=10,
                               command=lambda nv=note_value: self.play_and_record(nv))
            button.grid(row=0, column=i, sticky="nsew")
            self.white_keys[note_value] = button

        # Rysowanie czarnych klawiszy
        for note_name, note_value in self.black_notes:
            # Obliczanie pozycji czarnego klawisza w obrębie oktawy
            position_in_octave = self.get_black_key_position(note_name)
            if position_in_octave is not None:
                # Obliczamy przesunięcie w pikselach
                octave_index = (note_value - 36) // 12
                x_offset = (position_in_octave + octave_index * 7) * 43 - 16  # 7 białych klawiszy na oktawę
                button = tk.Button(self.root, text=note_name, bg="black", fg="white", width=3, height=5, anchor="s", padx=0, pady=5,
                                   command=lambda nv=note_value: self.play_and_record(nv))
                button.place(x=x_offset, y=0)
                self.black_keys[note_value] = button

    def get_black_key_position(self, note_name):
        """
        Funkcja mapująca czarne klawisze do ich pozycji w obrębie oktawy.
        """
        key_map = {"C#": 1, "D#": 2, "F#": 4, "G#": 5, "A#": 6}  # Pozycje między białymi klawiszami
        base_note = note_name.rstrip("0123456789")  # Usuwamy numer oktawy
        return key_map.get(base_note)

    def play_sound(self, note):
        """
        Funkcja do odtwarzania dźwięku klawisza.
        """
        note_name = next(name for name, value in self.notes if value == note)
        sound_file = f"{self.sound_folder}{note_name}.wav"  # Ścieżka do pliku dźwiękowego

        # Sprawdź, czy plik dźwiękowy istnieje
        try:
            sound = pygame.mixer.Sound(sound_file)
            sound.play(maxtime=750)
        except pygame.error:
            print(f"Sound file for {note_name} not found!")

    def stop_playing_sound(self):
        # Sprawdź, czy jakiś dźwięk jest odtwarzany i zatrzymaj go
        if self.current_sound:
            self.current_sound.stop()  # Zatrzymaj dźwięk
            self.current_sound = None  # Wyczyść zmienną przechowującą aktualny dźwięk

    def play_and_record(self, note):
        """
        Funkcja, która rejestruje naciśnięcie klawisza, odtwarza dźwięk i zapisuje do pliku MIDI.
        """
        # Pobranie wybranej długości nuty
        note_type = self.duration_var.get()
        duration_in_beats = self.note_durations.get(note_type, 1)
        note_duration_ticks = int(duration_in_beats * self.midi_file.ticks_per_beat)

        # Rejestracja nuty w MIDI
        self.track.append(Message('note_on', note=note, velocity=64, time=0))
        self.track.append(Message('note_off', note=note, velocity=64, time=note_duration_ticks))

        # Dodanie nuty do listy z rzeczywistą nazwą i czasem trwania w tickach
        note_name = next(name for name, value in self.notes if value == note)
        self.added_notes.append((note_name, note_duration_ticks))

        # Odtwarzanie dźwięku
        self.play_sound(note)

        # Aktualizacja widoku nut
        self.update_notes_display()

        # Wyróżnienie klawisza na pianinie
        self.highlight_key(note)

    def on_key_press(self, event):
        """
        Funkcja reagująca na naciśnięcie klawisza.
        """
        # Sprawdzamy, czy fokusem jest pole tekstowe (gdzie wpisujesz tempo)
        if self.root.focus_get() == self.tempo_entry:
            return  # Ignorujemy naciśnięcie klawisza, gdy wpisujesz tempo

        key = event.char
        if key in self.key_map:
            note = self.key_map[key]
            note_value = next(value for name, value in self.notes if name == note)
            self.play_and_record(note_value)

    def on_key_release(self, event):
        """
        Funkcja reagująca na puszczenie klawisza.
        """
        key = event.char
        if key in self.key_map:
            note = self.key_map[key]
            note_value = next(value for name, value in self.notes if name == note)
            self.stop_playing_sound()

    def highlight_key(self, note):
        """
        Funkcja, która wyróżnia klawisz podczas jego naciśnięcia.
        """
        if note not in self.white_keys and note not in self.black_keys:
            return
        # Białe klawisze
        if note in self.white_keys:
            button = self.white_keys[note]
            button.config(bg="yellow")  # Zmiana koloru na żółty
            self.root.after(200, lambda: button.config(bg="white"))  # Po 200 ms przywracamy oryginalny kolor
        # Czarne klawisze
        elif note in self.black_keys:
            button = self.black_keys[note]
            button.config(bg="blue")  # Zmiana koloru czarnego klawisza na niebieski
            self.root.after(200, lambda: button.config(bg="black"))  # Po 200 ms przywracamy oryginalny kolor

    def update_notes_display(self):

        # Zbudowanie tekstu do wyświetlenia
        notes_text = "Added Notes: " + " ".join([f"{note[0]}" for note in self.added_notes])
        self.notes_display.config(text=notes_text)

    def clear_notes(self):
        """
        Funkcja do czyszczenia listy dodanych nut i resetowania ścieżki MIDI.
        """
        # Czyszczenie listy nut
        self.added_notes.clear()

        # Tworzenie nowej ścieżki MIDI
        self.track = MidiTrack()
        self.midi_file.tracks = [self.track]  # Zastąp istniejące ścieżki nową
        self.track.append(MetaMessage('set_tempo', tempo=self.tempo))  # Dodanie tempa

        # Aktualizacja wyświetlania
        self.update_notes_display()

    def undo_last_note(self):
        """
        Funkcja do cofania ostatnio dodanej nuty.
        """
        if self.added_notes:
            self.added_notes.pop()
            self.update_notes_display()

    def save_midi(self):
        """
        Funkcja do zapisywania pliku MIDI, pozwalając użytkownikowi ustawić tempo.
        """
        # Pobranie tempa z pola tekstowego
        try:
            bpm = int(self.tempo_entry.get())
            if bpm <= 0:
                raise ValueError
            self.tempo = int(60000000 / bpm)  # Przekształcenie BPM na mikrosekundy na ćwierćnutę
        except ValueError:
            messagebox.showerror("Error", "Invalid tempo! Please enter a positive integer.")
            return

        # Tworzymy nowy plik MIDI
        self.midi_file = MidiFile()
        self.track = MidiTrack()
        self.midi_file.tracks.append(self.track)
        self.midi_file.ticks_per_beat = 480  # Standardowa wartość podziału na 480 ticków na ćwierćnutę
        self.track.append(MetaMessage('set_tempo', tempo=self.tempo))  # Dodanie tempa

        # Dodanie wszystkich nut do pliku MIDI
        for note, duration_ticks in self.added_notes:
            note_value = next(value for name, value in self.notes if name == note)
            self.track.append(Message('note_on', note=note_value, velocity=64, time=0))
            self.track.append(Message('note_off', note=note_value, velocity=64, time=duration_ticks))

        # Okno dialogowe do wyboru miejsca zapisu
        file_path = filedialog.asksaveasfilename(defaultextension=".mid", filetypes=[("MIDI Files", "*.mid")])
        if not file_path:
            return  # Użytkownik anulował zapis

        try:
            # Zapisanie pliku MIDI
            self.midi_file.save(file_path)
            messagebox.showinfo("Info", f"MIDI file saved: {file_path}")
        except PermissionError:
            messagebox.showerror("Error", "Permission denied. Try saving in another directory.")


if __name__ == "__main__":
    root = tk.Tk()
    app = PianoApp(root)
    root.mainloop()

