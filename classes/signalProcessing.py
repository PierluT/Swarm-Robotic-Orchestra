import os
import librosa
import librosa.display
import soundfile as sf
import numpy as np
import glob
import re    


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
    
    print(f"Trovati {len(wav_files)} file WAV nella directory di input: {input_directory}")
    
    for wav_file in wav_files:
        # Analizza il nome del file
        filename = os.path.basename(wav_file)
        # Modifica la regex per estrarre la dinamica senza la N o la R finale
        match = re.match(r"(\w+)-ord-([A-G]#?\d+)-(\w+)-([NR])\.wav", filename)
        if not match:
            print(f"Formato del file non valido, ignorato: {filename}")
            continue
        
        # Estrai i componenti dal nome
        acronym, note, dynamic, dynamic_value = match.groups()
        
        # Converte la nota in valore MIDI
        midi_value = note_to_midi(note)
        
        # Verifica se la durata desiderata è un numero decimale
        if '.' in str(desired_duration):
            # Sostituisci il punto con trattino basso solo se la durata è decimale
            safe_duration = str(desired_duration).replace('.', '')
        else:
            # Se non è decimale, lascia il numero invariato
            safe_duration = str(int(desired_duration))  # Usa solo la parte intera
        
        # Ora prendiamo solo la dinamica senza la "N" o la "R" finale
        # Ad esempio "pp", "mf", "ff"
        dynamic_value = dynamic
        
        # Nuovo nome del file con durata desiderata inclusa
        new_filename = f"{acronym}_{midi_value}_{safe_duration}_{dynamic_value}.wav"
        new_filepath = os.path.join(output_directory, new_filename)
        
        # Modifica la durata del file audio
        audio, sr = librosa.load(wav_file, sr=None)
        original_duration = librosa.get_duration(y=audio, sr=sr)
        scaling_value = original_duration / desired_duration
        time_scaled_audio = librosa.effects.time_stretch(y=audio, rate=scaling_value)
        
        # Salva il file modificato nella directory di output
        sf.write(new_filepath, time_scaled_audio, sr)
        print(f"File elaborato e salvato come: {new_filepath}")

input_directory = r"C:/Users/pierl\Downloads/TinySOL/TinySOL/audio/Brass/Bass_Tuba/ordinario"
output_directory = r"C:/Users/pierl/Desktop/MMI/tesi/robotic-orchestra/classes/samples/bass_tuba"

final_duration = 0.5

process_wav_files(input_directory, output_directory, final_duration)