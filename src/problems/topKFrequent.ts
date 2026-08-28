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

export function getExpectedAnswer(
  nums: number[],
  k: number,
): number[] {
  const frequency = new Map<number, number>();

  for (const num of nums) {
    frequency.set(num, (frequency.get(num) ?? 0) + 1);
  }

  return Array.from(frequency.entries())
    .sort((a, b) => b[1] - a[1])
    .slice(0, k)
    .map(([num]) => num)
    .sort((a, b) => a - b);
}

export function validateOutput(output: unknown): number[] {
  if (!Array.isArray(output)) {
    throw new Error('Output must be a JSON array');
  }

  if (!output.every((x) => typeof x === 'number')) {
    throw new Error('Output array must contain only numbers');
  }

  return output;
}

export function answersMatch(
  actual: number[],
  expected: number[],
): boolean {
  const normalizedActual = [...actual].sort((a, b) => a - b);
  const normalizedExpected = [...expected].sort((a, b) => a - b);

  if (normalizedActual.length !== normalizedExpected.length) {
    return false;
  }

  return normalizedActual.every(
    (value, index) => value === normalizedExpected[index],
  );
}