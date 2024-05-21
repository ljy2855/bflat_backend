from flask import request, jsonify, Response
from werkzeug.utils import secure_filename
import os

from app.models import *
from app.services import check_sound, separate_instruments
from app.utils import *

def configure_routes(app):
    # request로부터 file 추출
    """tmp = input("곡의 이름 입력 : ")
    filename = tmp + '.wav'
    filepath = os.path.join('local_storage', filename)

    stem = {
    "bass": input("Bass 포함 여부 (t/f): ").strip().lower() == 't',
    "drums": input("Drums 포함 여부 (t/f): ").strip().lower() == 't',
    "vocals": input("Vocals 포함 여부 (t/f): ").strip().lower() == 't',
    "other": input("Other 포함 여부 (t/f): ").strip().lower() == 't'
    }

    volumes_dict = check_sound(filepath, stem)

    bpm = int(input("BPM: "))
    meter = int(input("Meter: "))
    bpm_meter = BPMMeter(bpm=bpm, meter=meter)
    
    instructments = separate_instruments(filepath, bpm_meter, stem)
"""
    @app.route("/")
    def index():
        return "Welcome to the Model API"

    @app.route("/balance", methods=["POST"])
    def balance():
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

        stem = {
            "bass": request.form.get("bass", 'false').lower() == 'true',
            "drums": request.form.get("drums", 'false').lower() == 'true',
            "vocals": request.form.get("vocals", 'false').lower() == 'true',
            "other": request.form.get("other", 'false').lower() == 'true'
        }

        filename = secure_filename(file.filename)
        filepath = os.path.join("/tmp", filename)
        file.save(filepath)

        volumes_dict = check_sound(filepath, stem)

        os.remove(filepath)

        response = BalanceResponse(
            volumes=InstrumentVolumes(**volumes_dict), success=True
        )
        return Response(
            response.model_dump_json(), status=200, mimetype="application/json"
        )

    @app.route("/analysis", methods=["POST"])
    def analysis():
        if "file1" not in request.files or "file2" not in request.files:
            response = BalanceResponse(
                volumes=None, success=False, error_message="No file1 or file2 part"
            )
            return Response(
                response.model_dump_json(), status=400, mimetype="application/json"
            )

        file1 = request.files["file1"]
        file2 = request.files["file2"]
        if file1.filename == "" or file2.filename == "":
            response = BalanceResponse(
                volumes=None, success=False, error_message="No selected file"
            )
            return Response(
                response.model_dump_json(), status=400, mimetype="application/json"
            )

        filename1 = secure_filename(file1.filename)
        filename2 = secure_filename(file2.filename)
        filepath1 = os.path.join("/tmp", filename1)
        filepath2 = os.path.join("/tmp", filename2)
        file1.save(filepath1)
        file2.save(filepath2)

        bpm = int(request.form.get("bpm"))
        meter = int(request.form.get("meter"))
        stem = {
            "bass": request.form.get("bass", 'false').lower() == 'true',
            "drums": request.form.get("drums", 'false').lower() == 'true',
            "vocals": request.form.get("vocals", 'false').lower() == 'true',
            "other": request.form.get("other", 'false').lower() == 'true'
        }

        bpm_meter = BPMMeter(bpm=bpm, meter=meter)
        instruments1 = separate_instruments(filepath1, bpm_meter, stem)
        instruments2 = separate_instruments(filepath2, bpm_meter, stem)

        response = AnalysisResponse(
            files=InstrumentFileUrls(**instruments1), success=True
        )
        return Response(
            response.model_dump_json(), status=200, mimetype="application/json"
        )
