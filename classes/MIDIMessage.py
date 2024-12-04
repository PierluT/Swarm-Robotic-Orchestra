import csv
import numpy as np
from scipy.io.wavfile import write
from moviepy import AudioFileClip,VideoFileClip
from classes.tempo import Note
class MIDIMessage():
    
    def __init__(self):
        self.MIDI_Port_name = 'loopMIDI Port 1'
        self.music_csv_file = "music_data.csv"
        self.audio_file = 'final_output.wav'

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
    
    # convert a MIDI note into frequency.
    def midi_to_freq(self,midi_note):
        return 440.0 * (2 ** ((midi_note - 69) / 12.0))
    
    # to generate a sinusoidal wave.
    def generate_wave(self,freq,duration, amplitude, sample_rate = 44100):
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint= False)
        wave = amplitude * np.sin(2* np.pi * freq * t)
        return wave
    
    def generate_audio_from_csv(self):
        """Genera un file audio dal file CSV con note suonate nella sequenza corretta e per la loro durata specifica."""
        sample_rate = 44100  # Sample rate in Hz
        audio_data = []

        # Leggi i dati dal file CSV
        with open(self.music_csv_file, 'r') as f:
            lines = f.readlines()
            max_ms = 0  # Per tracciare il massimo valore di millisecondi

            for line in lines[1:]:  # Salta la prima riga (intestazione)
                parts = line.strip().split(';')
                try:
                    # Controlla se la riga contiene un valore di millisecondi valido
                    ms = int(parts[0]) if parts[0].isdigit() else 0
                    max_ms = max(max_ms, ms)  # Aggiorna il massimo valore di millisecondi

                    # Prosegui solo se ci sono informazioni valide per generare una nota
                    if len(parts) > 2 and parts[2].isdigit():
                        midi_note, duration, amplitude = map(int, (parts[2], parts[3], parts[4]))
                        freq = self.midi_to_freq(midi_note)

                        # Durata della nota in secondi (durata specificata nel CSV)
                        duration_seconds = duration  # Ad esempio, 1 secondo
                        wave = self.generate_wave(freq, duration_seconds, amplitude / 127.0, sample_rate)

                        # Calcola la posizione temporale in campioni
                        start_sample = int(ms / 1000.0 * sample_rate)  # Converti ms a campioni

                        # Aggiungi la wave alla posizione corretta nel file audio
                        end_sample = start_sample + len(wave)
                        if len(audio_data) < end_sample:
                            audio_data.extend([0] * (end_sample - len(audio_data)))  # Aggiungi silenzio se necessario

                        # Sovrapponi la wave al file audio esistente
                        audio_data[start_sample:end_sample] += wave

                except ValueError as e:
                    print(f"Errore durante l'elaborazione della riga: {line.strip()} - {e}")

        # Converti l'audio in formato int16 per la scrittura nel file
        audio = np.int16(np.array(audio_data) / np.max(np.abs(audio_data)) * 32767)  # Normalizza

        # Scrivi il file audio
        write(self.audio_file, sample_rate, audio)
        print(f"Audio file generated: {self.audio_file}")

    def midi_event(self,filename):
        self.read_data_from_csv_and_write_music_data(filename)
        self.generate_audio_from_csv()


        