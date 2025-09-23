from flask import Flask
from routes import clientes_bp

app = Flask(__name__)
app.register_blueprint(clientes_bp, url_prefix="/clientes")

@app.route("/")
def index():
    return "Microservicio de clientes funcionando."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
