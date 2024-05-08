import shutil
import boto3
import os


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in {"mp3", "wav"}


def save_file_based_on_environment(file_path, filename):
    """환경에 따라 파일 저장 방식 선택"""
    if os.getenv("FLASK_ENV") == "DEPLOY":
        return upload_file_to_s3(file_path, filename)
    else:
        return save_local(file_path, filename)


def save_local(file_path, filename):
    """로컬 파일 시스템에 파일 저장"""
    local_storage_path = "local_storage"
    if not os.path.exists(local_storage_path):
        os.makedirs(local_storage_path)

    local_file_path = os.path.join(local_storage_path, filename)
    # 파일 복사 사용
    if os.path.exists(file_path):
        shutil.copy(file_path, local_file_path)
        # 절대 경로 반환
        return os.path.abspath(local_file_path)
    else:
        print(f"Error: File not found at {file_path}")
        return None  # 파일이 없는 경우 None 반환


def upload_file_to_s3(file_path, filename, expiration=3600):
    """업로드한 파일의 프리사인드 URL을 생성하여 반환한다."""
    s3 = boto3.client("s3")
    bucket_name = os.getenv("S3_BUCKET_NAME")  # 환경 변수에서 버킷 이름 가져오기
    if not bucket_name:
        raise ValueError("S3 bucket name not set in environment variables")

    s3_file_path = f"uploads/{filename}"
    s3.upload_file(file_path, bucket_name, s3_file_path)

    # 프리사인드 URL 생성
    try:
        response = s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket_name, "Key": s3_file_path},
            ExpiresIn=expiration,
        )
    except Exception as e:
        print(f"Error generating presigned URL: {e}")
        return None

    return response
