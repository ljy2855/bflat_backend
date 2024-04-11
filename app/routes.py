from flask import request, jsonify, Response
from werkzeug.utils import secure_filename
import os

from app.models import *
from app.services import make_prediction
from app.utils import *


def configure_routes(app):
    @app.route("/")
    def index():
        return "Welcome to the Model API"

    @app.route("/balance", methods=["POST"])
    def balance():
        if "file" not in request.files:
            response = BalanceResponse(
                volumes=None, success=False, error_message="No file part"
            )
            return Response(response.json(), status=400, mimetype="application/json")

        file = request.files["file"]
        if file.filename == "":
            response = BalanceResponse(
                volumes=None, success=False, error_message="No selected file"
            )
            return Response(response.json(), status=400, mimetype="application/json")

        filename = secure_filename(file.filename)
        filepath = os.path.join("/tmp", filename)
        file.save(filepath)

        # 서비스 로직 호출
        volumes_dict = make_prediction(filepath)

        # 파일 처리 후 서버에서 파일 삭제
        os.remove(filepath)

        # 응답 데이터 구성
        response = BalanceResponse(
            volumes=InstrumentVolumes(**volumes_dict), success=True
        )
        return Response(response.json(), status=200, mimetype="application/json")

    @app.route("/analysis", methods=["POST"])
    def analysis():
        return "analysis"
