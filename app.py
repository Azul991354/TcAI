from flask import Flask, request, jsonify
import os
import json
import secrets
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Habilitar CORS para que tu frontend en SPA pueda comunicarse sin problemas

# Archivo local para persistencia de datos (claves, prompts y memoria)
DATA_FILE = "tcai_database.json"

# System Prompt Base (identidad raíz inalterable del modelo)
CORE_IDENTITY_PROMPT = (
    "You are the TCAI Model 001 Lite. You were created by Azul991354. "
    "A user generated an API KEY for their own AI agent. "
    "The SYSTEM_PROMPT is for you to act as the person asks you to. "
    "For example, 'You are the AI MistyAI, you are an expert programmer, "
    "these are the terms of service...' Do you understand? Good."
)

def load_data():
    """Carga los datos almacenados en el archivo json"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_data(data):
    """Guarda los datos de forma persistente en disco"""
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)
    except:
        pass

@app.route("/")
def home():
    """Ruta de estado y verificación básica"""
    data = load_data()
    return f"TCAI Model 001 Lite Backend (Active). Agents registered: {len(data)}"

@app.route("/api/create-key", methods=["POST"])
def create_key():
    """Genera una API Key única con estructura tcAI_... y crea el espacio del agente."""
    data = load_data()
    new_key = f"tcAI_{secrets.token_hex(16)}"
    
    # Inicializa al agente con un system prompt predeterminado y memoria vacía
    data[new_key] = {
        "system_prompt": "You are a helpful AI assistant.",
        "knowledge": {}
    }
    
    save_data(data)
    return jsonify({
        "status": "success",
        "api_key": new_key,
        "message": "API Key created successfully. Store it safely."
    })

@app.route("/api/set-prompt", methods=["POST"])
def set_system_prompt():
    """Permite configurar o actualizar la variable system_prompt personalizada del usuario."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return jsonify({"error": "Missing Authorization Bearer header"}), 401
    
    token = auth_header.split(" ")[1]
    data = load_data()
    if token not in data:
        return jsonify({"error": "Invalid API Key"}), 403
        
    req_data = request.json or {}
    custom_prompt = req_data.get("system_prompt", "").strip()
    if not custom_prompt:
        return jsonify({"error": "System prompt cannot be empty"}), 400
        
    data[token]["system_prompt"] = custom_prompt
    save_data(data)
    
    return jsonify({
        "status": "success",
        "message": "Custom system prompt updated successfully."
    })

@app.route("/api/teach", methods=["POST"])
def teach_model():
    """Enseña un nuevo conocimiento (prompt -> respuesta) al agente"""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return jsonify({"error": "Missing Authorization Bearer header"}), 401
    
    token = auth_header.split(" ")[1]
    data = load_data()
    if token not in data:
        return jsonify({"error": "Invalid API Key"}), 403
        
    req_data = request.json or {}
    prompt_key = req_data.get("prompt", "").strip().lower()
    response_value = req_data.get("response", "").strip()
    
    if not prompt_key or not response_value:
        return jsonify({"error": "Missing 'prompt' or 'response'"}), 400
        
    data[token]["knowledge"][prompt_key] = response_value
    save_data(data)
    
    return jsonify({
        "status": "success",
        "message": f"Knowledge successfully learned for: '{prompt_key}'"
    })

@app.route("/api/chat", methods=["POST"])
def chat():
    """Procesa el chat combinando la identidad base y el system_prompt personalizado."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return jsonify({"error": "Missing Authorization Bearer header"}), 401
    
    token = auth_header.split(" ")[1]
    data = load_data()
    if token not in data:
        return jsonify({"error": "Invalid API Key"}), 403
        
    req_data = request.json or {}
    user_message = req_data.get("message", "").strip().lower()
    
    agent = data[token]
    user_custom_prompt = agent["system_prompt"]
    knowledge_base = agent["knowledge"]
    
    final_system_prompt = f"{CORE_IDENTITY_PROMPT}\nYour SYSTEM_PROMPT is: {user_custom_prompt}"
    reply = knowledge_base.get(user_message, "I don't have enough data on this yet. Teach me using /api/teach.")
    
    return jsonify({
        "active_system_prompt": final_system_prompt,
        "response": reply
    })

@app.route("/getres", methods=["POST"])
def get_response():
    """Endpoint directo /getres compatible con la estructura API KEY + Prompt."""
    auth_header = request.headers.get("Authorization", "")
    req_data = request.json or {}
    
    # Extraer la API Key ya sea del header Bearer o directamente del cuerpo JSON (api_key)
    token = None
    if auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    else:
        token = req_data.get("api_key")
        
    if not token:
        return jsonify({"error": "Missing Authorization Bearer or api_key"}), 401
        
    data = load_data()
    if token not in data:
        return jsonify({"error": "Invalid API Key"}), 403
        
    # Obtener el prompt o mensaje del usuario
    user_prompt = req_data.get("prompt", req_data.get("message", "")).strip()
    if not user_prompt:
        return jsonify({"error": "Missing 'prompt' in request body"}), 400
        
    agent = data[token]
    user_custom_prompt = agent["system_prompt"]
    knowledge_base = agent["knowledge"]
    
    # Combinar identidad base con el prompt del usuario
    final_system_prompt = f"{CORE_IDENTITY_PROMPT}\nYour SYSTEM_PROMPT is: {user_custom_prompt}"
    
    lower_prompt = user_prompt.lower()
    reply = knowledge_base.get(lower_prompt, "")
    
    if not reply:
        # Respuesta estructurada por defecto si no está en memoria
        reply = f"TCAI Model 001 Lite procesó tu consulta correctamente. Prompt recibido: '{user_prompt}'."

    return jsonify({
        "status": "success",
        "active_system_prompt": final_system_prompt,
        "response": reply,
        "code_snippet": "# Bloque de código generado por TCAI 001 Lite\ndef execute_task():\n    print('Ejecución exitosa desde /getres')"
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
