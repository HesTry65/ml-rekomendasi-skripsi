import { test } from "node:test";
import assert from "node:assert/strict";
import { buildRecommendation } from "./recommend.ts";

test("apple + no gaya selected -> fokus outer, all item lists empty", () => {
  const result = buildRecommendation("apple", []);
  assert.equal(result.fokus, "outer");
  assert.deepEqual(result.outer, []);
  assert.deepEqual(result.atasan, []);
  assert.deepEqual(result.bawahan, []);
  assert.equal(result.fullbody, undefined);
});

test("apple + sporty -> fokus atasan, complement bawahan populated", () => {
  const result = buildRecommendation("apple", ["sporty"]);
  assert.equal(result.fokus, "atasan");
  assert.deepEqual(result.atasan, ["kaos oversize"]);
  assert.deepEqual(result.bawahan, ["celana wide-leg"]);
  assert.equal(result.fullbody, undefined);
  assert.equal(result.outer, undefined);
});

test("apple + classic + formal -> fokus bawahan, complement atasan populated and deduped", () => {
  const result = buildRecommendation("apple", ["classic", "formal"]);
  assert.equal(result.fokus, "bawahan");
  assert.deepEqual(result.bawahan, ["celana bootcut", "rok A-line"]);
  assert.deepEqual(result.atasan, ["blus empire", "kemeja flowy", "kemeja empire"]);
});

test("apple + bohemian + sporty -> fokus fullbody, only fullbody key present", () => {
  const result = buildRecommendation("apple", ["bohemian", "sporty"]);
  assert.equal(result.fokus, "fullbody");
  assert.deepEqual(result.fullbody, ["dress wrap", "dress empire", "jumpsuit longgar"]);
  assert.equal(result.atasan, undefined);
  assert.equal(result.bawahan, undefined);
  assert.equal(result.outer, undefined);
});

test("unrecognized body_shape throws", () => {
  assert.throws(() => buildRecommendation("unknown", ["casual"]));
});
