def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in {"mp3", "wav"}
