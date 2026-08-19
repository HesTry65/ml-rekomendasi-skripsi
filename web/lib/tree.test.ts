import { test } from "node:test";
import assert from "node:assert/strict";
import { predict } from "./tree.ts";
import fixtures from "../data/tree-fixtures.json" with { type: "json" };

test("predict matches all 160 body_shape x gaya combinations", () => {
  for (const fx of fixtures) {
    const got = predict(fx.input);
    assert.equal(got, fx.expected, `mismatch for ${JSON.stringify(fx.input)}`);
  }
});
