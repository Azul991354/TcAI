from flask import Flask, request, jsonify
import numpy as np
import threading
import time
import os
import json
import secrets

app = Flask(__name__)

KEYS_FILE = "tcai_keys.json"
WEIGHTS_FILE = "tcai_weights.json"

class TCAIModel001Lite:
    def __init__(self):
        self.experiencias = 0
        self.pesos = np.random.randn(4, 8)
        self.cargar_estado()

    def cargar_estado(self):
        if os.path.exists(WEIGHTS_FILE):
            try:
                with open(WEIGHTS_FILE, "r") as f:
                    data = json.load(f)
                    self.experiencias = data.get("experiencias", 0)
                    self.pesos = np.array(data.get("pesos", self.pesos.tolist()))
            except:
                pass

    def guardar_estado(self):
        try:
            with open(WEIGHTS_FILE, "w") as f:
                json.dump({"experiencias": self.experiencias, "pesos": self.pesos.tolist()}, f)
        except:
            pass

    def loop_aprendizaje(self):
        while True:
            self.pesos += np.random.randn(4, 8) * 0.01
            self.experiencias += 1
            self.guardar_estado()
            time.sleep(30)

# Gestion de API Keys
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

# Iniciar IA en segundo plano
tcai = TCAIModel001Lite()
threading.Thread(target=tcai.loop_aprendizaje, daemon=True).start()

@app.route("/")
def home():
    return f"TCAI Model 001 Lite activo. Experiencias: {tcai.experiencias}"

@app.route("/api/create-key", methods=["POST"])
def create_key():
    # Genera una llave unica con la estructura exacta solicitada
    nueva_key = f"tcAI_{secrets.token_hex(12)}"
    keys = cargar_keys()
    keys.append(nueva_key)
    guardar_keys(keys)
    return jsonify({"status": "success", "api_key": nueva_key, "mensaje": "Guarda tu key, no se volvera a mostrar."})

@app.route("/api/protected-action", methods=["POST"])
def protected_action():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return jsonify({"error": "Falta header de autorizacion Bearer"}), 401
    
    token = auth_header.split(" ")[1]
    keys = cargar_keys()
    
    if token not in keys:
        return jsonify({"error": "API Key invalida"}), 403

    return jsonify({"status": "ok", "mensaje": "Acceso concedido a TCAI", "experiencias": tcai.experiencias})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
