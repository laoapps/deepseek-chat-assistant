import os
from flask import Flask, request, jsonify
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import psycopg2
import json

# Initialize Flask app
app = Flask(__name__)

# Load environment variables
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "yourpassword")
POSTGRES_DB = os.getenv("POSTGRES_DB", "assistant")

# Define the model name and local path
MODEL_NAME = "deepseek-ai/deepseek-chat-7b"
MODEL_LOCAL_PATH = "app/models/deepseek-chat-7b"

# Check if the model is already downloaded locally
if not os.path.exists(MODEL_LOCAL_PATH):
    print("Downloading DeepSeek model...")
    # Download the model and tokenizer
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, torch_dtype=torch.float16)

    # Save the model and tokenizer locally
    model.save_pretrained(MODEL_LOCAL_PATH)
    tokenizer.save_pretrained(MODEL_LOCAL_PATH)
    print("Model downloaded and saved locally.")
else:
    print("Loading DeepSeek model from local storage...")
    # Load the model and tokenizer from local storage
    tokenizer = AutoTokenizer.from_pretrained(MODEL_LOCAL_PATH)
    model = AutoModelForCausalLM.from_pretrained(MODEL_LOCAL_PATH, torch_dtype=torch.float16)

# Move the model to GPU if available
device = "cuda" if torch.cuda.is_available() else "cpu"
model = model.to(device)
print(f"Model loaded on device: {device}")

# PostgreSQL connection
def get_db_connection():
    return psycopg2.connect(
        host="postgres",
        database=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD
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
    inputs = tokenizer(user_input, return_tensors="pt").to(device)
    outputs = model.generate(**inputs, max_length=100, num_return_sequences=1)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Add assistant response to history
    history.append({"role": "assistant", "content": response})
    cur.execute(
        "INSERT INTO conversations (user_id, history) VALUES (%s, %s) ON CONFLICT (user_id) DO UPDATE SET history = %s",
        (user_id, json.dumps(history), json.dumps(history))
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

    # Save training data to a file
    with open("app/data/training_data.json", "w") as f:
        json.dump(training_data, f)

    # Fine-tune the model (this is a placeholder for actual fine-tuning logic)
    # In a real implementation, you would use a training script here.
    os.system("python3 app/train.py")
    return jsonify({"message": "Training completed successfully"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
