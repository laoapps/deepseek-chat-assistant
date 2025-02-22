from flask import Flask, request, jsonify
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import torch
import os
import redis
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

# Initialize Redis for conversation history
redis_client = redis.Redis(host="redis", port=6379, db=0)

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
    history = redis_client.get(f"conversation:{user_id}")
    if history:
        history = json.loads(history)
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
    redis_client.set(f"conversation:{user_id}", json.dumps(history))

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
