import os
from flask import Flask, jsonify, request
from database import init_db
from routes.api import api_bp
from routes.web import web_bp

def create_app(test_config=None):
    app = Flask(__name__, static_folder="static", template_folder="templates")
    
    app.config.from_mapping(
        SECRET_KEY="spendwise-secret-key-debuglab",
        DATABASE=os.path.join(app.root_path, "data", "spendwise.db")
    )

    if test_config:
        app.config.update(test_config)

    # Initialize SQLite database and seed initial data
    init_db(app.config.get("DATABASE"))

    # Register blueprints
    app.register_blueprint(web_bp)
    app.register_blueprint(api_bp)

    @app.errorhandler(404)
    def handle_404(e):
        if request.path.startswith("/api/"):
            return jsonify({"error": "Resource not found"}), 404
        return e

    @app.errorhandler(500)
    def handle_500(e):
        if request.path.startswith("/api/"):
            return jsonify({"error": "Internal server error"}), 500
        return e

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
