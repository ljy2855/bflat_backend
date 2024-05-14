from flask import request, jsonify, Response
from werkzeug.utils import secure_filename
import os

from app.models import *
from app.services import check_sound, separate_instruments
from app.utils import *


def configure_routes(app):
    # request로부터 file 추출
    tmp = input("곡의 이름 입력 : ")
    filename = tmp + '.wav'
    filepath = os.path.join('local_storage', filename)
    
    instructments = separate_instruments(filepath, tmp)

    """@app.route("/")
    def index():
        return "Welcome to the Model API"

    @app.route("/balance", methods=["POST"])
    def balance():
        # request로부터 file 추출
        if "file" not in request.files:
            response = BalanceResponse(
                volumes=None, success=False, error_message="No file part"
            )
            return Response(
                response.model_dump_json(), status=400, mimetype="application/json"
            )

        file = request.files["file"]
        if file.filename == "":
            response = BalanceResponse(
                volumes=None, success=False, error_message="No selected file"
            )
            return Response(
                response.model_dump_json(), status=400, mimetype="application/json"
            )

        filename = secure_filename(file.filename)
        filepath = os.path.join("/tmp", filename)
        file.save(filepath)

        # 서비스 로직 호출
        volumes_dict = check_sound(filepath)

        # 파일 처리 후 서버에서 파일 삭제
        os.remove(filepath)

        # 응답 데이터 구성
        response = BalanceResponse(
            volumes=InstrumentVolumes(**volumes_dict), success=True
        )
        return Response(
            response.model_dump_json(), status=200, mimetype="application/json"
        )

    @app.route("/analysis", methods=["POST"])
    def analysis():
        # request로부터 file 추출
        if "file" not in request.files:
            response = BalanceResponse(
                volumes=None, success=False, error_message="No file part"
            )
            return Response(
                response.model_dump_json(), status=400, mimetype="application/json"
            )

        file = request.files["file"]
        if file.filename == "":
            response = BalanceResponse(
                volumes=None, success=False, error_message="No selected file"
            )
            return Response(
                response.model_dump_json(), status=400, mimetype="application/json"
            )

        filename = secure_filename(file.filename)
        filepath = os.path.join("/tmp", filename)
        file.save(filepath)

        instructments = separate_instruments(filepath)

        response = AnalysisResponse(
            files=InstrumentFileUrls(**instructments), success=True
        )
        return Response(
            response.model_dump_json(), status=200, mimetype="application/json"
        )
"""