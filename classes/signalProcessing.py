import os
import librosa
import librosa.display
import soundfile as sf

def modify_wav_sample(input_file, output_file, desired_duration):
    """
    Modifica un file audio WAV cambiando durata senza distorcere il pitch.
    
    Args:
        input_file (str): Path al file WAV originale.
        output_file (str): Path dove salvare il file modificato.
        desired_duration (float): Durata desiderata in secondi.
    """
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
    

input_wav = r"C:/Users/pierl/Desktop/MMI/tesi/robotic-orchestra/classes/samples/Tbn-G.wav"
output_wav =r"C:/Users/pierl/Desktop/MMI/tesi/robotic-orchestra/classes/samples/Tbn-G-modified2.wav"
final_duration = 1

modify_wav_sample(input_wav, output_wav, final_duration)
