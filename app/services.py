from app.utils import save_file_based_on_environment
import os
import noisereduce as nr
import numpy as np
import torch
import librosa
import subprocess
import soundfile as sf
import shutil

def check_sound(file):
    # 악기별 sound 반환
    return {
        "guitar": 20,
        "drums": 80.1,
        "bass": 30,
        "vocal": 40,
    }


def separate_instruments(file_path, file_name):
    print("Load Audio")
    #y, sr = librosa.load(file_path, sr=44100)
    print("Remove noise")
    #y = nr.reduce_noise(y=y, sr=sr)

    # Define the output directory for the separated tracks
    separate_path = os.path.join(os.path.dirname(file_path), 'separated')
    if not os.path.exists(separate_path):
        os.makedirs(separate_path)

    print("Separate using Demucs")
    # Run Demucs separation
    #subprocess.run(["python3", "-m", "demucs", "-d", "cpu", "-o", separate_path, file_path])

    # Instruments that Demucs separates into
    instruments = ['bass', 'drums', 'vocals', 'other']
    paths = {}

    # Save each separated file using your environment-specific function
    for instrument in instruments:
        source_path = os.path.join(separate_path, 'htdemucs', file_name, instrument + ".wav")
        if os.path.exists(source_path):
            saved_path = save_file_based_on_environment(source_path, instrument + ".wav")
            paths[instrument] = saved_path
        else:
            print(f"Warning: The expected file {source_path} does not exist.")
    
    if os.path.exists(separate_path):
        # 디렉토리와 내용물 전체 삭제
        shutil.rmtree(separate_path)
        print(f"'{separate_path}' 디렉토리와 모든 내용물이 성공적으로 삭제되었습니다.")
    else:
        print(f"'{separate_path}' 디렉토리는 존재하지 않습니다.")

    return paths
