import type { ProblemModule } from './types.js';
import { topKFrequentProblem } from './topKFrequent.js';

export const PROBLEM_REGISTRY: Record<string, ProblemModule> = {
  'top-k-frequent': topKFrequentProblem,
};

export function getProblem(problemId: string): ProblemModule {
  const problem = PROBLEM_REGISTRY[problemId];
  if (!problem) {
    throw new Error(`Unknown problemId: ${problemId}`);
  }
  return problem;
}