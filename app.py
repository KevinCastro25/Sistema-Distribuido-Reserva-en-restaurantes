from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import datetime

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://127.0.0.1:5500"}})

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///reservasRest.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# -------------------
# MODELO CLIENTE (simplificado sin contraseñas)
# -------------------
class Cliente(db.Model):
    __tablename__ = "Cliente"
    id_Cliente = db.Column(db.Integer, primary_key=True)
    nombre_Cliente = db.Column(db.String(100), nullable=False)
    email_Cliente = db.Column(db.String(100), nullable=False)
    telefono_Cliente = db.Column(db.String(20), nullable=False)

# -------------------
# MODELO MESA
# -------------------
class Mesa(db.Model):
    __tablename__ = "Mesa"
    id_Mesa = db.Column(db.Integer, primary_key=True)
    numero_Mesa = db.Column(db.Integer, unique=True, nullable=False)
    capacidad_Mesa = db.Column(db.Integer, nullable=False)
    estado_Mesa = db.Column(db.String(20), default="disponible")  # disponible, ocupada, reservada

# -------------------
# MODELO RESERVA
# -------------------
class Reserva(db.Model):
    __tablename__ = "Reserva"
    id_Reserva = db.Column(db.Integer, primary_key=True)
    id_Cliente = db.Column(db.Integer, db.ForeignKey('Cliente.id_Cliente'), nullable=False)
    id_Mesa = db.Column(db.Integer, db.ForeignKey('Mesa.id_Mesa'), nullable=False)
    fecha_Reserva = db.Column(db.Date, nullable=False)
    hora_Reserva = db.Column(db.Time, nullable=False)
    num_Personas = db.Column(db.Integer, nullable=False)
    estado_Reserva = db.Column(db.String(20), default="pendiente")  # pendiente, confirmada, cancelada
    
    # Relaciones
    cliente = db.relationship('Cliente', backref=db.backref('reservas', lazy=True))
    mesa = db.relationship('Mesa', backref=db.backref('reservas', lazy=True))

# -------------------
# ENDPOINTS CLIENTES (simplificado)
# -------------------

@app.route("/api/clientes", methods=["POST"])
def crear_cliente():
    try:
        data = request.get_json()
        nombre = data.get("nombre")
        email = data.get("email")
        telefono = data.get("telefono")
        
        if not all([nombre, email, telefono]):
            return jsonify({"message": "Faltan datos"}), 400
        
        nuevo_cliente = Cliente(
            nombre_Cliente=nombre,
            email_Cliente=email,
            telefono_Cliente=telefono
        )
        
        db.session.add(nuevo_cliente)
        db.session.commit()
        
        return jsonify({
            "message": "Cliente registrado con éxito",
            "id_Cliente": nuevo_cliente.id_Cliente
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error al registrar cliente", "error": str(e)}), 500

# -------------------
# ENDPOINTS MESAS
# -------------------

@app.route("/api/mesas", methods=["GET"])
def obtener_mesas():
    try:
        mesas = Mesa.query.all()
        return jsonify([{
            "id_Mesa": mesa.id_Mesa,
            "numero_Mesa": mesa.numero_Mesa,
            "capacidad_Mesa": mesa.capacidad_Mesa,
            "estado_Mesa": mesa.estado_Mesa
        } for mesa in mesas])
    except Exception as e:
        return jsonify({"message": "Error al obtener mesas", "error": str(e)}), 500

# -------------------
# ENDPOINTS RESERVAS (sin autenticación)
# -------------------

@app.route("/api/reservas", methods=["POST"])
def crear_reserva():
    try:
        data = request.get_json()
        print("[DEBUG] Datos recibidos en POST /api/reservas:", data)

        # Datos del cliente
        nombre_cliente = data.get("nombre_cliente")
        email_cliente = data.get("email_cliente")
        telefono_cliente = data.get("telefono_cliente")

        # Datos de la reserva
        id_Mesa = data.get("id_Mesa")
        fecha_Reserva = data.get("fecha_Reserva")
        hora_Reserva = data.get("hora_Reserva")
        num_Personas = data.get("num_Personas")

        if not all([nombre_cliente, email_cliente, telefono_cliente, id_Mesa, fecha_Reserva, hora_Reserva, num_Personas]):
            print("[ERROR] Faltan datos en la reserva:", data)
            return jsonify({"message": "Faltan datos", "data": data}), 400

        # Verificar que la mesa existe
        mesa = Mesa.query.get(id_Mesa)
        if not mesa:
            print(f"[ERROR] Mesa no encontrada: id_Mesa={id_Mesa}")
            return jsonify({"message": "Mesa no encontrada"}), 400

        # Verificar que el número de personas no exceda la capacidad de la mesa
        if int(num_Personas) > mesa.capacidad_Mesa:
            print(f"[ERROR] Exceso de personas: {num_Personas} > {mesa.capacidad_Mesa}")
            return jsonify({"message": f"La mesa solo tiene capacidad para {mesa.capacidad_Mesa} personas"}), 400

        # Verificar si la mesa está fuera de servicio (opcional, si usas estado_Mesa para eso)
        if mesa.estado_Mesa not in ["disponible", "reservada"]:
            print(f"[ERROR] Mesa fuera de servicio: id_Mesa={id_Mesa}, estado={mesa.estado_Mesa}")
            return jsonify({"message": "Mesa fuera de servicio"}), 400

        # Verificar si ya existe una reserva para esa mesa en esa fecha y hora
        fecha_dt = datetime.datetime.strptime(fecha_Reserva, '%Y-%m-%d').date()
        hora_dt = datetime.datetime.strptime(hora_Reserva, '%H:%M').time()
        reserva_existente = Reserva.query.filter_by(id_Mesa=id_Mesa, fecha_Reserva=fecha_dt, hora_Reserva=hora_dt).first()
        if reserva_existente:
            print(f"[ERROR] Ya existe una reserva para la mesa {id_Mesa} en {fecha_Reserva} {hora_Reserva}")
            return jsonify({"message": "La mesa ya está reservada para esa fecha y hora"}), 400

        # Crear o obtener cliente
        cliente = Cliente.query.filter_by(email_Cliente=email_cliente).first()
        if not cliente:
            cliente = Cliente(
                nombre_Cliente=nombre_cliente,
                email_Cliente=email_cliente,
                telefono_Cliente=telefono_cliente
            )
            db.session.add(cliente)
            db.session.flush()  # Para obtener el ID del cliente

        # Crear reserva
        nueva_reserva = Reserva(
            id_Cliente=cliente.id_Cliente,
            id_Mesa=id_Mesa,
            fecha_Reserva=fecha_dt,
            hora_Reserva=hora_dt,
            num_Personas=num_Personas
        )

        db.session.add(nueva_reserva)
        db.session.commit()
        print(f"[OK] Reserva creada: id={nueva_reserva.id_Reserva}")

        return jsonify({
            "message": "Reserva creada con éxito",
            "id_Reserva": nueva_reserva.id_Reserva,
            "numero_Mesa": mesa.numero_Mesa,
            "fecha_Reserva": fecha_Reserva,
            "hora_Reserva": hora_Reserva
        }), 201

    except Exception as e:
        db.session.rollback()
        print("[ERROR] Excepción al crear reserva:", str(e))
        return jsonify({"message": "Error al crear reserva", "error": str(e)}), 500

@app.route("/api/reservas", methods=["GET"])
def obtener_reservas():
    try:
        email = request.args.get('email')
        
        if email:
            # Buscar reservas por email del cliente
            cliente = Cliente.query.filter_by(email_Cliente=email).first()
            if not cliente:
                return jsonify([])
            
            reservas = Reserva.query.filter_by(id_Cliente=cliente.id_Cliente).all()
        else:
            # Obtener todas las reservas (para administración)
            reservas = Reserva.query.all()
        
        return jsonify([{
            "id_Reserva": reserva.id_Reserva,
            "id_Mesa": reserva.id_Mesa,
            "nombre_Cliente": reserva.cliente.nombre_Cliente,
            "email_Cliente": reserva.cliente.email_Cliente,
            "telefono_Cliente": reserva.cliente.telefono_Cliente,
            "numero_Mesa": reserva.mesa.numero_Mesa,
            "fecha_Reserva": reserva.fecha_Reserva.strftime('%Y-%m-%d'),
            "hora_Reserva": reserva.hora_Reserva.strftime('%H:%M'),
            "num_Personas": reserva.num_Personas,
            "estado_Reserva": reserva.estado_Reserva
        } for reserva in reservas])
        
    except Exception as e:
        return jsonify({"message": "Error al obtener reservas", "error": str(e)}), 500

@app.route("/api/reservas/<int:id>", methods=["PUT"])
def modificar_reserva(id):
    try:
        reserva = Reserva.query.get(id)
        if not reserva:
            return jsonify({"message": "Reserva no encontrada"}), 404
        
        data = request.get_json()
        
        if "estado_Reserva" in data:
            reserva.estado_Reserva = data["estado_Reserva"]
            
            # Si se cancela la reserva, liberar la mesa
            if data["estado_Reserva"] == "cancelada":
                mesa = Mesa.query.get(reserva.id_Mesa)
                mesa.estado_Mesa = "disponible"
        
        db.session.commit()
        
        return jsonify({"message": "Reserva actualizada con éxito"})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error al actualizar reserva", "error": str(e)}), 500

@app.route("/api/reservas/<int:id>", methods=["DELETE"])
def eliminar_reserva(id):
    try:
        reserva = Reserva.query.get(id)
        if not reserva:
            return jsonify({"message": "Reserva no encontrada"}), 404
        
        # Liberar la mesa
        mesa = Mesa.query.get(reserva.id_Mesa)
        mesa.estado_Mesa = "disponible"
        
        db.session.delete(reserva)
        db.session.commit()
        
        return jsonify({"message": "Reserva eliminada con éxito"})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error al eliminar reserva", "error": str(e)}), 500

# -------------------
# ENDPOINTS REPORTES
# -------------------

@app.route("/api/reportes/reservas", methods=["GET"])
def obtener_reportes_reservas():
    try:
        # Obtener parámetros de fecha
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        
        # Consultar reservas
        query = Reserva.query
        
        if fecha_inicio:
            fecha_inicio = datetime.datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            query = query.filter(Reserva.fecha_Reserva >= fecha_inicio)
        
        if fecha_fin:
            fecha_fin = datetime.datetime.strptime(fecha_fin, '%Y-%m-%d').date()
            query = query.filter(Reserva.fecha_Reserva <= fecha_fin)
        
        reservas = query.all()
        
        return jsonify([{
            "id_Reserva": reserva.id_Reserva,
            "nombre_Cliente": reserva.cliente.nombre_Cliente,
            "email_Cliente": reserva.cliente.email_Cliente,
            "telefono_Cliente": reserva.cliente.telefono_Cliente,
            "numero_Mesa": reserva.mesa.numero_Mesa,
            "fecha_Reserva": reserva.fecha_Reserva.strftime('%Y-%m-%d'),
            "hora_Reserva": reserva.hora_Reserva.strftime('%H:%M'),
            "num_Personas": reserva.num_Personas,
            "estado_Reserva": reserva.estado_Reserva
        } for reserva in reservas])
        
    except Exception as e:
        return jsonify({"message": "Error al obtener reportes", "error": str(e)}), 500

# -------------------
# RUTAS HTML
# -------------------

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/reservas")
def reservas_page():
    return render_template("reservas.html")

@app.route("/admin")
def admin_page():
    return render_template("admin.html")

# -------------------
# INICIALIZACIÓN
# -------------------

def crear_datos_iniciales():
    # Crear mesas si no existen
    if not Mesa.query.first():
        mesas = [
            Mesa(numero_Mesa=1, capacidad_Mesa=4),
            Mesa(numero_Mesa=2, capacidad_Mesa=2),
            Mesa(numero_Mesa=3, capacidad_Mesa=6),
            Mesa(numero_Mesa=4, capacidad_Mesa=4),
            Mesa(numero_Mesa=5, capacidad_Mesa=8),
            Mesa(numero_Mesa=6, capacidad_Mesa=2),
            Mesa(numero_Mesa=7, capacidad_Mesa=4),
            Mesa(numero_Mesa=8, capacidad_Mesa=6)
        ]
        db.session.add_all(mesas)
        db.session.commit()
        print("Mesas creadas exitosamente")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        crear_datos_iniciales()
    app.run(debug=True, port=5000)