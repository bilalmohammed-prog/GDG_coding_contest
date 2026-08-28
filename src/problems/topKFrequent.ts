export type TestCase = {
  nums: number[];
  k: number;
};

export type DriverTestResult =
  | { ok: true; output: unknown }
  | { ok: false; error: string };

export const TEST_CASES: TestCase[] = [
  { nums: [1, 1, 1, 2, 2, 3], k: 2 },

  { nums: [1], k: 1 },

  { nums: [-1, -1, -1, 2, 2, 3, 3, 3, 3], k: 2 },

  { nums: [4, 4, 4, 5, 5, 6, 6, 6, 6, 7, 7, 8], k: 2 },

  { nums: [1, 2, 3, 4, 5], k: 3 },

  {
    nums: Array.from({ length: 100000 }, (_, i) => (i % 100) - 50),
    k: 10,
  },

  {
    nums: Array.from({ length: 100000 }, (_, i) => {
      const x = (i * 9301 + 49297) % 233280;
      return (x % 20001) - 10000;
    }),
    k: 100,
  },
];

// ------------------------------------------------------------
// Deterministic, tie-aware scoring.
//
// Top-K-Frequent has multiple valid outputs whenever the k-th
// and (k+1)-th most frequent elements share the same frequency.
// A single ordered "expected" array is NOT sufficient to score
// this problem correctly — we validate against the full
// frequency map instead, so any valid tie-break is accepted.
// ------------------------------------------------------------

export function getEligibleAnswerSet(
  nums: number[],
  k: number,
): { eligible: Set<number>; kthFrequency: number } {
  const frequency = new Map<number, number>();

  for (const num of nums) {
    frequency.set(num, (frequency.get(num) ?? 0) + 1);
  }

  const sorted = Array.from(frequency.entries()).sort((a, b) => b[1] - a[1]);

  if (k > sorted.length) {
    throw new Error(
      `k=${k} exceeds distinct element count=${sorted.length}`,
    );
  }

  const kthFrequency = sorted[k - 1]![1];
  const eligible = new Set(
    sorted.filter(([, freq]) => freq >= kthFrequency).map(([num]) => num),
  );

  return { eligible, kthFrequency };
}

/**
 * ONE valid answer, for display/logging only — do not use for
 * scoring. Use answersMatch, which checks the full eligible set.
 */
export function getExpectedAnswer(nums: number[], k: number): number[] {
  const { eligible } = getEligibleAnswerSet(nums, k);
  return Array.from(eligible).sort((a, b) => a - b).slice(0, k);
}

export function validateOutput(output: unknown): number[] {
  if (!Array.isArray(output)) {
    throw new Error('Output must be a JSON array');
  }

  if (
    !output.every(
      (x) => typeof x === 'number' && Number.isFinite(x) && Number.isInteger(x),
    )
  ) {
    throw new Error('Output array must contain only finite integers');
  }

  if (new Set(output).size !== output.length) {
    throw new Error('Output array must not contain duplicate values');
  }

  return output as number[];
}

export function answersMatch(
  actual: number[],
  nums: number[],
  k: number,
): boolean {
  if (actual.length !== k) {
    return false;
  }

  const frequency = new Map<number, number>();

  for (const num of nums) {
    frequency.set(num, (frequency.get(num) ?? 0) + 1);
  }

  const sorted = Array.from(frequency.entries())
    .sort((a, b) => b[1] - a[1]);

  const kthFrequency = sorted[k - 1]![1];

  // Every returned value must exist in nums.
  if (!actual.every(value => frequency.has(value))) {
    return false;
  }

  // Every element with strictly higher frequency MUST be included.
  for (const [num, freq] of frequency) {
    if (freq > kthFrequency && !actual.includes(num)) {
      return false;
    }
  }

  return true;
}