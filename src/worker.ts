// src/worker.ts

import { Worker, Job } from 'bullmq';
import { redisConnection } from './queue.js';
import { execFile } from 'child_process';
import util from 'util';
import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';
import {
  TEST_CASES,
  getExpectedAnswer,
  validateOutput,
  answersMatch,
} from './problems/topKFrequent.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const execFilePromise = util.promisify(execFile);

const WORKER_CONCURRENCY = 5;
const TIME_LIMIT_SECONDS = 3;
// Wall-clock budget for the whole container (all test cases).
// Must exceed TIME_LIMIT_SECONDS * TEST_CASES.length with headroom
// for interpreter startup, or a run of legitimately-slow-but-passing
// tests could get killed by the outer timeout instead of alarm().
const CONTAINER_TIMEOUT_SECONDS = 30;

// ============================================================
// Problem: LeetCode 347 - Top K Frequent Elements
// ============================================================

type TestCase = {
  nums: number[];
  k: number;
};

type JudgeResult = {
  status: 'ACCEPTED' | 'WRONG_ANSWER' | 'TIME_LIMIT_EXCEEDED' | 'RUNTIME_ERROR';
  output: string;
  error: string;
  executionTimeMs: number;
};

type DriverTestResult =
  | { ok: true; output: unknown }
  | { ok: false; error: string };

// ------------------------------------------------------------
// Build the driver script that runs INSIDE the container.
//
// One process, one interpreter start, loops over every test
// case, enforces a per-test wall-clock limit with signal.alarm
// so one slow/hanging test can't block the rest of the batch.
// ------------------------------------------------------------

function buildDriverScript(contestantCode: string): string {
  return `
import sys
import json
import signal

class TestTimeout(Exception):
    pass

def __timeout_handler(signum, frame):
    raise TestTimeout()

signal.signal(signal.SIGALRM, __timeout_handler)

${contestantCode}

def __run_all():
    with open('/app/tests.json') as f:
        tests = json.load(f)

    results = []

    for test in tests:
        nums = test["nums"]
        k = test["k"]

        signal.alarm(${TIME_LIMIT_SECONDS})

        try:
            output = topKFrequent(nums, k)
            results.append({"ok": True, "output": output})
        except TestTimeout:
            results.append({"ok": False, "error": "TIME_LIMIT_EXCEEDED"})
        except Exception as e:
            results.append({"ok": False, "error": f"{type(e).__name__}: {e}"})
        finally:
            signal.alarm(0)

    print(json.dumps(results))

if __name__ == "__main__":
    __run_all()
`;
}

// ------------------------------------------------------------
// Worker
// ------------------------------------------------------------

export const worker = new Worker(
  'code-submissions',

  async (job: Job) => {
    const { code, language } = job.data;
    const jobId = job.id;

    console.log(`[Worker PID=${process.pid}] Executing submission #${jobId}`);

    const tmpDir = path.join(__dirname, '../tmp', `job_${jobId}`);
    await fs.mkdir(tmpDir, { recursive: true });

    const startTime = Date.now();

    let finalResult: JudgeResult = {
      status: 'ACCEPTED',
      output: '',
      error: '',
      executionTimeMs: 0,
    };

    try {
      if (language !== 'python') {
        throw new Error(`Unsupported language: ${language}`);
      }

      const driverScript = buildDriverScript(code);
      const solutionPath = path.join(tmpDir, 'driver.py');
      await fs.writeFile(solutionPath, driverScript);

      const testsPath = path.join(tmpDir, 'tests.json');
      await fs.writeFile(testsPath, JSON.stringify(TEST_CASES));

      // --------------------------------------------------------
      // ONE container for the whole submission. All test cases
      // run inside it, in-process, driven by driver.py.
      //
      // execFile (not exec) => no shell, no quoting bugs, no
      // injection surface for anything derived from contestant
      // input or file paths.
      // --------------------------------------------------------

      const dockerArgs = [
        'run', '--rm',
        '--memory=128m',
        '--cpus=0.5',
        '--pids-limit=20',
        '--network=none',
        '--read-only',
        '--tmpfs', '/tmp:rw,noexec,nosuid,size=16m',
        '-v', `${solutionPath}:/app/driver.py:ro`,
        '-v', `${testsPath}:/app/tests.json:ro`,
        'python:3.10-slim',
        'timeout', `${CONTAINER_TIMEOUT_SECONDS}s`,
        'python', '/app/driver.py',
      ];

      let stdout = '';

      try {
        const result = await execFilePromise('docker', dockerArgs, {
          maxBuffer: 10 * 1024 * 1024,
        });

        stdout = result.stdout;
      } catch (err: any) {
        // Outer `timeout` firing here means the WHOLE container
        // blew the container-level budget — e.g. an infinite loop
        // that also swallows/ignores SIGALRM, or driver.py itself
        // hanging outside the per-test alarm window. Per-test
        // TLEs are caught inside driver.py and show up as normal
        // JSON output, not as a process failure.
        if (err.code === 124 || err.signal === 'SIGTERM' || err.killed) {
          finalResult.status = 'TIME_LIMIT_EXCEEDED';
          finalResult.error = `Container exceeded ${CONTAINER_TIMEOUT_SECONDS}s overall limit`;
        } else {
          finalResult.status = 'RUNTIME_ERROR';
          finalResult.error =
            err.stderr?.trim() || err.stdout?.trim() || err.message;
        }

        throw new Error('__handled__'); // short-circuit to finally, result already set
      }

      // ------------------------------------------------------
      // Parse driver output: array of per-test results, in
      // the same order as TEST_CASES.
      // ------------------------------------------------------

      let driverResults: DriverTestResult[];

      try {
        driverResults = JSON.parse(stdout.trim());
        if (!Array.isArray(driverResults)) {
          throw new Error('Driver output must be a JSON array');
        }
      } catch (err: any) {
        finalResult.status = 'RUNTIME_ERROR';
        finalResult.error = `Malformed driver output: ${err.message}`;
        throw new Error('__handled__');
      }

      // ------------------------------------------------------
      // Walk results, fail-fast on first bad test case
      // (matches prior behavior: stop at first WA/TLE/RE).
      // ------------------------------------------------------

      for (let i = 0; i < TEST_CASES.length; i++) {
        const testCase = TEST_CASES[i]!;
        const testResult = driverResults[i];

        if (!testResult) {
          finalResult.status = 'RUNTIME_ERROR';
          finalResult.error = `Missing result for test case ${i + 1}`;
          break;
        }

        if (!testResult.ok) {
          if (testResult.error === 'TIME_LIMIT_EXCEEDED') {
            finalResult.status = 'TIME_LIMIT_EXCEEDED';
            finalResult.error = `Time Limit Exceeded on test case ${i + 1} (${TIME_LIMIT_SECONDS}.0s limit reached)`;
          } else {
            finalResult.status = 'RUNTIME_ERROR';
            finalResult.error = `Runtime error on test case ${i + 1}: ${testResult.error}`;
          }
          break;
        }

        let actual: number[];

        try {
          actual = validateOutput(testResult.output);
        } catch (err: any) {
          finalResult.status = 'WRONG_ANSWER';
          finalResult.error = `Invalid output on test case ${i + 1}: ${err.message}`;
          break;
        }

        const expected = getExpectedAnswer(testCase.nums, testCase.k);

        if (!answersMatch(actual, expected)) {
          finalResult.status = 'WRONG_ANSWER';
          finalResult.error = `Wrong answer on test case ${i + 1}`;
          finalResult.output = JSON.stringify({ expected, actual });
          break;
        }

        console.log(
          `[Worker PID=${process.pid}] Job #${jobId} test ${i + 1} passed`,
        );
      }
    } catch (err: any) {
      // '__handled__' means finalResult was already set above;
      // anything else is a genuine unexpected failure.
      if (err.message !== '__handled__') {
        finalResult.status = 'RUNTIME_ERROR';
        finalResult.error = err.message || 'Unknown error';
      }
    } finally {
      finalResult.executionTimeMs = Date.now() - startTime;

      await fs.rm(tmpDir, { recursive: true, force: true });
    }

    console.log(
      `[Worker] Finished #${jobId}: ${finalResult.status} (${finalResult.executionTimeMs}ms)`,
    );

    return finalResult;
  },

  {
    connection: redisConnection,
    concurrency: WORKER_CONCURRENCY,
  },
);