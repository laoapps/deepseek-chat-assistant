from flask import Flask, request, jsonify
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import torch
import os
import psycopg2
import json

# Initialize Flask app
app = Flask(__name__)

# Load DeepSeek-Chat model and tokenizer
MODEL_NAME = "deepseek-ai/deepseek-chat-7b"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, torch_dtype=torch.float16)
model = model.to("cuda" if torch.cuda.is_available() else "cpu")

# Load fine-tuned model (if available)
FINE_TUNED_MODEL_PATH = "app/models/fine-tuned"
if os.path.exists(FINE_TUNED_MODEL_PATH):
    model = AutoModelForCausalLM.from_pretrained(FINE_TUNED_MODEL_PATH, torch_dtype=torch.float16)
    model = model.to("cuda" if torch.cuda.is_available() else "cpu")

# PostgreSQL connection
def get_db_connection():
    return psycopg2.connect(
        host="postgres",
        database="assistant",
        user="postgres",
        password="password"
    )

@app.route("/chat", methods=["POST"])
def chat():
    """
    API endpoint for handling chat requests.
    """
    user_input = request.json.get("message")
    user_id = request.json.get("user_id")
    if not user_input or not user_id:
        return jsonify({"error": "Missing message or user_id"}), 400

    # Retrieve conversation history
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT history FROM conversations WHERE user_id = %s", (user_id,))
    history = cur.fetchone()
    if history:
        history = json.loads(history[0])
    else:
        history = []

    # Add user input to history
    history.append({"role": "user", "content": user_input})

    # Generate response
    inputs = tokenizer(user_input, return_tensors="pt").to(model.device)
    outputs = model.generate(**inputs, max_length=100, num_return_sequences=1)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Add assistant response to history
    history.append({"role": "assistant", "content": response})
    cur.execute(
        "INSERT INTO conversations (user_id, history) VALUES (%s, %s) ON CONFLICT (user_id) DO UPDATE SET history = %s",
        (user_id, json.dumps(history), json.dumps(history))
    )
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"response": response})

@app.route("/train", methods=["POST"])
def train():
    """
    API endpoint for training the assistant on a specific topic.
    """
    training_data = request.json.get("data")
    if not training_data:
        return jsonify({"error": "No training data provided"}), 400

    with open("app/data/training_data.json", "w") as f:
        json.dump(training_data, f)

    os.system("python3 app/train.py")
    return jsonify({"message": "Training completed successfully"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
