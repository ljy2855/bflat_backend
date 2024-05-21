import librosa
import soundfile as sf
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import uniform_filter1d
from scipy.signal import butter, sosfilt, resample
import os
import itertools
import random

def remove_low_amplitude(y, threshold_db):
    amplitude = np.abs(y)
    threshold = 10 ** (threshold_db / 20)
    y[amplitude < threshold] = 0
    return y

def smooth_signal(y, window_size):
    y_smooth = uniform_filter1d(y, size=window_size)
    y_smooth *= np.max(np.abs(y)) / np.max(np.abs(y_smooth))  # 재정규화
    return y_smooth

def reduce_reverb(y, sr):
    # High-pass filter to reduce low-frequency reverb
    sos = butter(10, 300, 'hp', fs=sr, output='sos')
    y_filtered = sosfilt(sos, y)
    return y_filtered

def remove_bass_from_other(y_other, y_bass, sr):
    # STFT (Short-Time Fourier Transform)
    stft_other = librosa.stft(y_other)
    stft_bass = librosa.stft(y_bass)
    
    # Magnitude and phase
    mag_other, phase_other = np.abs(stft_other), np.angle(stft_other)
    mag_bass, phase_bass = np.abs(stft_bass), np.angle(stft_bass)
    
    # Remove bass frequencies from other
    mag_result = mag_other - mag_bass
    mag_result = np.maximum(mag_result, 0)  # Ensure no negative values
    
    # Reconstruct the complex spectrum
    stft_result = mag_result * np.exp(1.j * phase_other)
    
    # Inverse STFT to get the time-domain signal
    y_result = librosa.istft(stft_result)
    return y_result

def optimize_other(file_other, file_drums, file_bass):
    # Load audio files
    y1, sr1 = librosa.load(file_other, sr=44100)
    y_bass, sr_bass = librosa.load(file_bass, sr=44100)
    
    if sr1 != sr_bass:
        raise ValueError("Sampling rates of the input files do not match.")
    
    # Remove bass sounds from other
    #y1 = remove_bass_from_other(y1, y_bass, sr1)
    
    # Save the optimized file
    #sf.write(file_other, y1, sr1)
    #print(f"Optimized other saved to {file_other}")

    return

def visualize_spectrum(file_paths, titles):
    fig, axs = plt.subplots(3, 1, figsize=(10, 12))

    for i, (file_path, title) in enumerate(zip(file_paths, titles)):
        y, sr = librosa.load(file_path, sr=44100)
        S = np.abs(librosa.stft(y))
        S_db = librosa.amplitude_to_db(S, ref=np.max)
        
        img = librosa.display.specshow(S_db, sr=sr, x_axis='time', y_axis='log', cmap='inferno', ax=axs[i])
        axs[i].set_title(f'Frequency Spectrum of {title}')
        axs[i].set_xlabel('Time (s)')
        axs[i].set_ylabel('Frequency (Hz)')
        fig.colorbar(img, ax=axs[i], format='%+2.0f dB')

    plt.tight_layout()
    plt.show()

def change_tempo(file_path, output_path, rate=1.2):
    # Load audio file
    y, sr = librosa.load(file_path, sr=44100)
    
    # Calculate new length of the audio
    new_length = int(len(y) / rate)
    
    # Resample audio to change the tempo
    y_stretched = resample(y, new_length)
    
    # Save the changed file
    sf.write(output_path, y_stretched, sr)
    print(f"Tempo changed and saved to {output_path}")

def load_audio(file_path):
    y, sr = librosa.load(file_path, sr=None)
    return y, sr

def save_audio(file_path, y, sr):
    sf.write(file_path, y, sr)

def combine_audios_with_random_volumes(audio_files, output_dir="local_storage/combined", num_combinations=10):
    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Load all audio files
    audio_data = {}
    sr = None
    for name, file_path in audio_files.items():
        y, sr = load_audio(file_path)
        audio_data[name] = y

    # Generate all combinations of audio files with at least 3 instruments
    all_combinations = []
    for r in range(3, len(audio_files) + 1):
        combinations = itertools.combinations(audio_files.keys(), r)
        all_combinations.extend(combinations)
    
    # Randomly select a few combinations
    selected_combinations = random.sample(all_combinations, min(num_combinations, len(all_combinations)))

    # Combine and save each combination with random volumes
    for combination in selected_combinations:
        combined_audio = np.zeros_like(audio_data[combination[0]])
        volume_changes = {}
        
        for instrument in combination:
            random_volume = random.uniform(0.5, 1.5)
            volume_changes[instrument] = random_volume
            combined_audio += audio_data[instrument] * random_volume
        
        combined_audio = combined_audio / len(combination)  # Normalize to prevent clipping

        volume_change_str = "_".join([f"{instrument}_{volume_changes[instrument]:.2f}" for instrument in combination])
        file_name = f"{len(combination)}_{volume_change_str}.wav"
        file_path = os.path.join(output_dir, file_name)
        save_audio(file_path, combined_audio, sr)
        print(f"Saved combined audio: {file_path}")

# Example usage
audio_files = {
    "other": "local_storage/other.wav",
    "drums": "local_storage/drums.wav",
    "bass": "local_storage/bass.wav",
    "vocals": "local_storage/vocals.wav"
}
file_song = "local_storage/song.wav"
#change_tempo(file_song, output_song, rate=1.2)
#optimize_bass(file_bass)
#visualize_spectrum([file_bass], ['Optimized_bass'])
#optimize_other(file_other, file_drums, file_bass)
