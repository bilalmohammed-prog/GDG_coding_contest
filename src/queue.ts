// src/queue.ts
import { Queue } from 'bullmq';
import { Redis } from 'ioredis'; // Use named import instead of default import

export const redisConnection = new Redis({
  host: process.env.REDIS_HOST || '127.0.0.1',
  port: Number(process.env.REDIS_PORT) || 6379,
  maxRetriesPerRequest: null, // Required by BullMQ
});

// Create the submission queue
export const submissionQueue = new Queue('code-submissions', {
  connection: redisConnection,
});