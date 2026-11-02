from flask import Flask, request, jsonify
import os
import json
import secrets

app = Flask(__name__)

KEYS_FILE = "tcai_keys.json"
MEMORY_FILE = "tcai_conocimiento.json"

# gestiónsita api keys
def cargar_keys():
    if os.path.exists(KEYS_FILE):
        try:
            with open(KEYS_FILE, "r") as f:
                return json.load(f)
        except:
            return []
    return []

def guardar_keys(keys):
    with open(KEYS_FILE, "w") as f:
        json.dump(keys, f)

# aprender escribir y Código 
def cargar_memoria():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def guardar_memoria(memoria):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memoria, f, indent=4)

@app.route("/")
def home():
    memoria = cargar_memoria()
    return f"TCAI Model 001 Lite activo. Conceptos aprendidos: {len(memoria)}"

# uno crear apikey nueva
@app.route("/api/create-key", methods=["POST"])
def create_key():
    nueva_key = f"tcAI_{secrets.token_hex(12)}"
    keys = cargar_keys()
    keys.append(nueva_key)
    guardar_keys(keys)
    return jsonify({"status": "success", "api_key": nueva_key, "mensaje": "Guarda tu key, no se volvera a mostrar."})

# dos enseñar  un concepto o comando de programación
@app.route("/api/aprender", methods=["POST"])
def aprender():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return jsonify({"error": "Falta token de autorización"}), 401
    
    token = auth_header.split(" ")[1]
    if token not in cargar_keys():
        return jsonify({"error": "API Key inválida"}), 403

    data = request.json
    prompt = data.get("prompt", "").strip()
    respuesta = data.get("respuesta", "").strip()

    if not prompt or not respuesta:
        return jsonify({"error": "Faltan datos: envia 'prompt' y 'respuesta'"}), 400

    memoria = cargar_memoria()
    memoria[prompt.lower()] = respuesta
    guardar_memoria(memoria)

    return jsonify({"status": "success", "mensaje": f"¡Concepto '{prompt}' aprendido con éxito!"})

# tres preguntar a la ia (requiere apikey)
@app.route("/api/preguntar", methods=["POST"])
def preguntar():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return jsonify({"error": "Falta token de autorización"}), 401
    
    token = auth_header.split(" ")[1]
    if token not in cargar_keys():
        return jsonify({"error": "API Key inválida"}), 403

    data = request.json
    prompt = data.get("prompt", "").strip().lower()

    memoria = cargar_memoria()
    if prompt in memoria:
        return jsonify({"respuesta": memoria[prompt]})
    
    return jsonify({"respuesta": "Aún no he aprendido sobre eso. Enséñame usando /api/aprender"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
