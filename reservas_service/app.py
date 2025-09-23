from flask import Flask
from routes import reservas_bp
from client_clientes import consultar_clientes_bp


app = Flask(__name__)
app.register_blueprint(reservas_bp, url_prefix="/reservas")
app.register_blueprint(consultar_clientes_bp)

@app.route("/")
def index():
    return "Microservicio de reservas funcionando."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
