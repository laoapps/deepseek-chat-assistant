from flask import Flask, request, jsonify
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# Initialize Flask app
app = Flask(__name__)

# Load DeepSeek-Chat model and tokenizer
MODEL_NAME = "deepseek-ai/deepseek-chat-7b"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, torch_dtype=torch.float16)
model = model.to("cuda" if torch.cuda.is_available() else "cpu")

@app.route("/chat", methods=["POST"])
def chat():
    """
    API endpoint for handling chat requests.
    """
    # Get user input from the request
    user_input = request.json.get("message")
    if not user_input:
        return jsonify({"error": "No message provided"}), 400

    # Tokenize input and generate response
    inputs = tokenizer(user_input, return_tensors="pt").to(model.device)
    outputs = model.generate(**inputs, max_length=100, num_return_sequences=1)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Return the response
    return jsonify({"response": response})

if __name__ == "__main__":
    # Run the Flask app
    app.run(host="0.0.0.0", port=5000)
