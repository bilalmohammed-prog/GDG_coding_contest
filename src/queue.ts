import { Queue } from 'bullmq';
import { Redis } from 'ioredis';

export const redisConnection = new Redis(process.env.UPSTASH_REDIS_REST_URL!, {
  maxRetriesPerRequest: null,
});

export const submissionQueue = new Queue('code-submissions', {
  connection: redisConnection,
});