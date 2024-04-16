from flask import Flask
from routes.routes import routes

app = Flask(__name__)

app.register_blueprint(routes, url_prefix="/api/v1")

if __name__ == "__main__":
    app.run(debug=True)
