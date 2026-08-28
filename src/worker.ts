// src/worker.ts
import { Worker, Job } from 'bullmq';
import { redisConnection } from './queue.js';
import { exec } from 'child_process';
import util from 'util';
import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const execPromise = util.promisify(exec);
const WORKER_CONCURRENCY = 5;

export const worker = new Worker(
  'code-submissions',
  async (job: Job) => {
    const { code, language } = job.data;
    const jobId = job.id;

    console.log(`[Worker] Executing submission #${jobId}`);

    // Create temp directory for this run
    const tmpDir = path.join(__dirname, '../tmp', `job_${jobId}`);
    await fs.mkdir(tmpDir, { recursive: true });

    let result = {
      status: 'ACCEPTED',
      output: '',
      error: '',
      executionTimeMs: 0,
    };

    const startTime = Date.now();

    try {
      if (language === 'python') {
        const filePath = path.join(tmpDir, 'solution.py');
        await fs.writeFile(filePath, code);

        // Docker execution with hard constraints
        const dockerCmd = `docker run --rm \
          --memory=128m \
          --cpus=0.5 \
          --pids-limit=20 \
          --network=none \
          -v "${filePath}:/app/solution.py:ro" \
          python:3.10-slim \
          timeout 3s python /app/solution.py`;

        const { stdout, stderr } = await execPromise(dockerCmd);
        
        result.output = stdout.trim();
        // Filter Docker pull output if present
        result.error = stderr
          .split('\n')
          .filter((line) => !line.includes('Unable to find image') && !line.includes('Pulling') && !line.includes('Digest:') && !line.includes('Status:'))
          .join('\n')
          .trim();
      } else {
        throw new Error(`Unsupported language: ${language}`);
      }
    } catch (err: any) {
      // Exit code 124 is returned by GNU timeout when a process exceeds 3s
      if (err.code === 124 || err.killed || err.signal === 'SIGTERM') {
        result.status = 'TIME_LIMIT_EXCEEDED';
        result.error = 'Time Limit Exceeded (3.0s limit reached)';
      } else {
        result.status = 'RUNTIME_ERROR';
        result.error = err.stderr ? err.stderr.trim() : err.message;
      }
    } finally {
      result.executionTimeMs = Date.now() - startTime;
      // Clean up temp files
      await fs.rm(tmpDir, { recursive: true, force: true });
    }

    console.log(`[Worker] Finished #${jobId}: ${result.status} (${result.executionTimeMs}ms)`);
    return result;
  },
  {
    connection: redisConnection,
    concurrency: WORKER_CONCURRENCY,
  }
);