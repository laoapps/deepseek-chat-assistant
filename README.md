# Assistant - AI  Assistant

Assistant is a Dockerized AI  assistant powered by **DeepSeek-Chat**. It provides REST APIs for interacting with the AI model, fine-tuning it on specific topics, and storing conversation history in a PostgreSQL database.

---

## **Features**
- **Natural Language Processing**: Powered by DeepSeek-Chat, a state-of-the-art conversational AI model.
- **REST API**: APIs for chat and training.
- **PostgreSQL Integration**: Stores conversation history and user data.
- **Dockerized**: Containerized for easy deployment and scalability.
- **Fine-Tuning**: Train the assistant on specific topics for better performance.
- **Environment Variables**: Load PostgreSQL credentials and JWT secret from `.env`.

---

## **Requirements**

### **Hardware**
- **Minimum (CPU-only)**:
  - RAM: 16 GB
  - Storage: 20 GB (for model weights and dependencies)
- **Recommended (GPU)**:
  - GPU: NVIDIA GPU with at least 16 GB VRAM (e.g., A100, V100, or RTX 3090)
  - RAM: 32 GB
  - Storage: 50 GB (for model weights and dependencies)

### **Software**
- Docker (with NVIDIA Container Toolkit for GPU support)
- Docker Compose
- Python 3.8+
- Node.js 18+ (for the wrapper)

---

## **Setup**

### **1. Clone the Repository**
```bash
git clone https://github.com/your-username/assistant.git
cd assistant
