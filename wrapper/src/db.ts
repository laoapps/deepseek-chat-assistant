import { Pool } from "pg";

const pool = new Pool({
    user: "postgres",
    host: "postgres",
    database: "assistant",
    password: "password",
    port: 5432,
});

export const connectDB = async () => {
    try {
        await pool.query(`
            CREATE TABLE IF NOT EXISTS conversations (
                user_id TEXT PRIMARY KEY,
                history JSONB NOT NULL
            );
        `);
        console.log("Connected to PostgreSQL");
    } catch (error) {
        console.error("Failed to connect to PostgreSQL", error);
    }
};

export const saveConversation = async (user_id: string, message: string, response: string) => {
    const history = await getConversationHistory(user_id);
    history.push({ role: "user", content: message });
    history.push({ role: "assistant", content: response });

    await pool.query(
        "INSERT INTO conversations (user_id, history) VALUES ($1, $2) ON CONFLICT (user_id) DO UPDATE SET history = $2",
        [user_id, JSON.stringify(history)]
    );
};

export const getConversationHistory = async (user_id: string) => {
    const result = await pool.query("SELECT history FROM conversations WHERE user_id = $1", [user_id]);
    return result.rows[0]?.history || [];
};
