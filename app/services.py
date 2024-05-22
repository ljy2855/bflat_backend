from app.utils import save_file_based_on_environment
import os
import noisereduce as nr
import numpy as np
import librosa
import subprocess
import soundfile as sf
import shutil
import sys
from scipy.ndimage import uniform_filter1d
from scipy.signal import butter, sosfilt
import pyloudnorm as pyln
from app.models import BPMMeter

class mergedbeat:
    def __init__(self, start, duration, bpm):
        self.start = start
        self.duration = duration
        self.bpm = bpm

# 일정 음량 이하의 음원 파일 삭제
def remove_silent_files(file_path, threshold=0.01):
    if os.path.exists(file_path):
        y, sr = librosa.load(file_path, sr=44100)
        rms = librosa.feature.rms(y=y).mean()
        if rms < threshold:
            print(f"Remove {os.path.basename(file_path)}")
            os.remove(file_path)
            return 0.0
        else:
            print(f"Keep {os.path.basename(file_path)}")
            y_abs = np.abs(y)
            med = np.median(y_abs)
            return med
    else:
        print(f"File {os.path.basename(file_path)} does not exist.")
        return 0.0

def check_sound(file, stem):
    # 분리할 임시 디렉토리 설정
    separate_path = os.path.join(os.path.dirname(file), 'separated_temp')
    if not os.path.exists(separate_path):
        os.makedirs(separate_path)

    # 파일 불러올, 저장할 절대 주소 저장
    full_file_path = os.path.abspath(file)
    full_separate_path = os.path.abspath(separate_path)

    # demucs 가동
    print("Separate using Demucs")
    subprocess.run([sys.executable, "-m", "demucs", "-d", "cpu", "-o", full_separate_path, full_file_path])

    instruments = ['bass', 'drums', 'vocals', 'other']
    paths = {}

    # 악기별로 분리된 파일 경로 저장
    for instrument in instruments:
        if stem.get(instrument, False):  # stem에서 해당 악기가 True일 때만 처리
            source_path = os.path.join(separate_path, 'htdemucs', os.path.splitext(os.path.basename(file))[0], instrument + ".wav")
            if os.path.exists(source_path):
                paths[instrument] = source_path
            else:
                print(f"Warning: The expected file {source_path} does not exist.")

    # 각 파일에 대해 처리
    db_stems = {}
    for instrument in instruments:
        if instrument in paths:
            db_stems[instrument] = remove_silent_files(paths[instrument], threshold=0.01)

    # 전체 음원의 중앙값 구하기
    audio, sr = librosa.load(file, sr=44100)
    origin_abs = np.abs(audio)
    origin_med = np.median(origin_abs)
    if origin_med == 0:
        raise ValueError("The median of the original audio is 0, cannot scale volumes.")

    # 각 악기의 볼륨 계산 및 출력
    volumes = {}
    for instrument, med in db_stems.items():
        if med > 0:
            volume_value = (50 / origin_med) * med
        else:
            volume_value = 0
        volumes[instrument] = volume_value
    
    # separated_temp 디렉토리와 내용물 전체 삭제
    if os.path.exists(separate_path):
        shutil.rmtree(separate_path)
        print(f"'{separate_path}' 디렉토리와 모든 내용물이 성공적으로 삭제되었습니다.")
    else:
        print(f"'{separate_path}' 디렉토리는 존재하지 않습니다.")
    
    # 악기별 sound 반환    
    return volumes

def separate_instruments(file_path, bpm_meter: BPMMeter, stem):
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
        if stem.get(instrument, False):  # stem에서 해당 악기가 True일 때만 처리
            source_path = os.path.join(separate_path, 'htdemucs', os.path.splitext(os.path.basename(file_path))[0], instrument + ".wav")
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

    if 'drums' in paths:
        optimize_drums(paths['drums'])
    if 'bass' in paths:
        optimize_bass(paths['bass'])
    if 'vocals' in paths:
        optimize_vocals(paths['vocals'])
    if 'other' in paths:
        optimize_other(paths['other'], paths.get('drums', None), paths.get('bass', None))

    # bpm 측정
    # 예상 duration time
    expected_duration = 60 / bpm_meter.bpm * bpm_meter.meter
    
    # WAV 파일 로드
    audio, sr = librosa.load(paths['drums'], sr=None)

    # 템포 추정 및 비트 추출
    tempo, beat_frames = librosa.beat.beat_track(y=audio, sr=sr)

    # 마디 위치 계산
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)

    measure_meter = []
    # 머신에서 도출된 duration / bpm 계산
    for i in range(len(beat_times) - 1):
        duration = beat_times[i+1] - beat_times[i]
        meter = expected_duration / duration
        measure_meter.append(meter)

    # 평균 kick 수 구하기
    tot_meter = sum(measure_meter)  # measure_beats 리스트의 meter 속성의 합계 계산
    avg_meter_f = tot_meter / len(measure_meter)  # 평균 meter 계산
    avg_meter = int(round(avg_meter_f * 2) / 2)
    
    # Bar를 합쳐서 마디로 만들기
    merged_beat_times = []
    for i in range(0, len(beat_times), avg_meter):
        if i + avg_meter < len(beat_times):  # 다음 Bar가 존재하는 경우에만 합치기
            merged_beat_times.append((beat_times[i], beat_times[i + avg_meter]))

    merged_beats = []
    # 합쳐진 Bar의 BPM 계산 및 출력
    for i, (start_time, end_time) in enumerate(merged_beat_times):
        measure_duration = end_time - start_time
        bpm = 60 / measure_duration * bpm_meter.meter 
        # MergedBeat 인스턴스 생성 및 리스트에 추가
        merged_beat = mergedbeat(start=start_time, duration=measure_duration, bpm=bpm)
        merged_beats.append(merged_beat)
    
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
    y_smooth = uniform_filter1d(y, size=window_size)
    y_smooth *= np.max(np.abs(y)) / np.max(np.abs(y_smooth))  # 재정규화
    return y_smooth

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
    y = remove_low_amplitude(y, threshold_db=-40)
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

