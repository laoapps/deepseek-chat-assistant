export interface ChatRequest {
    message: string;
    user_id: string;
}

export interface TrainRequest {
    data: Array<{ text: string }>;
}

export interface Conversation {
    user_id: string;
    history: Array<{ role: "user" | "assistant"; content: string }>;
}
