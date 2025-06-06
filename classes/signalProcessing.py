import os
import librosa
import soundfile as sf
import numpy as np
import glob
import re    
import numpy as np
import matplotlib.pyplot as plt
import soundfile as sf
from scipy.fft import rfft, rfftfreq


# Mappa per le note MIDI
NOTE_TO_MIDI = {
    'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5, 'F#': 6,
    'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11
}

def note_to_midi(note):
    """
    Converte una nota (es. G#4) nel valore MIDI corrispondente.
    """
    match = re.match(r"([A-G]#?)(\d+)", note)
    if not match:
        raise ValueError(f"Nota non valida: {note}")
    
    pitch_class, octave = match.groups()
    return NOTE_TO_MIDI[pitch_class] + (12 * (int(octave) + 1))

def process_wav_files(input_directory, output_directory, desired_duration):
    """
    Modifica la durata di tutti i file WAV in una directory di input e salva i file
    rinominati nella directory di output.

    Args:
        input_directory (str): Path della directory contenente i file WAV originali.
        output_directory (str): Path della directory dove salvare i file modificati.
        desired_duration (float): Durata desiderata in secondi per ciascun file.
    """
    if not os.path.exists(input_directory):
        raise FileNotFoundError(f"La directory di input non esiste: {input_directory}")
    
    # Crea la directory di output se non esiste
    os.makedirs(output_directory, exist_ok=True)
    
    # Trova tutti i file WAV nella directory di input
    wav_files = glob.glob(os.path.join(input_directory, "*.wav"))
    
    if not wav_files:
        raise FileNotFoundError(f"Nessun file WAV trovato nella directory: {input_directory}")
    
    #print(f"Trovati {len(wav_files)} file WAV nella directory di input: {input_directory}")
    
    for wav_file in wav_files:
        # Analizza il nome del file
        filename = os.path.basename(wav_file)
        # Modifica la regex per estrarre la dinamica senza la N o la R finale
        match = re.match(r"(\w+)-ord-([A-G]#?\d+)-(\w+).*\.wav", filename)
        if not match:
            print(f"Formato del file non valido, ignorato: {filename}")
            continue
        
        # Estrai i componenti dal nome
        acronym, note, dynamic = match.groups()
        
        # Converte la nota in valore MIDI
        midi_value = note_to_midi(note)
        
        # Verifica se la durata desiderata è un numero decimale
        if '.' in str(desired_duration):
            # Sostituisci il punto con trattino basso solo se la durata è decimale
            safe_duration = str(desired_duration).replace('.', '')
        else:
            # Se non è decimale, lascia il numero invariato
            safe_duration = str(int(desired_duration))  # Usa solo la parte intera
        
        # Nuovo nome del file con durata desiderata inclusa
        new_filename = f"{acronym}_{midi_value}_{safe_duration}_{dynamic}.wav"
        new_filepath = os.path.join(output_directory, new_filename)
        
        # Modifica la durata del file audio
        audio, sr = librosa.load(wav_file, sr=None)
        original_duration = librosa.get_duration(y=audio, sr=sr)
        scaling_value = original_duration / desired_duration
        time_scaled_audio = librosa.effects.time_stretch(y=audio, rate=scaling_value)
        
        # Salva il file modificato nella directory di output
        sf.write(new_filepath, time_scaled_audio, sr)
        print(f"File elaborato e salvato come: {new_filepath}")
        
        # Verifica che la durata ottenuta corrisponda a quella desiderata
        processed_audio, sr_new = librosa.load(new_filepath, sr=None)
        output_duration = librosa.get_duration(y=processed_audio, sr=sr_new)
        
        # Confronto tra durata desiderata e ottenuta
        if not np.isclose(output_duration, desired_duration, atol=0.01):  # Tolleranza di 10 ms
            print(f"ATTENZIONE: La durata del file {new_filename} non corrisponde a quella desiderata!")
            print(f"Durata desiderata: {desired_duration}s, durata ottenuta: {output_duration}s.")

#input_directory = r"C:/Users/pierl/Downloads/TinySOL/TinySOL/audio/Keyboards/Accordion/ordinario"
#output_directory = r"C:/Users/pierl/Desktop/samples/Acc"

#final_duration = 0.5

#process_wav_files(input_directory, output_directory, final_duration)

def generate_mixed_audio(output_file, duration=20.0):
    """
    Genera un file audio che è la sovrapposizione di più file WAV 
    che iniziano a momenti diversi (inventati) su una durata totale di 20 secondi.
    
    Args:
        output_file (str): Path del file audio finale da salvare.
        duration (float): Durata totale in secondi del file finale (default 20 secondi).
    """
    # Lista dei file audio di esempio (modifica con i tuoi file veri)
    input_files = [r""] * 5  # Copia del file 5 volte per l'esempio
    start_times = [1.0, 1.5, 3.0, 5.0, 7.5]  # I momenti di inizio per i file sovrapposti (esempio)
    
    # Creiamo un array di zeri per il file finale, della durata totale in campioni
    sr = 22050  # Frequenza di campionamento, deve essere uguale per tutti i file audio
    final_audio = np.zeros(int(duration * sr))  # Array finale per 20 secondi di durata

    # Sovrapponiamo i file audio all'interno dell'array finale
    for i, input_file in enumerate(input_files):
        # Carica ogni file audio
        audio, sr_file = librosa.load(input_file, sr=sr)  # Imposta la stessa frequenza di campionamento
        start_sample = int(start_times[i] * sr)  # Calcola il campione di inizio in base al tempo
        end_sample = start_sample + len(audio)  # Calcola la fine del file audio nel file finale
        
        # Aggiungi l'audio alla posizione corretta, sovrapponendolo
        final_audio[start_sample:end_sample] += audio  # Sovrapposizione semplice (senza normalizzazione)

    # Salva il file audio finale
    sf.write(output_file, final_audio, sr)
    print(f"Audio finale sovrapposto salvato in: {output_file}")

#output_final_wav_file = r"C:/Users/pierl/Desktop/MMI/tesi/robotic-orchestra/classes/samples/Mix-Audio.wav"
#generate_mixed_audio(output_final_wav_file, duration=1)



def plot_fft_spectrum(audio_path, max_freq=10000):
    """
    Carica un file WAV e mostra il suo spettro di frequenza con FFT.

    Parameters:
        audio_path (str): percorso al file WAV
        max_freq (int): frequenza massima da visualizzare (Hz)

    Output:
        Un grafico con l'ampiezza in funzione della frequenza.
    """
    # Carica il file audio
    y, sr = sf.read(audio_path)
    
    # Se stereo, prendi solo un canale
    if len(y.shape) > 1:
        y = y[:, 0]

    # Esegui la FFT
    N = len(y)
    yf = rfft(y)
    xf = rfftfreq(N, 1 / sr)

    # Grafico dello spettro
    plt.figure(figsize=(10, 4))
    plt.plot(xf, np.abs(yf), color='blue')
    plt.title("Spettro di Frequenza (FFT)")
    plt.xlabel("Frequenza (Hz)")
    plt.ylabel("Ampiezza")
    plt.xlim(0, max_freq)
    plt.grid(True)
    plt.tight_layout()
    plt.show()


plot_fft_spectrum(r"C:/Users/pierl/Desktop/MMI/tesi/robotic-orchestra/classes/samples/Ob/Ob_86_2_ff.wav", max_freq=8000)

