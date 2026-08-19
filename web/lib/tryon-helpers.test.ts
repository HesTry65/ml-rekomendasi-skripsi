import { test } from "node:test";
import assert from "node:assert/strict";
import { sortByGarmentOrder, isBlankBySize } from "../public/tryon-helpers.js";

test("sortByGarmentOrder orders fullbody < atasan < bawahan < outer, unknown categories last", () => {
  const input = [
    { image: "a", label: "A", category: "outer" },
    { image: "b", label: "B", category: "fullbody" },
    { image: "c", label: "C", category: "bawahan" },
    { image: "d", label: "D", category: "atasan" },
    { image: "e", label: "E", category: "weird" },
  ];
  const sorted = sortByGarmentOrder(input);
  assert.deepEqual(sorted.map((g) => g.category), ["fullbody", "atasan", "bawahan", "outer", "weird"]);
});

test("isBlankBySize matches the Flask _is_probably_blank(min_bytes=8000) threshold", () => {
  assert.equal(isBlankBySize(3000), true);
  assert.equal(isBlankBySize(7999), true);
  assert.equal(isBlankBySize(8000), false);
  assert.equal(isBlankBySize(80000), false);
});
