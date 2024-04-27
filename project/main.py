from flask import Flask
from scraper.routes import routes


app = Flask(__name__)

app.register_blueprint(routes, url_prefix="/api/v1")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=2500)
