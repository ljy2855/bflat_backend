from app.utils import save_file_based_on_environment
import os
import noisereduce as nr
import numpy as np
import torch
import librosa
import subprocess
import soundfile as sf
import shutil
import sys
from scipy.ndimage import uniform_filter1d
from scipy.signal import butter, sosfilt
import pyloudnorm as pyln

def check_sound(file):
    # 악기별 sound 반환
    # file로 input이 들어온다고 가정하시고 작성해주심 되겠습니다.
    # 일단은 직접 작성하신 코드로 테스트 이후에 끝나면 옮길 예정이긴 합니다.
    
    return {
        "guitar": 20,
        "drums": 80.1,
        "bass": 30,
        "vocal": 40,
    }


def separate_instruments(file_path, file_name):
    # 샘플링 레이트 통일 및 음원 로드
    print("Load Audio")
    y, sr = librosa.load(file_path, sr=44100)
    # 추출 전 노이즈 제거
    print("Remove noise")
    y = nr.reduce_noise(y=y, sr=sr)

    # 중간 저장 디렉토리 생성
    separate_path = os.path.join(os.path.dirname(file_path), 'separated')
    if not os.path.exists(separate_path):
        os.makedirs(separate_path)

    # 파일 불러올, 저장할 절대 주소 저장
    full_file_path = os.path.abspath(file_path)
    full_separate_path = os.path.abspath(separate_path)

    # demucs 가동
    print("Separate using Demucs")
    subprocess.run([sys.executable, "-m", "demucs", "-d", "cpu", "-o", full_separate_path, full_file_path])

    instruments = ['bass', 'drums', 'vocals', 'other']
    paths = {}

    # save_file_based_on_environment 함수를 이용하여 악기별로 local_storage 폴더로 이동하여 저장
    for instrument in instruments:
        source_path = os.path.join(separate_path, 'htdemucs', file_name, instrument + ".wav")
        if os.path.exists(source_path):
            saved_path = save_file_based_on_environment(source_path, instrument + ".wav")
            paths[instrument] = saved_path
        else:
            print(f"Warning: The expected file {source_path} does not exist.")
    
    if os.path.exists(separate_path):
        # separated 디렉토리와 내용물 전체 삭제
        shutil.rmtree(separate_path)
        print(f"'{separate_path}' 디렉토리와 모든 내용물이 성공적으로 삭제되었습니다.")
    else:
        print(f"'{separate_path}' 디렉토리는 존재하지 않습니다.")

    # 여기까지 음원 분리 및 파일 저장 완료
    # 이후부터는 분리된 음원 개선 및 마디 분리, 원곡과 녹음본 비교 진행

    optimize_drums(paths['drums'])
    optimize_bass(paths['bass'])
    optimize_vocals(paths['vocals'])
    optimize_other(paths['other'], paths['drums'], paths['bass'])

    # 이 부분에 drum beat 관련 함수 연결해주시면 될 것 같습니다.
    # 현재는 paths[]에 파일이 연결되어 있는 상태입니다.
    # 함수 추가 작성은 하단에 부탁드립니다.

    return paths

def remove_low_amplitude(y, threshold_db):
    # Calculate the amplitude of the signal
    amplitude = np.abs(y)
    # Convert threshold from dB to amplitude
    threshold = 10 ** (threshold_db / 20)
    # Zero out values below the threshold
    y[amplitude < threshold] = 0
    return y

def smooth_signal(y, window_size=100):
    return uniform_filter1d(y, size=window_size)

def reduce_reverb(y, sr):
    # Here you can use a simple high-pass filter to reduce low-frequency reverb
    sos = butter(10, 300, 'hp', fs=sr, output='sos')
    y_filtered = sosfilt(sos, y)
    return y_filtered

def apply_compressor(y, sr, threshold=-20.0, ratio=4.0):
    # Use pyloudnorm for loudness normalization
    meter = pyln.Meter(sr)  # create BS.1770 meter
    loudness = meter.integrated_loudness(y)
    y_normalized = pyln.normalize.loudness(y, loudness, threshold)
    
    # Simple compression by limiting the max amplitude
    y_compressed = np.clip(y_normalized, -ratio, ratio)
    return y_compressed

def optimize_drums(file_drums):
    # drum 소리 이외에 잡음 들리지 않도록 특정 진폭 이하의 소리 제거
    y, sr = librosa.load(file_drums, sr=44100)
    y = remove_low_amplitude(y, threshold_db=-40)
    sf.write(file_drums, y, sr)

    return

def optimize_bass(file_bass):
    # bass의 음역대가 아닌 특정 hZ 이상 음 제거
    # bass의 음이 찢어지는 경향 완화
    y, sr = librosa.load(file_bass, sr=44100)
    y = remove_low_amplitude(y, threshold_db=-60)
    y = smooth_signal(y, window_size=100)
    sf.write(file_bass, y, sr)

    return

def optimize_vocals(file_vocals):
    # vocal reverb 축소
    # 보컬 연속성 보장
    # 보컬 성량 일정 수준 유지
    y, sr = librosa.load(file_vocals, sr=44100)
    
    # Reduce reverb
    y = reduce_reverb(y, sr)
    
    # Remove sounds below a certain dB threshold
    y = remove_low_amplitude(y, threshold_db=-60)
    
    # Smooth the signal to reduce harshness and prevent clipping
    y = smooth_signal(y, window_size=100)
    
    # Apply compressor to even out volume levels
    y = apply_compressor(y, sr)
    
    # Increase volume by 1.2 times
    y = y * 1.2
    # Ensure that the signal does not clip
    y = np.clip(y, -1.0, 1.0)
    sf.write(file_vocals, y, sr)

    return

def optimize_other(file_other, file_drums, file_bass):
    # other 파일로부터 drums.wav, bass.wav와 겹치는 음 제거

    return