from app.utils import save_file_based_on_environment


def check_sound(file):
    # 악기별 sound 반환
    return {
        "guitar": 20,
        "drums": 80.1,
        "bass": 30,
        "vocal": 40,
    }


def separate_instruments(file_path):
    """악기별로 파일을 분리하고 저장한 후 접근 가능한 경로를 반환"""
    return {
        "guitar": save_file_based_on_environment(file_path, "guitar.wav"),
        "drums": save_file_based_on_environment(file_path, "drums.wav"),
        "bass": save_file_based_on_environment(file_path, "bass.wav"),
        "vocal": save_file_based_on_environment(file_path, "vocal.wav"),
    }
