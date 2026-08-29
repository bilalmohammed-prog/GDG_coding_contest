export interface ProblemModule<TTestCase = any, TOutput = any> {
  id: string;
  entryFunctionName: string;      // e.g. "topKFrequent" — used to build driver.py call
  testCases: TTestCase[];
  scoringReferenceInstructions: number;
  validateOutput(output: unknown): TOutput;
  answersMatch(actual: TOutput, testCase: TTestCase): boolean;
  getExpectedAnswer?(testCase: TTestCase): unknown; // optional, for display only
}