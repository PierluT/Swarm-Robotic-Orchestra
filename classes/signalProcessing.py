import os
import librosa
import librosa.display
import soundfile as sf
import numpy as np
import glob


def modify_wav_samples_in_place(directory, desired_duration):
    """
    Modifica tutti i file audio WAV in una directory, cambiandone la durata senza distorcere il pitch.
    Sovrascrive i file originali.
    
    Args:
        directory (str): Path della directory contenente i file WAV.
        desired_duration (float): Durata desiderata in secondi per ciascun file.
    
    Returns:
        dict: Dizionario con i file modificati e le loro durate finali.
    """
    if not os.path.exists(directory):
        raise FileNotFoundError(f"La directory non esiste: {directory}")
    
    # Trova tutti i file WAV nella directory
    wav_files = glob.glob(os.path.join(directory, "*.wav"))
    
    if not wav_files:
        raise FileNotFoundError(f"Nessun file WAV trovato nella directory: {directory}")
    
    print(f"Trovati {len(wav_files)} file WAV nella directory: {directory}")
    
    modified_durations = {}  # Dizionario per salvare durate e file modificati
    
    for wav_file in wav_files:
        # Carica il file audio
        audio, sr = librosa.load(wav_file, sr=None)

        # Calcola la durata originale
        original_duration = librosa.get_duration(y=audio, sr=sr)
        print(f"File: {wav_file}")
        print(f"Durata originale: {original_duration:.2f} secondi")

        # Calcola il fattore di scalatura
        scaling_value = original_duration / desired_duration

        # Applica il time stretching
        time_scaled_audio = librosa.effects.time_stretch(y=audio, rate=scaling_value)

        # Sovrascrive il file originale
        sf.write(wav_file, time_scaled_audio, sr)
        print(f"Audio modificato e sovrascritto in: {wav_file}")

        # Calcola e salva la durata del file modificato
        modified_duration = librosa.get_duration(y=time_scaled_audio, sr=sr)
        print(f"Durata del file modificato: {modified_duration:.2f} secondi\n")
        
        # Salva il risultato nel dizionario
        modified_durations[wav_file] = modified_duration
    
    return modified_durations    

input_wav = r"C:/Users/pierl/Desktop/MMI/tesi/robotic-orchestra/classes/samples"

final_duration = 1

modify_wav_samples_in_place(input_wav, final_duration)

def generate_mixed_audio(output_file,duration = 15):

    input_files = [r"C:/Users/pierl/Desktop/MMI/tesi/robotic-orchestra/classes/samples/Tbn-G-modified2.wav"] * 5
    start_times = [1.0, 1.5, 3.0, 5.0, 7.5]

    sr = 22050  # Frequenza di campionamento
    final_audio = np.zeros(int(duration * sr))

    for i, input_file in enumerate(input_files):
        audio, sr_file = librosa.load(input_file, sr=sr)
        
        start_sample = int(start_times[i] * sr)  # Calcola il campione di inizio in base al tempo
        end_sample = start_sample + len(audio)  # Calcola la fine del file audio nel file finale

        # Aggiungi l'audio alla posizione corretta, sovrapponendolo
        final_audio[start_sample:end_sample] += audio  # Sovrapposizione semplice (senza normalizzazione)
    
    # Salva il file audio finale
    sf.write(output_file, final_audio, sr)
    print(f"Audio finale sovrapposto salvato in: {output_file}")

#output_wav =r"C:/Users/pierl/Desktop/MMI/tesi/robotic-orchestra/classes/samples/final-wav.wav"
#generate_mixed_audio(output_wav, duration=15)


"""""
def modify_wav_sample(input_file, output_file, desired_duration):

    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Il file non esiste: {input_file}")
    
    # Carica il file audio
    audio, sr = librosa.load(input_file, sr=None)

    # Calcola la durata originale
    original_duration = librosa.get_duration(y=audio, sr=sr)
    print(f"Durata originale: {original_duration:.2f} secondi")

    scaling_value =  original_duration / desired_duration

    time_scaled_audio = librosa.effects.time_stretch(y = audio, rate = scaling_value)

    # Salva il file modificato
    sf.write(output_file, time_scaled_audio, sr)
    print(f"Audio modificato salvato in: {output_file}")

    # Ritorna la durata del file modificato
    modified_duration = librosa.get_duration(y=time_scaled_audio, sr=sr)
    print(f"Durata del file modificato: {modified_duration:.2f} secondi")
    
    return modified_duration
"""