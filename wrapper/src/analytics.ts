import { Request } from "express";
import winston from "winston";

// Configure Winston logger
const logger = winston.createLogger({
    level: "info",
    format: winston.format.json(),
    transports: [
        new winston.transports.Console(),
        new winston.transports.File({ filename: "logs/requests.log" }),
    ],
});

// Log API requests
export const logRequest = (req: Request) => {
    logger.info({
        method: req.method,
        url: req.url,
        timestamp: new Date().toISOString(),
    });
};
