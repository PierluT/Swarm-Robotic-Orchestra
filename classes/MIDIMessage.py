import csv
import numpy as np
import librosa
import os
import pandas as pd
from scipy.io.wavfile import write
from pathlib import Path
import soundfile as sf
from classes.file_reader import File_Reader

file_reader_valuse = File_Reader()
values_dictionary = file_reader_valuse.read_configuration_file()

class MIDIMessage():
    
    def __init__(self):
        self.music_csv_file = "music.csv"
        self.final_csv_music_path = ""
        self.final_audio_file = 'final_output.wav'

    def write_csv(self, conductor_spartito, simulation_number, csv_path):
        # I recieve the csv folder path from supervisor, but I have to remove video.csv
        csv_directory = os.path.dirname(csv_path)
        self.final_csv_music_path = os.path.join(csv_directory, self.music_csv_file)
        #print(self.final_csv_music_path)
        #os.makedirs(self.directory, exist_ok=True)
        
        # if it necessary to write first row
        first_iteration = not os.path.exists(self.final_csv_music_path)
        
        # mode w writes the file, mode a appends vaues on the file.
        mode = "w" if first_iteration else "a"

        with open(self.final_csv_music_path, mode= mode, newline = '') as file:
            writer = csv.DictWriter(file, fieldnames=["simulation number", "ms", "musician", "note", "dur","bpm", "timbre", "delay", "dynamic"], delimiter=';')
            
            if first_iteration:
                writer.writeheader()
                self.final_csv_music_path = self.final_csv_music_path
            if conductor_spartito:
                for row in conductor_spartito:
                    row["simulation number"] = simulation_number
                    row.pop("beat phase", None)
                writer.writerows(conductor_spartito)
            
    def finding_wav_from_csv(self):
        
        if not os.path.exists(self.final_csv_music_path):
            raise FileNotFoundError(f"Il file CSV non esiste: {self.music_csv_file}")

        with open(self.final_csv_music_path, 'r') as f:
            lines = f.readlines()

        header = lines[0].strip().split(';')  # first row
        data = [line.strip().split(';') for line in lines[1:]]  # data

        timbre_index = header.index('timbre')
        note_index = header.index('note')
        dur_index = header.index('dur')
        delay_index = header.index('delay')

        # dictionary to found needed WAV files.
        matched_files = []
        wav_folder_name = 'samples'
        self.directory = Path(__file__).parent
        samples_directory = os.path.join(self.directory,wav_folder_name)
        
        for index, row in enumerate(data):
            instrument = row[timbre_index]  # timbre
            midi_note = int(row[note_index])  # MIDI note
            raw_duration = float(row[dur_index])
            delay = int(row[delay_index])  # delay value
            
            # Correzione della durata
            if raw_duration < 1:
                duration = str(int(raw_duration * 10)).zfill(2)  # Esempio: 0.5 -> 05
            else:
                duration = str(int(raw_duration))
                    # I want the strong accent on the first beat 
            
            if delay == 0:
                dynamic = "ff"
            else:
                dynamic = "mf"  
            #file_pattern = f"{instrument}_{midi_note}_{duration}"
            file_pattern = f"{instrument}_{midi_note}_{duration}_{dynamic}"
            instrument_folder = os.path.join(samples_directory, instrument)
            
            if not os.path.exists(instrument_folder):
                print(f"Cartella strumento non trovata: {instrument_folder}")
                continue
            
            # search for the files in the instrument directory
            matching_files = [
                f for f in os.listdir(instrument_folder) 
                if f.startswith(file_pattern) and f.endswith(".wav")
            ]

            if len(matching_files) == 0:
                print(f"Nessun file WAV trovato per: {instrument}, {midi_note}, {duration}")
            
            elif len(matching_files) > 1:
                matched_files.append(os.path.join(instrument_folder, matching_files[0]))  # by now takes the first one, has to implement amp behaviour.
                
            else:
                matched_files.append(os.path.join(instrument_folder, matching_files[0]))  # by now takes the first one, has to implement amp behaviour.
                
    
        return matched_files
    
    def generate_audio_from_csv(self,wav_files):
            if not os.path.exists(self.final_csv_music_path):
                raise FileNotFoundError(f"Il file CSV non esiste: {self.final_csv_music_path}")
            with open(self.final_csv_music_path, 'r') as f:
                lines = f.readlines()
                last_line = lines[-1]
                last_ms = int(last_line.split(';')[1])  # extract the last ms value to set final WAV file length.
            
            # Controlif the number of WAV files and csv rows information is equal.
            if len(lines[1:]) != len(wav_files):
                print("Attenzione: il numero di righe nel CSV e il numero di file WAV non corrispondono!")
            
            # sampling frequency
            sr = 44100
            audio_data = np.zeros(int(((last_ms + 1000) / 1000) * sr))
            for line, input_file in zip(lines[1:], wav_files):
                parts = line.strip().split(';')
                
                try:
                    if not os.path.exists(input_file):
                        print(f"File WAV non trovato: {input_file}. Salto questa riga.")
                        continue
                    ms = int(parts[1]) if parts[1].isdigit() else 0  # Offset in ms
                    delay = int(parts[7]) if parts[7].isdigit() else 0 # offset in delay
                    duration = int(parts[4]) if parts[4].isdigit() else 0
                    #print("delay "+ str(delay))
                    start_sample = int((ms / 1000 + delay ) * sr) # converts ms in samples

                    # load WAV file
                    audio, sr_file = librosa.load(input_file, sr=sr)
                    end_sample = start_sample + len(audio)

                    audio_data[start_sample:end_sample] += audio

                except Exception as e:
                    print(f"Errore durante l'elaborazione della riga o del file {input_file}: {e}")

        
            sf.write(self.final_audio_file, audio_data, sr)
            print(f"File audio finale generato: {self.final_audio_file}")

    
    def generate_metronome_click(self, sample_rate, click_duration=0.05, frequency=1000, amplitude=0.1):
        """Genera un click breve per il metronomo."""
        t = np.linspace(0, click_duration, int(sample_rate * click_duration), endpoint=False)
        click = amplitude * np.sin(2 * np.pi * frequency * t)
        return click

