import { expect, test } from "bun:test";
import { runCLI } from "./helpers";

test("missing command exits non-zero and prints help", async () => {
  const result = await runCLI([]);
  expect(result.exitCode).toBe(1);
  expect(result.stdout).toContain("USAGE");
});

test("unknown command writes JSON error to stderr", async () => {
  const result = await runCLI(["bogus"]);
  expect(result.exitCode).toBe(1);
  expect(JSON.parse(result.stderr).code).toBe("BAD_CMD");
});
