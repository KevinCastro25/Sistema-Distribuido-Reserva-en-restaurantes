from flask import request, jsonify, render_template
import datetime
from . import reservas_bp
from models import db, Cliente, Mesa, Reserva   # importa de models.py global

# -------------------
# ENDPOINTS CLIENTES
# -------------------
@reservas_bp.route("/clientes", methods=["POST"])
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
@reservas_bp.route("/mesas", methods=["GET"])
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
# ENDPOINTS RESERVAS
# -------------------
@reservas_bp.route("/reservas", methods=["POST"])
def crear_reserva():
    try:
        data = request.get_json()
        nombre_cliente = data.get("nombre_cliente")
        email_cliente = data.get("email_cliente")
        telefono_cliente = data.get("telefono_cliente")
        id_Mesa = data.get("id_Mesa")
        fecha_Reserva = data.get("fecha_Reserva")
        hora_Reserva = data.get("hora_Reserva")
        num_Personas = data.get("num_Personas")

        if not all([nombre_cliente, email_cliente, telefono_cliente, id_Mesa, fecha_Reserva, hora_Reserva, num_Personas]):
            return jsonify({"message": "Faltan datos"}), 400

        # Validaciones
        mesa = Mesa.query.get(id_Mesa)
        if not mesa:
            return jsonify({"message": "Mesa no encontrada"}), 400
        if int(num_Personas) > mesa.capacidad_Mesa:
            return jsonify({"message": f"La mesa solo tiene capacidad para {mesa.capacidad_Mesa} personas"}), 400

        fecha_dt = datetime.datetime.strptime(fecha_Reserva, '%Y-%m-%d').date()
        hora_dt = datetime.datetime.strptime(hora_Reserva, '%H:%M').time()
        reserva_existente = Reserva.query.filter_by(id_Mesa=id_Mesa, fecha_Reserva=fecha_dt, hora_Reserva=hora_dt).first()
        if reserva_existente:
            return jsonify({"message": "La mesa ya está reservada para esa fecha y hora"}), 400

        # Crear/obtener cliente
        cliente = Cliente.query.filter_by(email_Cliente=email_cliente).first()
        if not cliente:
            cliente = Cliente(
                nombre_Cliente=nombre_cliente,
                email_Cliente=email_cliente,
                telefono_Cliente=telefono_cliente
            )
            db.session.add(cliente)
            db.session.flush()

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

        return jsonify({
            "message": "Reserva creada con éxito",
            "id_Reserva": nueva_reserva.id_Reserva,
            "numero_Mesa": mesa.numero_Mesa,
            "fecha_Reserva": fecha_Reserva,
            "hora_Reserva": hora_Reserva
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error al crear reserva", "error": str(e)}), 500


@reservas_bp.route("/reservas", methods=["GET"])
def obtener_reservas():
    try:
        email = request.args.get('email')
        if email:
            cliente = Cliente.query.filter_by(email_Cliente=email).first()
            if not cliente:
                return jsonify([])
            reservas = Reserva.query.filter_by(id_Cliente=cliente.id_Cliente).all()
        else:
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


# -------------------
# VISTAS HTML
# -------------------
@reservas_bp.route("/")
def reservas_page():
    return render_template("reservas.html")

@reservas_bp.route("/home")
def index():
    return render_template("index.html")

@reservas_bp.route("/admin")
def admin_page():
    return render_template("admin.html")