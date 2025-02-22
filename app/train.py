from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments
from datasets import load_dataset
import torch

# Load the model and tokenizer
MODEL_NAME = "deepseek-ai/deepseek-chat-7b"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, torch_dtype=torch.float16)
model = model.to("cuda" if torch.cuda.is_available() else "cpu")

# Load training data
dataset = load_dataset("json", data_files="app/data/training_data.json")

# Tokenize the dataset
def tokenize_function(examples):
    return tokenizer(examples["text"], padding="max_length", truncation=True)

tokenized_dataset = dataset.map(tokenize_function, batched=True)

# Define training arguments
training_args = TrainingArguments(
    output_dir="app/models/fine-tuned",
    per_device_train_batch_size=2,
    num_train_epochs=1,
    save_steps=10_000,
    save_total_limit=2,
)

# Initialize the Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset["train"],
)

# Fine-tune the model
trainer.train()

# Save the fine-tuned model
trainer.save_model("app/models/fine-tuned")
