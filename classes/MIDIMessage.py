import csv
import numpy as np
from scipy.io.wavfile import write
#import fluidsynth
from mido import Message, MidiFile, MidiTrack, bpm2tempo
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
            for line in lines[1:]:  # Salta la prima riga (intestazione)
                parts = line.strip().split(';')
                try:
                    ms, robot_id, midi_note, duration, amplitude, _ = map(int, parts)
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

    def convert_csv_to_midi(self):
        midi = MidiFile()
        track = MidiTrack()
        midi.tracks.append(track)

        previous_time_us = 0

        with open(self.music_csv_file, 'r') as f:
            reading_music_data = csv.DictReader(f, delimiter=";")
            for row in reading_music_data:
                # Leggi i valori dal CSV
                time_ms = int(row['ms'])
                time_us = time_ms * 1000  # Conversione millisecondi in microsecondi
                note = int(row['note'])
                duration_ms = int(row['dur'])
                duration_us = duration_ms * 1000  # Conversione millisecondi in microsecondi
                amplitude = int(float(row['amp']) * 127)  # Amplitude scalata a valori MIDI (0-127)
                bpm = int(row['bpm'])

                # Calcolo del tempo MIDI
                ppq = 480  # Pulses per Quarter Note
                tempo = bpm2tempo(bpm)  # Tempo in microsecondi per quarter note
                microseconds_per_tick = tempo / ppq  # Microsecondi per tick
                ticks_per_second = int(1_000_000 / microseconds_per_tick)

                # Delta time in tick (tra questo evento e il precedente)
                delta_time_us = time_us - previous_time_us
                delta_time_ticks = int(delta_time_us / microseconds_per_tick)
                previous_time_us = time_us

                # Durata della nota in tick
                duration_ticks = int(duration_us / ticks_per_second)

                # Crea gli eventi MIDI
                track.append(Message('note_on', note = note, velocity = amplitude, time = delta_time_ticks))
                track.append(Message('note_off', note = note, velocity = 0, time = duration_ticks))

        # Salva il file MIDI
        midi.save(self.midi_file)
        
    def read_midi_file(self):
        midifile = MidiFile(self.midi_file)
        for i, track in enumerate(midifile.tracks):
            print(f"Track {i}: {track.name}")
            for msg in track:
                # Stampa ogni messaggio
                print(msg)

    

        

    def midi_event(self,filename):
        self.read_data_from_csv_and_write_music_data(filename)
        self.generate_audio_from_csv()
        #self.convert_csv_to_midi()
        #self.convert_midi_to_audio()
        #self.read_midi_file()

"""""
def convert_midi_to_audio(self):

        fs = fluidsynth.Synth()
        fs.start()
        sfid = fs.sfload(self.soundfont_path)
        fs.program_select(0, sfid, 0, 0)
        fs.midi_to_audio(self.midi_file, self.audio_file)
        print(f"File audio salvato come {self.audio_file}")
"""
        