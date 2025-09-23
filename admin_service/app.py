from flask import Flask
from routes import admin_bp

app = Flask(__name__)
app.register_blueprint(admin_bp, url_prefix="/admin")

@app.route("/")
def index():
    return "Microservicio de admin funcionando."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003)
