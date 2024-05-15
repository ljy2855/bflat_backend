import librosa
import soundfile as sf
import numpy as np
from scipy.ndimage import uniform_filter1d
from scipy.signal import butter, sosfilt

def remove_low_amplitude(y, threshold_db):
    amplitude = np.abs(y)
    threshold = 10 ** (threshold_db / 20)
    y[amplitude < threshold] = 0
    return y

def smooth_signal(y, window_size=100):
    return uniform_filter1d(y, size=window_size)

def reduce_reverb(y, sr):
    # Here you can use a simple high-pass filter to reduce low-frequency reverb
    sos = butter(10, 300, 'hp', fs=sr, output='sos')
    y_filtered = sosfilt(sos, y)
    return y_filtered

def optimize_other(file_other, file_drums, file_bass):
    # Load audio file
    y1, sr1 = librosa.load(file_other, sr=44100)
    y1 = reduce_reverb(y1, sr1)
    
    # Remove sounds below a certain dB threshold
    y1 = remove_low_amplitude(y1, threshold_db=-40)
    
    # Smooth the signal to reduce harshness and prevent clipping
    y1 = smooth_signal(y1, window_size=100)

    # Increase volume by 2 times
    y1 = y1 * 2.0
    # Ensure that the signal does not clip
    y1 = np.clip(y1, -1.0, 1.0)
    
    # Save the optimized file
    sf.write(file_other, y1, sr1)
    print(f"Optimized other saved to {file_other}")

# Example usage
file_other = "local_storage/other.wav"
file_drums = "local_storage/drums.wav"
file_bass = "local_storage/bass.wav"
optimize_other(file_other, file_drums, file_bass)
