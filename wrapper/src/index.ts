import express, { Request, Response } from "express";
import axios from "axios";
import authMiddleware from "./auth";
import rateLimit from "./rateLimit";
import { connectDB, saveConversation, getConversationHistory } from "./db";
import { logRequest } from "./analytics";

const app = express();
app.use(express.json());

const ASSISTANT_API_URL = process.env.ASSISTANT_API_URL || "http://localhost:5000";

// Middleware
app.use(authMiddleware);
app.use(rateLimit);

// Chat endpoint
app.post("/chat", async (req: Request, res: Response) => {
    logRequest(req);
    const { message, user_id } = req.body;
    if (!message || !user_id) {
        return res.status(400).json({ error: "Missing message or user_id" });
    }

    try {
        const response = await axios.post(`${ASSISTANT_API_URL}/chat`, { message, user_id });
        await saveConversation(user_id, message, response.data.response);
        res.json(response.data);
    } catch (error) {
        res.status(500).json({ error: "Failed to communicate with the assistant" });
    }
});

// Train endpoint
app.post("/train", async (req: Request, res: Response) => {
    logRequest(req);
    const { data } = req.body;
    if (!data) {
        return res.status(400).json({ error: "No training data provided" });
    }

    try {
        const response = await axios.post(`${ASSISTANT_API_URL}/train`, { data });
        res.json(response.data);
    } catch (error) {
        res.status(500).json({ error: "Failed to train the assistant" });
    }
});

// Start server
const PORT = 3000;
app.listen(PORT, async () => {
    await connectDB();
    console.log(`Wrapper API running on http://localhost:${PORT}`);
});
