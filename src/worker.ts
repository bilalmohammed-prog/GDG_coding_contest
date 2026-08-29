// src/worker.ts
import 'dotenv/config';
import { supabase } from './supabase.js';

import { Worker, Job } from 'bullmq';
import { redisConnection } from './queue.js';
import { execFile } from 'child_process';
import util from 'util';
import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';
import { getProblem } from './problems/index.js';
//
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const execFilePromise = util.promisify(execFile);

const WORKER_CONCURRENCY = 5;
const TIME_LIMIT_SECONDS = 3;
const CONTAINER_TIMEOUT_SECONDS = 30;
const POINTS_PER_TEST = 1;
const ALL_PASSED_BONUS = 10;

type JudgeResult = {
  status: 'ACCEPTED' | 'WRONG_ANSWER' | 'TIME_LIMIT_EXCEEDED' | 'RUNTIME_ERROR';
  output: string;
  error: string;
  instructions: number;
  score: number;
};

// Driver reports, per test case: ok/output/error as before, PLUS
// an "instructions" count from the opcode tracer. 0 when the test
// didn't run to completion (error/timeout) — never scored in that case.
type DriverTestResult =
  | { ok: true; output: unknown; instructions: number }
  | { ok: false; error: string; instructions: number };

// ------------------------------------------------------------
// Build the driver script that runs INSIDE the container.
//
// Generic across problems: takes the entry function name so it
// isn't hardcoded to any one problem. Each test case is handed
// to the contestant's function as **kwargs matching the JSON
// keys in tests.json (so any problem's TestCase shape works,
// as long as its field names match the function's parameter
// names).
//
// Instruction counting: sys.settrace with f_trace_opcodes=True,
// scoped to only the entry-function call and everything it
// calls into (nested helper functions the contestant defines).
// This does NOT count inside C-implemented builtins (sorted(),
// dict, etc) — same caveat as V8 native calls, unavoidable
// without privileged perf access.
// ------------------------------------------------------------

function buildDriverScript(
  contestantCode: string,
  entryFunctionName: string,
): string {
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

class __OpcodeCounter:
    def __init__(self):
        self.count = 0

    def tracer(self, frame, event, arg):
        if event == 'call':
            frame.f_trace_opcodes = True
        elif event == 'opcode':
            self.count += 1
        return self.tracer

def __run_all():
    with open('/app/tests.json') as f:
        tests = json.load(f)

    results = []

    for test in tests:
        signal.alarm(${TIME_LIMIT_SECONDS})
        counter = __OpcodeCounter()

        try:
            sys.settrace(counter.tracer)
            output = ${entryFunctionName}(**test)
            results.append({
                "ok": True,
                "output": output,
                "instructions": counter.count,
            })
        except TestTimeout:
            results.append({
                "ok": False,
                "error": "TIME_LIMIT_EXCEEDED",
                "instructions": counter.count,
            })
        except Exception as e:
            results.append({
                "ok": False,
                "error": f"{type(e).__name__}: {e}",
                "instructions": counter.count,
            })
        finally:
            sys.settrace(None)
            signal.alarm(0)

    print(json.dumps(results))

if __name__ == "__main__":
    __run_all()
`;
}

export const worker = new Worker(
  'code-submissions',

  async (job: Job) => {
    const { code, language, problemId, user_id } = job.data;
    const jobId = job.id;
    

    console.log(`[Worker PID=${process.pid}] Executing submission #${jobId} (problem=${problemId})`);

    const tmpDir = path.join(__dirname, '../tmp', `job_${jobId}`);
    await fs.mkdir(tmpDir, { recursive: true });

    const startTime = Date.now();

    let finalResult: JudgeResult = {
  status: 'ACCEPTED',
  output: '',
  error: '',
  instructions: 0,
  score: 0,
};

    try {
      if (language !== 'python') {
        throw new Error(`Unsupported language: ${language}`);
      }

      const problem = getProblem(problemId);

      const driverScript = buildDriverScript(code, problem.entryFunctionName);
      const solutionPath = path.join(tmpDir, 'driver.py');
      await fs.writeFile(solutionPath, driverScript);

      const testsPath = path.join(tmpDir, 'tests.json');
      await fs.writeFile(testsPath, JSON.stringify(problem.testCases));

      // --------------------------------------------------------
      // ONE container for the whole submission. All test cases
      // run inside it, in-process, driven by driver.py.
      //
      // No perf/privileged flags needed — instruction counting
      // is done in pure Python via sys.settrace inside the
      // driver, so the sandboxing flags below stay minimal.
      // --------------------------------------------------------

      const dockerArgs = [
        'run', '--rm',
        '--memory=128m',
        '--cpus=0.5',
        '--pids-limit=20',
        '--network=none',
        '--read-only',
        '--tmpfs', '/tmp:rw,noexec,nosuid,size=16m',
        '-e', 'PYTHONHASHSEED=0',
        '-v', `${solutionPath}:/app/driver.py:ro`,
        '-v', `${testsPath}:/app/tests.json:ro`,
        'contest-judge',
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
      // the same order as problem.testCases.
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
      // Walk results, fail-fast on first bad test case.
      // Accumulate score only for tests that actually pass;
      // if we break early, remaining tests contribute nothing
      // and the all-passed bonus is never awarded (status
      // won't be ACCEPTED at the end).
      // ------------------------------------------------------

      let totalInstructions = 0;
      let scoreAccumulated = 0;
      let allTestsRan = true;

      for (let i = 0; i < problem.testCases.length; i++) {
        const testCase = problem.testCases[i]!;
        const testResult = driverResults[i];

        if (!testResult) {
          finalResult.status = 'RUNTIME_ERROR';
          finalResult.error = `Missing result for test case ${i + 1}`;
          allTestsRan = false;
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
          allTestsRan = false;
          break;
        }

        let actual: unknown;

        try {
          actual = problem.validateOutput(testResult.output);
        } catch (err: any) {
          finalResult.status = 'WRONG_ANSWER';
          finalResult.error = `Invalid output on test case ${i + 1}: ${err.message}`;
          allTestsRan = false;
          break;
        }

        if (!problem.answersMatch(actual, testCase)) {
          finalResult.status = 'WRONG_ANSWER';
          finalResult.error = `Wrong answer on test case ${i + 1}`;
          finalResult.output = JSON.stringify({
            actual,
            exampleValid: problem.getExpectedAnswer?.(testCase), // one valid answer, for display only
          });
          allTestsRan = false;
          break;
        }

        // Test case passed — count it toward instructions + score.
        totalInstructions += testResult.instructions;
        const ratio = problem.scoringReferenceInstructions / testResult.instructions;
        scoreAccumulated += Math.min(POINTS_PER_TEST, ratio * POINTS_PER_TEST);

        console.log(
          `[Worker PID=${process.pid}] Job #${jobId} test ${i + 1} passed (${testResult.instructions} instructions)`,
        );
      }

      finalResult.instructions = totalInstructions;

      if (allTestsRan && finalResult.status === 'ACCEPTED') {
        finalResult.score = Math.round(
          (scoreAccumulated + ALL_PASSED_BONUS) * 100,
        ) / 100;
      }
    } catch (err: any) {
      // '__handled__' means finalResult was already set above;
      // anything else is a genuine unexpected failure.
      if (err.message !== '__handled__') {
        finalResult.status = 'RUNTIME_ERROR';
        finalResult.error = err.message || 'Unknown error';
      }
    } finally {
  if (finalResult.status === 'ACCEPTED') {
    const { error: dbError } = await supabase.from('submissions').insert({
      user_id,
      score: finalResult.score,
      instruction_count: finalResult.instructions,
    });

    if (dbError) {
      console.error(`[Worker] Failed to persist submission #${jobId}:`, dbError.message);
    }
  }

  await fs.rm(tmpDir, { recursive: true, force: true });
}

  

    console.log(
  `[Worker] Finished #${jobId}: ${finalResult.status} | ` +
  `Score: ${finalResult.score} | ` +
  `Instructions: ${finalResult.instructions}`,
);

    return finalResult;
  },

  {
    connection: redisConnection,
    concurrency: WORKER_CONCURRENCY,
  },
);