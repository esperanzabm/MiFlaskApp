from flask import Flask, jsonify, request

app = Flask(__name__)

# -------------------------------
# 🌿 Base de datos plantas
# -------------------------------
plants = [
    {"id": 1, "name": "Lavanda", "species": "Lavandula", "sunlight": "full", "is_indoor": False},
    {"id": 2, "name": "Helecho", "species": "Nephrolepis exaltata", "sunlight": "partial", "is_indoor": True},
    {"id": 3, "name": "Cactus", "species": "Echinocactus grusonii", "sunlight": "full", "is_indoor": False},
    {"id": 4, "name": "Poto", "species": "Epipremnum aureum", "sunlight": "partial", "is_indoor": True},
    {"id": 5, "name": "Romero", "species": "Salvia rosmarinus", "sunlight": "full", "is_indoor": False},
]

# -------------------------------
# 🌼 1. Ruta base: inicio
# -------------------------------
@app.route("/")
def home():
    return jsonify({
        "message": "Bienvenida a la API de Plantas 🌿",
        "endpoints": {
            "/plants": "Lista todas las plantas o aplica filtros",
            "/plants/<id>": "Muestra una planta específica por ID"
        }
    })

# -------------------------------
# 🌱 2. Ruta para listar y filtrar plantas
# -------------------------------
@app.route("/plants", methods=["GET"])
def get_plants():
    sunlight = request.args.get("sunlight")
    is_indoor = request.args.get("is_indoor")
    species = request.args.get("species")

    filtered = plants

    # Filtrado por tipo de luz
    if sunlight:
        filtered = [p for p in filtered if p["sunlight"] == sunlight]

    # Filtrado por interior/exterior
    if is_indoor:
        if is_indoor.lower() == "true":
            filtered = [p for p in filtered if p["is_indoor"] is True]
        elif is_indoor.lower() == "false":
            filtered = [p for p in filtered if p["is_indoor"] is False]

    # Filtrado por especie
    if species:
        filtered = [p for p in filtered if species.lower() in p["species"].lower()]

    return jsonify(filtered)

# -------------------------------
# 🌵 3. Ruta para obtener planta por ID
# -------------------------------
@app.route("/plants/<int:plant_id>", methods=["GET"])
def get_plant_by_id(plant_id):
    for plant in plants:
        if plant["id"] == plant_id:
            return jsonify(plant)
    return jsonify({"error": "Planta no encontrada"}), 404

# Endpoint: POST /plants -> crear nueva planta (valida campos)
@app.route("/plants", methods=["POST"])
def create_plant():
    # Forzamos JSON válido
    try:
        data = request.get_json(force=True)
    except Exception:
        return jsonify({"error": "Se requiere JSON válido en el body"}), 400

    # Campos obligatorios
    required = ["name", "species", "sunlight", "is_indoor"]
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({"error": "Faltan campos", "missing": missing}), 400

    # Normalizar is_indoor (acepta bool, "true"/"false", 1/0)
    raw = data["is_indoor"]
    if isinstance(raw, bool):
        is_indoor = raw
    elif isinstance(raw, (int, float)):
        is_indoor = bool(int(raw))
    elif isinstance(raw, str):
        val = raw.strip().lower()
        if val in ("true", "1", "yes", "y"):
            is_indoor = True
        elif val in ("false", "0", "no", "n"):
            is_indoor = False
        else:
            return jsonify({"error": "is_indoor inválido; use true/false"}), 400
    else:
        return jsonify({"error": "is_indoor debe ser booleano"}), 400

    # Generar nuevo id
    new_id = max((p["id"] for p in plants), default=0) + 1

    new_plant = {
        "id": new_id,
        "name": data["name"],
        "species": data["species"],
        "sunlight": data["sunlight"],
        "is_indoor": is_indoor
    }

    plants.append(new_plant)
    return jsonify(new_plant), 201

# Endpoint: DELETE /plants/<int:plant_id> -> elimina una planta por su id
@app.route("/plants/<int:plant_id>", methods=["DELETE"])
def delete_plant(plant_id):
    global plants
    original_len = len(plants)
    plants = [p for p in plants if p["id"] != plant_id]
    if len(plants) == original_len:
        # no se eliminó nada -> id no encontrado
        return jsonify({"error": "Planta no encontrada"}), 404
    # eliminado OK: 204 No Content (sin cuerpo)
    return "", 204

# -------------------------------
# 🚀 Ejecución del servidor
# -------------------------------
if __name__ == "__main__":
    app.run(debug=True)