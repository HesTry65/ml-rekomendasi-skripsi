import { test } from "node:test";
import assert from "node:assert/strict";
import { BODY_GAYA_ITEM } from "./recommend-data.ts";

test("spot-check entries match the source Flask BODY_GAYA_ITEM dict", () => {
  assert.deepEqual(BODY_GAYA_ITEM.apple.casual.atasan, ["kaos oversize", "blus flowy"]);
  assert.deepEqual(BODY_GAYA_ITEM.hourglass.formal.fullbody, ["setelan fitted"]);
  assert.deepEqual(BODY_GAYA_ITEM.rectangle.sporty.bawahan, ["celana wide-leg", "rok flared"]);
  assert.deepEqual(BODY_GAYA_ITEM.pear.classic.outer, ["blazer bahu tegas"]);
  assert.deepEqual(BODY_GAYA_ITEM.inverted.bohemian.fullbody, ["dress A-line", "dress flared"]);
});

test("every body shape has exactly the 5 gaya keys, every gaya has all 4 kategori keys", () => {
  const bodyShapes = Object.keys(BODY_GAYA_ITEM);
  assert.equal(bodyShapes.length, 5);
  for (const bs of Object.values(BODY_GAYA_ITEM)) {
    assert.deepEqual(Object.keys(bs).sort(), ["bohemian", "casual", "classic", "formal", "sporty"]);
    for (const item of Object.values(bs)) {
      assert.deepEqual(Object.keys(item).sort(), ["atasan", "bawahan", "fullbody", "outer"]);
    }
  }
});
