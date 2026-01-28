import numpy as np
from scipy.io import wavfile

def compute_sound_intensity_db(wav_path):
    """
    Computes the sound intensity level (in dB SPL) of a .wav file.
    
    Parameters
    ----------
    wav_path : str
        Path to the .wav file.
        
    Returns
    -------
    Lp : float
        Average sound pressure level (dB SPL).
    """
    # 1. Load the WAV file
    sample_rate, data = wavfile.read(wav_path)

    # 2. If stereo, convert to mono (average the two channels)
    if data.ndim > 1:
        data = np.mean(data, axis=1)

    # 3. Normalize to the range [-1, 1] if it's integer-encoded
    if np.issubdtype(data.dtype, np.integer):
        max_val = np.iinfo(data.dtype).max
        data = data / max_val

    # 4. Compute RMS pressure (root mean square)
    p_rms = np.sqrt(np.mean(data**2))

    # 5. Reference pressure in air (Pa)
    p_ref = 2e-5  # 20 µPa, standard reference in acoustics

    # 6. Compute sound pressure level in decibels
    Lp = 20 * np.log10(p_rms / p_ref)

    return Lp

# Example of usage:
wav_file = "samples\TpC\TpC_77_1_pp.wav"  # <-- replace with your .wav file path
intensity_db = compute_sound_intensity_db(wav_file)
print(f"Average sound intensity level: {intensity_db:.2f} dB SPL")
