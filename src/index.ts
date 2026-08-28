// src/index.ts
import 'dotenv/config';
import express from 'express';
import { submissionQueue } from './queue.js';
import { supabase } from './supabase.js';

const app = express();
app.use(express.json());
app.get('/users', async (_req, res) => {
  const { data, error } = await supabase
    .from('users')
    .select('*');

  if (error) {
    return res.status(500).json({ error: error.message });
  }

  res.json(data);
});



// 1. Submit Code Route
app.post('/api/submit', async (req, res) => {
  const { code, language, problemId } = req.body;

  if (!code || !language) {
    return res.status(400).json({ error: 'Missing code or language' });
  }

  // Add job to BullMQ queue
  const job = await submissionQueue.add('eval-job', {
    code,
    language,
    problemId: problemId || 'default-problem',
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
  return res.json({
    id: job.id,
    state, // 'completed', 'failed', 'active', 'waiting'
    result: job.returnvalue || null,
    failedReason: job.failedReason || null,
  });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`🚀 API Server running on http://localhost:${PORT}`);
});