def configure_routes(app):
    @app.route("/")
    def index():
        return "Welcome to the Model API"

    @app.route("/predict", methods=["POST"])
    def predict():
        from .services import make_prediction

        return make_prediction()
