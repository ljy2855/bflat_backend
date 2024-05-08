import boto3
import os


def make_prediction(file):
    # 악기별 sound 반환
    return {
        "guitar": 20,
        "drums": 80.1,
        "bass": 30,
        "vocal": 40,
    }


def seperate_instructment(file):
    # 악기 분리 로직
    return {
        "guitar": upload_file_to_s3(file, "guitar"),
        "drums": upload_file_to_s3(file, "drums"),
        "bass": upload_file_to_s3(file, "bass"),
        "vocal": upload_file_to_s3(file, "vocal"),
    }


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
