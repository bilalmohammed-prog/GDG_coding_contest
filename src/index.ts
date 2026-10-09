// src/index.ts
import 'dotenv/config';
import express from 'express';
import { submissionQueue } from './queue.js';
import { supabase } from './supabase.js';
import { PROBLEM_REGISTRY } from './problems/index.js';

const app = express();
app.use(express.json());


// 1. Submit Code Route
app.post('/api/submit', async (req, res) => {
  const { code, language, problemId, user_id } = req.body;

  if (!code || !language || !problemId || !user_id) {
    return res.status(400).json({ error: 'Missing code, language, problemId, or user_id' });
  }

  if (!PROBLEM_REGISTRY[problemId]) {
    return res.status(400).json({ error: `Unknown problemId: ${problemId}` });
  }

  const job = await submissionQueue.add('eval-job', {
    code,
    language,
    problemId,
    user_id,
    timestamp: Date.now(),
  });

  return res.json({
    status: 'QUEUED',
    submissionId: job.id,
  });
});

// 2. Poll Status Route (Optional endpoint to check job state)
app.get('/api/submission/:id', async (req, res) => {
  const job = await submissionQueue.getJob(req.params.id);

  if (!job) {
    return res.status(404).json({ error: 'Submission not found' });
  }

  const state = await job.getState();

  // BullMQ can report state=completed a moment before returnvalue
  // is fully persisted. Re-fetch once if we see that race.
  let returnvalue = job.returnvalue;
  if (state === 'completed' && !returnvalue) {
    const refreshed = await submissionQueue.getJob(req.params.id);
    returnvalue = refreshed?.returnvalue ?? null;
  }

  return res.json({
    id: job.id,
    state,
    result: returnvalue || null,
    failedReason: job.failedReason || null,
  });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`🚀 API Server running on http://localhost:${PORT}`);
});


export default app;