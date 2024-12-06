import csv
import numpy as np
from scipy.io.wavfile import write

class MIDIMessage():
    
    
    def __init__(self):
        self.MIDI_Port_name = 'loopMIDI Port 1'
        self.music_csv_file = "music_data.csv"
        self.audio_file = 'final_output.wav'

    def write_csv(self,conductor_spartito):
        with open(self.music_csv_file, mode="w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=["ms", "musician", "note", "dur", "amp", "bpm"])
            writer.writeheader()  # Scrive l'intestazione del CSV
            writer.writerows(conductor_spartito)  # Scrive tutte le righe

    
    # convert a MIDI note into frequency.
    def midi_to_freq(self,midi_note):
        return 440.0 * (2 ** ((midi_note - 69) / 12.0))
    
    # to generate a sinusoidal wave.
    def generate_wave(self,freq,duration, amplitude, sample_rate = 44100):
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint= False)
        wave = amplitude * np.sin(2* np.pi * freq * t)
        return wave
    
    def generate_audio_from_csv(self):
        """Genera un file audio dal file CSV con note e metronomo scandito ogni secondo."""
        sample_rate = 44100  # Sample rate in Hz
        audio_data = []

        # Leggi i dati dal file CSV
        with open(self.music_csv_file, 'r') as f:
            lines = f.readlines()

            # Variabili per tenere traccia della durata totale
            total_duration_samples = 0

            for line in lines[1:]:  
                parts = line.strip().split(',')
                try:
                    # Controlla se la riga contiene un valore di millisecondi valido
                    ms = int(parts[0]) if parts[0].isdigit() else 0

                    # Prosegui solo se ci sono informazioni valide per generare una nota
                    if len(parts) > 5 and parts[2].isdigit():
                        midi_note, duration, amplitude, bpm = map(int, (parts[2], parts[3], parts[4], parts[5]))
                        freq = self.midi_to_freq(midi_note)

                        # Durata della nota in secondi (durata specificata nel CSV)
                        duration_seconds = duration  # Durata in secondi
                        wave = self.generate_wave(freq, duration_seconds, amplitude / 127.0, sample_rate)

                        # Calcola la posizione temporale in campioni
                        start_sample = int(ms / 1000.0 * sample_rate)  # Converti ms a campioni
                        end_sample = start_sample + len(wave)

                        # Aggiorna la durata totale in campioni
                        total_duration_samples = max(total_duration_samples, end_sample)

                        # Aggiungi la wave alla posizione corretta nel file audio
                        if len(audio_data) < end_sample:
                            audio_data.extend([0] * (end_sample - len(audio_data)))  # Aggiungi silenzio se necessario

                        # Sovrapponi la wave al file audio esistente
                        for i in range(len(wave)):
                            if start_sample + i < len(audio_data):
                                audio_data[start_sample + i] += wave[i]

                except ValueError as e:
                    print(f"Errore durante l'elaborazione della riga: {line.strip()} - {e}")

        # Aggiungi il metronomo ogni secondo
        click_duration = 0.05  
        metronome_click = self.generate_metronome_click(sample_rate, click_duration, 1000, 0.2)
        metronome_interval_samples = sample_rate 

        for start_sample in range(0, total_duration_samples, metronome_interval_samples):
            end_sample = start_sample + len(metronome_click)
            if len(audio_data) < end_sample:
                audio_data.extend([0] * (end_sample - len(audio_data)))  # Aggiungi silenzio se necessario
            for i in range(len(metronome_click)):
                if start_sample + i < len(audio_data):
                    audio_data[start_sample + i] += metronome_click[i] * 0.1  # Volume ridotto del metronomo

        # Normalizzazione dell'audio
        audio_data = np.array(audio_data, dtype=float)
        audio_data = audio_data / np.max(np.abs(audio_data)) * 32767  # Normalizza

        # Scrivi il file audio
        audio = np.int16(audio_data)  # Converte l'audio normalizzato in int16
        write(self.audio_file, sample_rate, audio)
        print(f"Audio file generated: {self.audio_file}")


    def generate_metronome_click(self, sample_rate, click_duration=0.05, frequency=1000, amplitude=0.1):
        """Genera un click breve per il metronomo."""
        t = np.linspace(0, click_duration, int(sample_rate * click_duration), endpoint=False)
        click = amplitude * np.sin(2 * np.pi * frequency * t)
        return click


    def midi_event(self,filename):
        self.read_data_from_csv_and_write_music_data(filename)
        self.generate_audio_from_csv()

"""""
        # Aggiungi il metronomo
        beat_interval = 60.0 / bpm  # Intervallo di un battito in secondi
        total_duration_seconds = max_ms / 1000.0  # Durata totale dell'audio in secondi
        metronome_samples = int(sample_rate * beat_interval)

        for beat in range(0, int(total_duration_seconds / beat_interval)):
            start_sample = beat * metronome_samples
            end_sample = start_sample + len(metronome_click)
            if len(audio_data) < end_sample:
                audio_data.extend([0] * (end_sample - len(audio_data)))  # Aggiungi silenzio se necessario
            audio_data[start_sample:end_sample] += metronome_click



    def read_data_from_csv_and_write_music_data(self, filename):
        with open(filename, mode= 'r') as file:
            reader = csv.DictReader(file,delimiter = ";")
            next(reader)
            
            rows = list(reader)
            
            with open(self.music_csv_file, mode = "w", newline = "") as output_file:
                writer = csv.writer(output_file, delimiter=";")
                writer.writerow(["ms", "musician", "note", "dur", "amp", "bpm"])

                for row in rows:
                    millisecond = row["ms"]  # "ms"
                    robot_number = row["robot number"]  # "robot number"
                    playing_flag = row["is playing"]
                    
                    if playing_flag == "True":
                        note = Note()
                        writer.writerow([millisecond, robot_number, note.midinote, note.dur, note.amp, note.BPM])
                        #print("robot n.:"+str(robot_number)+" deve suonare a ms: "+str(millisecond))
    
                # Determina l'ultimo millisecondo presente nel CSV
                last_millisecond = max(int(row["ms"]) for row in rows if row["ms"].isdigit())

                # Scrivi l'ultima riga con l'ultimo millisecondo
                writer.writerow([last_millisecond, "", "", "", "", ""])
"""        