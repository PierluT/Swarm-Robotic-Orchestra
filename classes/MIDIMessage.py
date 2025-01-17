import csv
import numpy as np
import librosa
import os
import pandas as pd
from scipy.io.wavfile import write
from pathlib import Path
import soundfile as sf

class MIDIMessage():
    
    def __init__(self):
        self.music_csv_file = "music_data.csv"
        self.final_audio_file = 'final_output.wav'
        self.directory = ""
        self.final_csv_music_path = ""

    def write_csv(self, conductor_spartito, csv_file_path):
        self.directory = csv_file_path
        music_csv_path = os.path.join(self.directory, self.music_csv_file)
        
        # Assicurati che la directory esista
        os.makedirs(self.directory, exist_ok=True)
        
        # Determina se è necessario scrivere l'intestazione
        first_iteration = not os.path.exists(music_csv_path)
        
        # Imposta la modalità di apertura del file
        mode = "w" if first_iteration else "a"
        
        # Apri il file in modalità corretta
        with open(music_csv_path, mode=mode, newline="") as file:
            writer = csv.DictWriter(file, fieldnames=["simulation number", "ms", "musician", "note", "dur", "amp", "bpm", "timbre", "delay"])
            
            # Scrivi l'intestazione solo se necessario
            if first_iteration:
                writer.writeheader()
                self.final_csv_music_path = music_csv_path
            
            # Scrivi le righe solo se ci sono dati
            if conductor_spartito:
                #print(f"Scrivendo {len(conductor_spartito)} righe nel file CSV...")
                writer.writerows(conductor_spartito)
            
    def finding_wav_from_csv(self):

        # Controlla se il file CSV esiste
        if not os.path.exists(self.final_csv_music_path):
            raise FileNotFoundError(f"Il file CSV non esiste: {self.music_csv_file}")

        # Leggi il file CSV con readlines()
        with open(self.final_csv_music_path, 'r') as f:
            lines = f.readlines()

        # Estrai l'intestazione e i dati
        header = lines[0].strip().split(',')  # Intestazione come lista
        data = [line.strip().split(',') for line in lines[1:]]  # Dati come liste

        # Indici delle colonne
        timbre_index = header.index('timbre')
        note_index = header.index('note')
        dur_index = header.index('dur')

        # Dizionario per salvare i percorsi dei file trovati
        matched_files = []
        wav_folder_name = 'samples'
        self.directory = Path(__file__).parent
        samples_directory = os.path.join(self.directory,wav_folder_name)
        
        # Itera sui dati
        for index, row in enumerate(data):
            instrument = row[timbre_index]  # Timbro
            midi_note = int(row[note_index])  # Nota MIDI
            duration = int(row[dur_index])  # Durata
            file_pattern = f"{instrument}_{midi_note}_{int(duration)}"

            # Directory dello strumento
            instrument_folder = os.path.join(samples_directory, instrument)
            #print("path cartella strumento: " +str(instrument_folder))
            
            if not os.path.exists(instrument_folder):
                print(f"Cartella strumento non trovata: {instrument_folder}")
                continue
            
            # Cerca i file corrispondenti nella directory dello strumento
            matching_files = [
                f for f in os.listdir(instrument_folder) 
                if f.startswith(file_pattern) and f.endswith(".wav")
            ]
            
            # Gestione dei risultati
            if len(matching_files) == 0:
                print(f"Nessun file WAV trovato per: {instrument}, {midi_note}, {duration}")
                #matched_files = None  # Nessun file trovato
            
            elif len(matching_files) > 1:
                matched_files.append(os.path.join(instrument_folder, matching_files[0]))  # Prendi il primo
                #print(f"Più file WAV trovati per: {instrument}, {midi_note}, {duration}, scegliendo il primo.")
                
                
            else:
                matched_files.append(os.path.join(instrument_folder, matching_files[0]))  # Prendi il primo
                
    
        return matched_files


    # convert a MIDI note into frequency.
    def midi_to_freq(self,midi_note):
        return 440.0 * (2 ** ((midi_note + 69 - 69) / 12.0))
    
    # to generate a sinusoidal wave.
    def generate_wave(self,freq,duration, amplitude, sample_rate = 44100):
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint= False)
        wave = amplitude * np.sin(2* np.pi * freq * t)
        return wave
    
    def generate_audio_from_csv(self,wav_files):
        
        # Controlla se il file CSV esiste
        if not os.path.exists(self.final_csv_music_path):
            raise FileNotFoundError(f"Il file CSV non esiste: {self.final_csv_music_path}")
        # Leggi il CSV come lista di righe
        with open(self.final_csv_music_path, 'r') as f:
            lines = f.readlines()
            last_line = lines[-1]
            last_ms = int(last_line.split(',')[1])  # Estrai il primo valore ('ms') e convertilo in intero
        #print(f"L'ultimo valore di ms è: {last_ms}")
        
        # Controlla se ci sono abbastanza file WAV rispetto alle righe del CSV
        if len(lines[1:]) != len(wav_files):
            print("Attenzione: il numero di righe nel CSV e il numero di file WAV non corrispondono!")
        else:   
            print("CSV e il numero di file WAV corrispondono!") 
        
        # sampling frequency
        sr = 44100
        audio_data = np.zeros(int(((last_ms + 1000) / 1000) * sr))
        # Itera su righe del CSV e file WAV simultaneamente
        for line, input_file in zip(lines[1:], wav_files):
            
            # Processa la riga del CSV
            parts = line.strip().split(',')
            
            try:
                # Controlla se il file WAV esiste
                if not os.path.exists(input_file):
                    print(f"File WAV non trovato: {input_file}. Salto questa riga.")
                    continue

                # Controlla se la riga contiene un valore di millisecondi valido
                ms = int(parts[1]) if parts[1].isdigit() else 0  # Offset in millisecondi
                delay = int(parts[8]) if parts[8].isdigit() else 0
                #print("delay "+ str(delay))
                start_sample = int((ms / 1000 + delay ) * sr)  # Converti ms in campioni

                # Carica il file WAV
                audio, sr_file = librosa.load(input_file, sr=sr)

                # Controlla la lunghezza del file WAV rispetto all'array di output
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

