# Fase 2a: Migrasi Backend ke Next.js Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the Flask backend (`app/app.py`) with a Next.js (App Router, TypeScript) app in `web/` that serves the same `/recommend` (now `/api/recommend`) API, the same legacy static UI unchanged, and a fully client-side try-on flow — deployable to Vercel Hobby.

**Architecture:** Next.js App Router as sole host. `app/api/recommend/route.ts` ports the C4.5 tree (extracted from `research/models/model_c45.pkl` into `data/tree.json`) and the `BODY_GAYA_ITEM` lookup to pure TypeScript — no Python/sklearn at runtime. Try-on runs 100% client-side: the legacy static page (`public/La Silhouette.dc.html` + `support.js` + `image-slot.js`, moved verbatim) calls `public/tryon.js`, a plain browser JS module that imports `@gradio/client` from a CDN and talks directly to the Hugging Face Space `yisol/IDM-VTON` — no round-trip through the Next.js server, sidestepping Vercel Hobby's ~60s function-duration limit.

**Tech Stack:** Next.js 16 (App Router, TypeScript), Node.js 24 native test runner (`node --test`, zero extra deps), `@gradio/client` (loaded via CDN ESM import in the browser, not an npm dependency of `web/`), Python 3 + a throwaway venv (discarded after use) for one-off tree extraction.

## Global Constraints

- Project root: `/home/raz/Unduhan/skripsi-puput-fix/ml-rekomendasi - skripsi - Copy` (path has spaces — always quote it in shell commands).
- New Next.js app lives in `web/` (not repo root) — avoids collision between Next's `app/` router convention and the existing Flask `app/` folder.
- The C4.5 model's predictions must be **100% identical** to `research/models/model_c45.pkl` — verified via a 160-combination parity check (5 body shapes × 32 gaya boolean combinations) with **0 mismatches** before `tree.json` is used by any route.
- Vercel Hobby function duration is ~60s max — try-on logic MUST run client-side only, never through a Next.js API route.
- `HF_TOKEN` is intentionally exposed client-side (user-approved) — name it `NEXT_PUBLIC_HF_TOKEN` in env files to make that explicit, not `HF_TOKEN`.
- No new persistence/DB — history stays in-memory client state (already the case in the legacy JS, confirmed no `localStorage` usage).
- The legacy UI files (`La Silhouette.dc.html`, `support.js`, `image-slot.js`) move to `web/public/` **unchanged in structure** — only the two `fetch()` calls (`/recommend` → `/api/recommend`, and the `/generate-tryon` block → a `tryon.js` import) are edited. No other lines in these files change.
- `app/` (the existing Flask implementation) is **not deleted** by this plan — it's left in place as a reference until the user confirms the Next.js version fully replaces it. Do not `rm` or `git rm` anything under `app/`.
- Never run `git add -A` or `git add .` — stage explicit paths only.
- Every `node --test` file that imports another local module must use an explicit `.ts` extension in the import specifier (e.g. `"./tree.ts"`, not `"./tree"`) — Node's native TS support requires it. `web/tsconfig.json` needs `"allowImportingTsExtensions": true` so Next's own TypeScript check doesn't reject those same `.ts`-suffixed imports.
- JSON imports (`tree.json`, `tree-fixtures.json`) use the `with { type: "json" }` import-attribute syntax everywhere (both `node --test` and Next.js require it for JSON imports in ESM).

---

### Task 1: Scaffold the Next.js app in `web/`

**Files:**
- Create: `web/` (entire scaffold via `create-next-app`)
- Modify: `web/tsconfig.json`

**Interfaces:**
- Produces: a working `web/` Next.js 16 App Router project with `npm run dev`, `npm run build`, `npm start` all functional, and `allowImportingTsExtensions` enabled for later tasks' `.ts`-suffixed imports.

- [ ] **Step 1: Scaffold the project**

```bash
cd "/home/raz/Unduhan/skripsi-puput-fix/ml-rekomendasi - skripsi - Copy"
npx --yes create-next-app@latest web --typescript --app --no-tailwind --eslint --import-alias "@/*" --disable-git --no-agents-md --use-npm --yes
```

Expected: `Success! Created web at .../web`. This creates `web/app/page.tsx`, `web/app/layout.tsx`, `web/public/` (with default SVGs — leave them, later tasks add real assets alongside), `web/tsconfig.json`, `web/next.config.ts`, `web/package.json` with `next`, `react`, `react-dom` deps and `dev`/`build`/`start`/`lint` scripts.

- [ ] **Step 2: Add `allowImportingTsExtensions` to tsconfig**

Open `web/tsconfig.json`. Find this block inside `compilerOptions`:

```json
    "resolveJsonModule": true,
    "isolatedModules": true,
```

Replace with:

```json
    "resolveJsonModule": true,
    "isolatedModules": true,
    "allowImportingTsExtensions": true,
```

- [ ] **Step 3: Verify the scaffold builds**

```bash
cd "/home/raz/Unduhan/skripsi-puput-fix/ml-rekomendasi - skripsi - Copy/web"
npm run build
```

Expected: `✓ Compiled successfully`, route table shows `/` as static.

- [ ] **Step 4: Commit**

```bash
cd "/home/raz/Unduhan/skripsi-puput-fix/ml-rekomendasi - skripsi - Copy"
git add web/
git commit -m "feat: scaffold Next.js app for backend migration (Fase 2a)"
```

---

### Task 2: Export and validate the C4.5 decision tree

**Files:**
- Create: `research/scripts/export_tree.py`
- Create (generated by the script, then committed): `web/data/tree.json`, `web/data/tree-fixtures.json`

**Interfaces:**
- Consumes: `research/models/model_c45.pkl`, `research/models/le_body.pkl`, `research/models/mlb_gaya.pkl`, `research/models/le_label.pkl` (existing, unmodified).
- Produces: `web/data/tree.json` — a nested node structure `{feature, threshold, left, right}` / leaf `{leaf: "atasan"|"bawahan"|"fullbody"|"outer"}`, walked by `left` when `input[feature] <= threshold` else `right`. `web/data/tree-fixtures.json` — an array of 160 `{input: {body_shape_enc, gaya_bohemian, gaya_casual, gaya_classic, gaya_formal, gaya_sporty}, expected: "<label>"}` objects, one per body-shape × gaya-boolean-combination, used by Task 3's test.
- Known encodings (confirmed from the trained pickles): `le_body.classes_` = `["apple", "hourglass", "inverted", "pear", "rectangle"]` (so `body_shape_enc` is that array's index). `mlb.classes_` = `["bohemian", "casual", "classic", "formal", "sporty"]` (alphabetical — this is the exact order of the `gaya_*` feature columns). `le_label.classes_` = `["atasan", "bawahan", "fullbody", "outer"]`.

- [ ] **Step 1: Create the export script**

Create `research/scripts/export_tree.py`:

```python
import itertools
import json
import os

import joblib
import pandas as pd

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
MODELS_DIR = os.path.join(REPO_ROOT, "research", "models")
OUT_DIR = os.path.join(REPO_ROOT, "web", "data")
os.makedirs(OUT_DIR, exist_ok=True)

model = joblib.load(os.path.join(MODELS_DIR, "model_c45.pkl"))
le_body = joblib.load(os.path.join(MODELS_DIR, "le_body.pkl"))
mlb = joblib.load(os.path.join(MODELS_DIR, "mlb_gaya.pkl"))
le_label = joblib.load(os.path.join(MODELS_DIR, "le_label.pkl"))

gaya_cols = [f"gaya_{g}" for g in mlb.classes_]
feature_names = ["body_shape_enc"] + gaya_cols

tree = model.tree_


def export_node(node_id):
    if tree.feature[node_id] == -2:  # sklearn's TREE_UNDEFINED = leaf
        class_idx = int(tree.value[node_id][0].argmax())
        return {"leaf": str(le_label.classes_[class_idx])}
    return {
        "feature": feature_names[tree.feature[node_id]],
        "threshold": float(tree.threshold[node_id]),
        "left": export_node(int(tree.children_left[node_id])),
        "right": export_node(int(tree.children_right[node_id])),
    }


tree_json = export_node(0)
with open(os.path.join(OUT_DIR, "tree.json"), "w") as f:
    json.dump(tree_json, f, indent=2)

# 160-combo fixtures: 5 body shapes x 32 gaya boolean combos (2^5, incl. empty set)
fixtures = []
for body_shape in le_body.classes_:
    bs_enc = int(le_body.transform([body_shape])[0])
    for combo in itertools.product([0, 1], repeat=5):
        gaya_selected = [g for g, bit in zip(mlb.classes_, combo) if bit]
        gaya_bin = mlb.transform([gaya_selected])[0]
        inp = pd.DataFrame([[bs_enc] + list(gaya_bin)], columns=feature_names)
        enc = int(model.predict(inp)[0])
        expected = str(le_label.classes_[enc])

        input_row = {"body_shape_enc": bs_enc}
        for g, bit in zip(mlb.classes_, combo):
            input_row[f"gaya_{g}"] = int(bit)
        fixtures.append({"input": input_row, "expected": expected})

print("total fixtures:", len(fixtures))

with open(os.path.join(OUT_DIR, "tree-fixtures.json"), "w") as f:
    json.dump(fixtures, f, indent=2)


# Parity check: walk tree.json in pure Python (mirrors the TS walk in web/lib/tree.ts)
# against model.predict directly — this is the 0-mismatch proof the spec requires.
def walk(node, row):
    if "leaf" in node:
        return node["leaf"]
    val = row[node["feature"]]
    if val <= node["threshold"]:
        return walk(node["left"], row)
    return walk(node["right"], row)


mismatch_count = 0
for fx in fixtures:
    got = walk(tree_json, fx["input"])
    if got != fx["expected"]:
        mismatch_count += 1
        print("MISMATCH:", fx["input"], "expected", fx["expected"], "got", got)

print("mismatches:", mismatch_count)
assert mismatch_count == 0, f"{mismatch_count} mismatches found — do not commit tree.json"
```

- [ ] **Step 2: Create a throwaway venv and run the script**

The repo's own `.venv/` is not usable (broken/platform-mismatched). Use a scratch venv, discarded after this step:

```bash
python3 -m venv /tmp/tree-export-venv
/tmp/tree-export-venv/bin/pip install -q scikit-learn joblib numpy pandas
cd "/home/raz/Unduhan/skripsi-puput-fix/ml-rekomendasi - skripsi - Copy"
/tmp/tree-export-venv/bin/python research/scripts/export_tree.py
```

Expected output: `total fixtures: 160` then `mismatches: 0` (an `InconsistentVersionWarning` about sklearn 1.8.0 vs 1.9.0 is expected and harmless — the pickle still loads and predicts correctly). If `mismatches` is not 0, STOP — do not proceed to Task 3, the tree export logic has a bug.

- [ ] **Step 3: Clean up the throwaway venv**

```bash
rm -rf /tmp/tree-export-venv
```

- [ ] **Step 4: Verify the generated files**

```bash
cd "/home/raz/Unduhan/skripsi-puput-fix/ml-rekomendasi - skripsi - Copy"
python3 -c "import json; d=json.load(open('web/data/tree.json')); print('root feature:', d.get('feature'))"
python3 -c "import json; fx=json.load(open('web/data/tree-fixtures.json')); print('fixture count:', len(fx))"
```

Expected: `root feature: body_shape_enc`, `fixture count: 160`.

- [ ] **Step 5: Commit**

```bash
cd "/home/raz/Unduhan/skripsi-puput-fix/ml-rekomendasi - skripsi - Copy"
git add research/scripts/export_tree.py web/data/tree.json web/data/tree-fixtures.json
git commit -m "feat: export C4.5 tree to JSON with 160-combo parity fixtures"
```

---

### Task 3: `lib/tree.ts` — pure TypeScript tree walker

**Files:**
- Create: `web/lib/tree.ts`
- Create: `web/lib/tree.test.ts`

**Interfaces:**
- Consumes: `web/data/tree.json`, `web/data/tree-fixtures.json` (from Task 2).
- Produces: `predict(input: TreeInput): "atasan" | "bawahan" | "fullbody" | "outer"` and the `TreeInput` type — Task 5 (`lib/recommend.ts`) imports both by name.

- [ ] **Step 1: Write the failing test**

Create `web/lib/tree.test.ts`:

```ts
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
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd "/home/raz/Unduhan/skripsi-puput-fix/ml-rekomendasi - skripsi - Copy/web"
node --test lib/tree.test.ts
```

Expected: FAIL — `Cannot find module './tree.ts'` (or similar module-not-found error).

- [ ] **Step 3: Write `lib/tree.ts`**

Create `web/lib/tree.ts`:

```ts
import treeData from "../data/tree.json" with { type: "json" };

type Leaf = "atasan" | "bawahan" | "fullbody" | "outer";

type TreeNode =
  | { feature: string; threshold: number; left: TreeNode; right: TreeNode }
  | { leaf: Leaf };

export interface TreeInput {
  body_shape_enc: number;
  gaya_bohemian: 0 | 1;
  gaya_casual: 0 | 1;
  gaya_classic: 0 | 1;
  gaya_formal: 0 | 1;
  gaya_sporty: 0 | 1;
}

const tree = treeData as TreeNode;

export function predict(input: TreeInput): Leaf {
  let node = tree;
  while (!("leaf" in node)) {
    const value = input[node.feature as keyof TreeInput];
    node = value <= node.threshold ? node.left : node.right;
  }
  return node.leaf;
}
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd "/home/raz/Unduhan/skripsi-puput-fix/ml-rekomendasi - skripsi - Copy/web"
node --test lib/tree.test.ts
```

Expected: `✔ predict matches all 160 body_shape x gaya combinations`, `ℹ pass 1`, `ℹ fail 0`.

- [ ] **Step 5: Verify Next.js's own TypeScript check also accepts the `.ts`-extension + JSON-attribute imports**

```bash
cd "/home/raz/Unduhan/skripsi-puput-fix/ml-rekomendasi - skripsi - Copy/web"
npm run build
```

Expected: `✓ Compiled successfully`. If this fails on the `.ts` extension import or the JSON import attribute, re-check Task 1 Step 2 (`allowImportingTsExtensions`) was applied correctly.

- [ ] **Step 6: Commit**

```bash
cd "/home/raz/Unduhan/skripsi-puput-fix/ml-rekomendasi - skripsi - Copy"
git add web/lib/tree.ts web/lib/tree.test.ts
git commit -m "feat: port C4.5 tree walk to TypeScript, 160/160 fixture parity"
```

---

### Task 4: `lib/recommend-data.ts` — port `BODY_GAYA_ITEM`

**Files:**
- Create: `web/lib/recommend-data.ts`
- Create: `web/lib/recommend-data.test.ts`

**Interfaces:**
- Produces: `BODY_GAYA_ITEM` (verbatim data transcription of the Flask dict), plus the types `BodyShape`, `Gaya`, `Kategori` — Task 5 imports all four by name.

- [ ] **Step 1: Write the failing test**

Create `web/lib/recommend-data.test.ts`:

```ts
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
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd "/home/raz/Unduhan/skripsi-puput-fix/ml-rekomendasi - skripsi - Copy/web"
node --test lib/recommend-data.test.ts
```

Expected: FAIL — `Cannot find module './recommend-data.ts'`.

- [ ] **Step 3: Write `lib/recommend-data.ts`**

Create `web/lib/recommend-data.ts` — this is a verbatim transcription of `app/app.py`'s `BODY_GAYA_ITEM` dict (lines 48-84), with no logic added:

```ts
export type BodyShape = "apple" | "hourglass" | "inverted" | "pear" | "rectangle";
export type Gaya = "bohemian" | "casual" | "classic" | "formal" | "sporty";
export type Kategori = "atasan" | "bawahan" | "fullbody" | "outer";

type ItemMap = Record<Kategori, string[]>;

export const BODY_GAYA_ITEM: Record<BodyShape, Record<Gaya, ItemMap>> = {
  apple: {
    bohemian: { atasan: ["blus flowy", "tunik"], bawahan: ["rok A-line"], fullbody: ["dress wrap", "dress empire"], outer: ["cardigan panjang"] },
    casual: { atasan: ["kaos oversize", "blus flowy"], bawahan: ["celana bootcut", "rok A-line"], fullbody: ["dress A-line", "jumpsuit longgar"], outer: ["outer panjang"] },
    classic: { atasan: ["blus empire", "kemeja flowy"], bawahan: ["celana bootcut", "rok A-line"], fullbody: ["setelan blazer panjang"], outer: ["blazer panjang"] },
    formal: { atasan: ["kemeja empire"], bawahan: ["celana bootcut"], fullbody: ["setelan blazer panjang"], outer: ["blazer panjang"] },
    sporty: { atasan: ["kaos oversize"], bawahan: ["celana wide-leg"], fullbody: ["jumpsuit longgar"], outer: ["outer panjang"] },
  },
  hourglass: {
    bohemian: { atasan: ["blus wrap", "knit fitted"], bawahan: ["rok midi", "rok wrap"], fullbody: ["dress wrap", "dress fitted"], outer: ["outer berpotongan"] },
    casual: { atasan: ["kaos fitted", "blus tucked-in"], bawahan: ["jeans skinny", "celana straight"], fullbody: ["dress wrap", "jumpsuit fitted"], outer: ["outer fitted"] },
    classic: { atasan: ["kemeja tucked-in", "blus fitted"], bawahan: ["rok pencil", "celana straight"], fullbody: ["setelan fitted"], outer: ["blazer fitted"] },
    formal: { atasan: ["kemeja tucked-in"], bawahan: ["rok pencil"], fullbody: ["setelan fitted"], outer: ["blazer fitted"] },
    sporty: { atasan: ["kaos fitted"], bawahan: ["celana straight", "legging"], fullbody: ["jumpsuit fitted"], outer: ["outer fitted"] },
  },
  inverted: {
    bohemian: { atasan: ["blus basic", "knit V-neck"], bawahan: ["rok flared", "rok A-line"], fullbody: ["dress A-line", "dress flared"], outer: ["cardigan panjang"] },
    casual: { atasan: ["kaos V-neck", "blus simple"], bawahan: ["celana wide-leg", "jeans flared"], fullbody: ["dress A-line", "jumpsuit lebar bawah"], outer: ["cardigan panjang"] },
    classic: { atasan: ["kemeja V-neck", "blus basic"], bawahan: ["celana wide-leg", "rok A-line"], fullbody: ["setelan rok flared"], outer: ["blazer single button"] },
    formal: { atasan: ["kemeja V-neck"], bawahan: ["celana wide-leg"], fullbody: ["setelan rok flared"], outer: ["blazer single button"] },
    sporty: { atasan: ["kaos V-neck"], bawahan: ["celana wide-leg", "celana palazzo"], fullbody: ["jumpsuit lebar bawah"], outer: ["cardigan panjang"] },
  },
  pear: {
    bohemian: { atasan: ["blus ruffle", "knit off-shoulder"], bawahan: ["rok A-line", "rok flared"], fullbody: ["dress A-line", "dress wrap"], outer: ["outer bahu tegas"] },
    casual: { atasan: ["kaos grafis", "blus off-shoulder"], bawahan: ["celana wide-leg", "rok A-line"], fullbody: ["dress A-line", "jumpsuit bahu lebar"], outer: ["outer bahu tegas"] },
    classic: { atasan: ["kemeja berdetail dada", "blus berdetail bahu"], bawahan: ["celana wide-leg", "rok midi flared"], fullbody: ["setelan atasan berdetail"], outer: ["blazer bahu tegas"] },
    formal: { atasan: ["kemeja berdetail bahu"], bawahan: ["celana wide-leg"], fullbody: ["setelan atasan berdetail"], outer: ["blazer bahu tegas"] },
    sporty: { atasan: ["kaos grafis dada", "kaos bahu lebar"], bawahan: ["celana wide-leg", "celana palazzo"], fullbody: ["jumpsuit bahu lebar"], outer: ["outer bahu tegas"] },
  },
  rectangle: {
    bohemian: { atasan: ["blus ruffle", "knit peplum"], bawahan: ["rok flared", "rok ruffled"], fullbody: ["dress wrap", "dress berpotongan"], outer: ["outer cropped"] },
    casual: { atasan: ["kaos crop", "blus tied"], bawahan: ["rok flared", "celana wide-leg"], fullbody: ["dress wrap", "jumpsuit ikat pinggang"], outer: ["outer cropped"] },
    classic: { atasan: ["kemeja peplum", "blus tucked-in"], bawahan: ["rok flared", "celana wide-leg"], fullbody: ["setelan ikat pinggang"], outer: ["blazer cropped"] },
    formal: { atasan: ["kemeja peplum"], bawahan: ["rok flared"], fullbody: ["setelan ikat pinggang"], outer: ["blazer cropped"] },
    sporty: { atasan: ["kaos crop", "kaos tied"], bawahan: ["celana wide-leg", "rok flared"], fullbody: ["jumpsuit ikat pinggang"], outer: ["outer cropped"] },
  },
};
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd "/home/raz/Unduhan/skripsi-puput-fix/ml-rekomendasi - skripsi - Copy/web"
node --test lib/recommend-data.test.ts
```

Expected: both tests pass.

- [ ] **Step 5: Commit**

```bash
cd "/home/raz/Unduhan/skripsi-puput-fix/ml-rekomendasi - skripsi - Copy"
git add web/lib/recommend-data.ts web/lib/recommend-data.test.ts
git commit -m "feat: port BODY_GAYA_ITEM lookup table to TypeScript"
```

---

### Task 5: `lib/recommend.ts` — encoding, fokus branching, item lookup

**Files:**
- Create: `web/lib/recommend.ts`
- Create: `web/lib/recommend.test.ts`

**Interfaces:**
- Consumes: `predict`, `TreeInput` from `./tree.ts` (Task 3); `BODY_GAYA_ITEM`, `BodyShape`, `Gaya`, `Kategori` from `./recommend-data.ts` (Task 4).
- Produces: `buildRecommendation(bodyShape: string, gaya: string[]): RecommendResult` and the `RecommendResult` interface — Task 6's route handler imports both by name. `buildRecommendation` throws a plain `Error` for an unrecognized `bodyShape`; it does NOT validate that `gaya` is non-empty (that HTTP-level check belongs to Task 6's route handler, matching the Flask behavior it replaces) — an empty or all-unrecognized `gaya` array is valid input to this function and yields empty item arrays plus whatever the tree predicts for an all-zero feature row.

- [ ] **Step 1: Write the failing test**

Create `web/lib/recommend.test.ts`:

```ts
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
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd "/home/raz/Unduhan/skripsi-puput-fix/ml-rekomendasi - skripsi - Copy/web"
node --test lib/recommend.test.ts
```

Expected: FAIL — `Cannot find module './recommend.ts'`.

- [ ] **Step 3: Write `lib/recommend.ts`**

Create `web/lib/recommend.ts` — ports `get_items()` and the `/recommend` fokus-branching logic from `app/app.py` lines 87-132:

```ts
import { predict } from "./tree.ts";
import { BODY_GAYA_ITEM, type BodyShape, type Gaya, type Kategori } from "./recommend-data.ts";

const BODY_SHAPES: readonly BodyShape[] = ["apple", "hourglass", "inverted", "pear", "rectangle"];
const GAYA_LIST: readonly Gaya[] = ["bohemian", "casual", "classic", "formal", "sporty"];

function isBodyShape(v: string): v is BodyShape {
  return (BODY_SHAPES as readonly string[]).includes(v);
}

function isGaya(v: string): v is Gaya {
  return (GAYA_LIST as readonly string[]).includes(v);
}

function getItems(bodyShape: BodyShape, gayaList: string[], kategori: Kategori): string[] {
  const items: string[] = [];
  const bsMap = BODY_GAYA_ITEM[bodyShape];
  for (const g of gayaList) {
    if (!isGaya(g)) continue;
    for (const item of bsMap[g][kategori]) {
      if (!items.includes(item)) items.push(item);
    }
  }
  return items;
}

export interface RecommendResult {
  fokus: Kategori;
  fullbody?: string[];
  atasan?: string[];
  bawahan?: string[];
  outer?: string[];
}

export function buildRecommendation(bodyShape: string, gaya: string[]): RecommendResult {
  if (!isBodyShape(bodyShape)) {
    throw new Error(`body_shape tidak dikenali: ${bodyShape}`);
  }

  const bodyShapeEnc = BODY_SHAPES.indexOf(bodyShape);
  const fokus = predict({
    body_shape_enc: bodyShapeEnc,
    gaya_bohemian: gaya.includes("bohemian") ? 1 : 0,
    gaya_casual: gaya.includes("casual") ? 1 : 0,
    gaya_classic: gaya.includes("classic") ? 1 : 0,
    gaya_formal: gaya.includes("formal") ? 1 : 0,
    gaya_sporty: gaya.includes("sporty") ? 1 : 0,
  });

  const result: RecommendResult = { fokus };

  if (fokus === "fullbody") {
    result.fullbody = getItems(bodyShape, gaya, "fullbody");
  } else if (fokus === "atasan") {
    result.atasan = getItems(bodyShape, gaya, "atasan");
    result.bawahan = getItems(bodyShape, gaya, "bawahan");
  } else if (fokus === "bawahan") {
    result.bawahan = getItems(bodyShape, gaya, "bawahan");
    result.atasan = getItems(bodyShape, gaya, "atasan");
  } else if (fokus === "outer") {
    result.outer = getItems(bodyShape, gaya, "outer");
    result.atasan = getItems(bodyShape, gaya, "atasan");
    result.bawahan = getItems(bodyShape, gaya, "bawahan");
  }

  return result;
}
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd "/home/raz/Unduhan/skripsi-puput-fix/ml-rekomendasi - skripsi - Copy/web"
node --test lib/recommend.test.ts
```

Expected: all 5 tests pass.

- [ ] **Step 5: Run the full test suite so far**

```bash
cd "/home/raz/Unduhan/skripsi-puput-fix/ml-rekomendasi - skripsi - Copy/web"
node --test
```

Expected: `ℹ pass 8` (1 from tree.test.ts + 2 from recommend-data.test.ts + 5 from recommend.test.ts), `ℹ fail 0`.

- [ ] **Step 6: Commit**

```bash
cd "/home/raz/Unduhan/skripsi-puput-fix/ml-rekomendasi - skripsi - Copy"
git add web/lib/recommend.ts web/lib/recommend.test.ts
git commit -m "feat: port /recommend fokus branching + item lookup to TypeScript"
```

---

### Task 6: `app/api/recommend/route.ts` — the API route

**Files:**
- Create: `web/app/api/recommend/route.ts`

**Interfaces:**
- Consumes: `buildRecommendation`, `RecommendResult` from `../../../lib/recommend.ts` (Task 5).
- Produces: `POST /api/recommend` — accepts `{body_shape: string, gaya: string[]}`, returns the same JSON shape the Flask `/recommend` route did (`{fokus, ...category arrays}` on success, `{error}` on 4xx/5xx).

- [ ] **Step 1: Write the route handler**

Create `web/app/api/recommend/route.ts` — ports the Flask `/recommend` view (`app/app.py` lines 102-138):

```ts
import { NextResponse } from "next/server";
import { buildRecommendation } from "@/lib/recommend";

export async function POST(request: Request) {
  const data = await request.json().catch(() => null);
  const bodyShape = String(data?.body_shape ?? "").trim().toLowerCase();
  const gayaRaw = Array.isArray(data?.gaya) ? data.gaya : [];
  const gaya = gayaRaw.map((g: unknown) => String(g).trim().toLowerCase());

  if (!bodyShape || gaya.length === 0) {
    return NextResponse.json(
      { error: "Mohon pilih bentuk tubuh dan gaya pakaian" },
      { status: 400 }
    );
  }

  try {
    const result = buildRecommendation(bodyShape, gaya);
    return NextResponse.json(result);
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    return NextResponse.json({ error: `Data tidak dikenali: ${message}` }, { status: 422 });
  }
}
```

- [ ] **Step 2: Verify it builds**

```bash
cd "/home/raz/Unduhan/skripsi-puput-fix/ml-rekomendasi - skripsi - Copy/web"
npm run build
```

Expected: `✓ Compiled successfully`, route table includes `/api/recommend` (dynamic).

- [ ] **Step 3: Manual runtime verification — cover all 4 fokus classes**

```bash
cd "/home/raz/Unduhan/skripsi-puput-fix/ml-rekomendasi - skripsi - Copy/web"
(npm start > /tmp/recommend-route-verify.log 2>&1 &)
sleep 3

curl -s -X POST http://localhost:3000/api/recommend -H "Content-Type: application/json" \
  -d '{"body_shape":"apple","gaya":["sporty"]}'
echo
# Expected: {"fokus":"atasan","atasan":["kaos oversize"],"bawahan":["celana wide-leg"]}

curl -s -X POST http://localhost:3000/api/recommend -H "Content-Type: application/json" \
  -d '{"body_shape":"apple","gaya":["classic","formal"]}'
echo
# Expected: {"fokus":"bawahan","bawahan":["celana bootcut","rok A-line"],"atasan":["blus empire","kemeja flowy","kemeja empire"]}

curl -s -X POST http://localhost:3000/api/recommend -H "Content-Type: application/json" \
  -d '{"body_shape":"apple","gaya":["bohemian","sporty"]}'
echo
# Expected: {"fokus":"fullbody","fullbody":["dress wrap","dress empire","jumpsuit longgar"]}

curl -s -X POST http://localhost:3000/api/recommend -H "Content-Type: application/json" \
  -d '{"body_shape":"hourglass","gaya":["classic"]}'
echo
# fokus should be "outer" per research/models parity data — if this JSON doesn't say
# "outer", cross-check web/data/tree-fixtures.json for body_shape_enc=1 (hourglass),
# gaya_classic=1, all other gaya=0, and treat any mismatch as a Task 5 bug, not expected.

curl -s -X POST http://localhost:3000/api/recommend -H "Content-Type: application/json" -d '{"body_shape":"apple","gaya":[]}'
echo
# Expected: 400 {"error":"Mohon pilih bentuk tubuh dan gaya pakaian"}

curl -s -X POST http://localhost:3000/api/recommend -H "Content-Type: application/json" -d '{"body_shape":"notashape","gaya":["casual"]}'
echo
# Expected: 422 {"error":"Data tidak dikenali: body_shape tidak dikenali: notashape"}

kill %1 2>/dev/null
```

- [ ] **Step 4: Commit**

```bash
cd "/home/raz/Unduhan/skripsi-puput-fix/ml-rekomendasi - skripsi - Copy"
git add web/app/api/recommend/route.ts
git commit -m "feat: add /api/recommend route handler"
```

---

### Task 7: Migrate static assets, wire the legacy UI to the new API

**Files:**
- Create (copies): `web/public/images/**`, `web/public/screenshots/**`, `web/public/La Silhouette.dc.html`, `web/public/support.js`, `web/public/image-slot.js`, `web/public/body_shape_clean.png`, `web/public/clothes_pattern.png`, `web/public/hero_blend.png`, `web/public/shape_apple.png`, `web/public/shape_apple_v2.png`, `web/public/shape_hourglass_v2.png`, `web/public/shape_inverted_v2.png`, `web/public/shape_pear_v2.png`, `web/public/shape_rectangle_v2.png`, `web/public/woman_only.png`
- Modify: `web/next.config.ts`
- Modify: `web/public/La Silhouette.dc.html` (one line)
- Delete: `web/app/page.tsx`

**Interfaces:**
- Produces: `GET /` serves the legacy static page; all its relative asset paths (`images/...`, etc.) resolve because they now live alongside it in `web/public/`. This task does not yet wire up try-on (Task 8 does that) — the "Coba Pakai Fotomu (AI)" button will still reference the old `/generate-tryon` fetch until Task 8 replaces it.

- [ ] **Step 1: Copy all static assets into `web/public/`**

Using `cp`, not `mv` — `app/` stays untouched per the Global Constraints.

```bash
cd "/home/raz/Unduhan/skripsi-puput-fix/ml-rekomendasi - skripsi - Copy"
mkdir -p web/public/images web/public/screenshots
cp -r app/images/. web/public/images/
cp -r app/screenshots/. web/public/screenshots/
cp "app/La Silhouette.dc.html" "web/public/La Silhouette.dc.html"
cp app/support.js web/public/support.js
cp app/image-slot.js web/public/image-slot.js
cp app/body_shape_clean.png app/clothes_pattern.png app/hero_blend.png \
   app/shape_apple.png app/shape_apple_v2.png app/shape_hourglass_v2.png \
   app/shape_inverted_v2.png app/shape_pear_v2.png app/shape_rectangle_v2.png \
   app/woman_only.png web/public/
```

- [ ] **Step 2: Verify copy completeness**

```bash
cd "/home/raz/Unduhan/skripsi-puput-fix/ml-rekomendasi - skripsi - Copy"
diff <(find app/images -type f | sed 's#app/images/##' | sort) <(find web/public/images -type f | sed 's#web/public/images/##' | sort)
diff <(find app/screenshots -type f | sed 's#app/screenshots/##' | sort) <(find web/public/screenshots -type f | sed 's#web/public/screenshots/##' | sort)
```

Expected: both `diff` commands produce no output (identical file sets).

- [ ] **Step 3: Edit the `/recommend` fetch URL**

In `web/public/La Silhouette.dc.html`, find (around line 834):

```js
        const response = await fetch('/recommend', {
```

Replace with:

```js
        const response = await fetch('/api/recommend', {
```

This is the only edit in this task — the `/generate-tryon` fetch block (around line 936) is left as-is until Task 8.

- [ ] **Step 4: Delete the default page and add the rewrite**

```bash
cd "/home/raz/Unduhan/skripsi-puput-fix/ml-rekomendasi - skripsi - Copy"
rm web/app/page.tsx
```

Replace the contents of `web/next.config.ts` with:

```ts
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    return [{ source: "/", destination: "/La%20Silhouette.dc.html" }];
  },
};

export default nextConfig;
```

`app/page.tsx` must be deleted for this rewrite to take effect — Next.js's filesystem route matching runs before rewrites, so a `page.tsx` at `/` would otherwise win over the rewrite every time.

- [ ] **Step 5: Verify build and runtime**

```bash
cd "/home/raz/Unduhan/skripsi-puput-fix/ml-rekomendasi - skripsi - Copy/web"
npm run build
(npm start > /tmp/static-verify.log 2>&1 &)
sleep 3
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:3000/
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:3000/images/atasan/
curl -s http://localhost:3000/ | grep -c "fetch('/api/recommend'"
kill %1 2>/dev/null
```

Expected: first `curl` prints `200` (the legacy HTML is served at `/`), the `grep -c` prints `1` (confirms the edited fetch URL is live). The `/images/atasan/` request's status code isn't meaningful on its own (directories aren't servable) — this step is just confirming the server responds, not a 404-from-missing-`public/`.

- [ ] **Step 6: Commit**

```bash
cd "/home/raz/Unduhan/skripsi-puput-fix/ml-rekomendasi - skripsi - Copy"
git add web/public/ web/next.config.ts
git rm web/app/page.tsx
git commit -m "feat: migrate static assets, serve legacy UI at / via rewrite"
```

---

### Task 8: Client-side try-on (`tryon.js`, `tryon-helpers.js`, `/api/config`)

**Files:**
- Create: `web/public/tryon-helpers.js`
- Create: `web/lib/tryon-helpers.test.ts`
- Create: `web/public/tryon.js`
- Create: `web/app/api/config/route.ts`
- Modify: `web/public/La Silhouette.dc.html` (one block)
- Create: `web/.env.example`

**Interfaces:**
- Produces: `generateTryon(photoBase64: string, garments: {image: string, label: string, category: string}[]): Promise<string>` (exported from `public/tryon.js`, returns a `data:image/png;base64,...` string) — consumed by the legacy HTML's `generateTryon()` method via dynamic `import()`. `GET /api/config` returns `{hfToken: string | null}`.
- These are plain browser JS files (not `.ts`, not bundled by Next) because they're served as static assets from `public/` and consumed by the un-bundled legacy HTML via `<script type="module">` semantics (dynamic `import()`), same as the spec's Component 4 but implemented as `.js` instead of `lib/tryon.ts` — Next.js never compiles anything under `public/`, so a `.ts` file there would never be transpiled and would 404 as an unparseable module in the browser.

- [ ] **Step 1: Write the failing test for the pure helpers**

Create `web/lib/tryon-helpers.test.ts` (imports across into `public/` via relative path so test code never lives inside the publicly-servable directory):

```ts
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
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd "/home/raz/Unduhan/skripsi-puput-fix/ml-rekomendasi - skripsi - Copy/web"
node --test lib/tryon-helpers.test.ts
```

Expected: FAIL — `Cannot find module '../public/tryon-helpers.js'`.

- [ ] **Step 3: Write `public/tryon-helpers.js`**

Create `web/public/tryon-helpers.js`:

```js
// Urutan tempel: bawah/fullbody dulu, lalu atasan, lalu outer paling atas
// (matches GARMENT_ORDER in the old app/app.py).
export const GARMENT_ORDER = { fullbody: 0, atasan: 1, bawahan: 2, outer: 3 };

export function sortByGarmentOrder(garments) {
  return garments
    .slice()
    .sort((a, b) => (GARMENT_ORDER[a.category] ?? 9) - (GARMENT_ORDER[b.category] ?? 9));
}

// Same 8000-byte threshold as the old app.py's _is_probably_blank(min_bytes=8000).
export function isBlankBySize(byteLength, minBytes = 8000) {
  return byteLength < minBytes;
}

export async function isProbablyBlank(url, minBytes = 8000) {
  try {
    const headRes = await fetch(url, { method: "HEAD" });
    const len = headRes.headers.get("content-length");
    if (len !== null) return isBlankBySize(Number(len), minBytes);
    const res = await fetch(url);
    const blob = await res.blob();
    return isBlankBySize(blob.size, minBytes);
  } catch {
    return true;
  }
}
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd "/home/raz/Unduhan/skripsi-puput-fix/ml-rekomendasi - skripsi - Copy/web"
node --test lib/tryon-helpers.test.ts
```

Expected: both tests pass.

- [ ] **Step 5: Write the `/api/config` route**

Create `web/app/api/config/route.ts`:

```ts
import { NextResponse } from "next/server";

export async function GET() {
  return NextResponse.json({ hfToken: process.env.NEXT_PUBLIC_HF_TOKEN || null });
}
```

Create `web/.env.example`:

```
NEXT_PUBLIC_HF_TOKEN=hf_your_token_here
```

`NEXT_PUBLIC_` prefix is deliberate (per Global Constraints) — this token is client-exposed by design, the prefix just makes that explicit rather than pretending it's a server secret. Actual values go in `web/.env.local` (already gitignored by the Task 1 scaffold's default `.gitignore`), never committed.

- [ ] **Step 6: Write `public/tryon.js`**

Create `web/public/tryon.js` — ports the Hugging Face call chain from `app/app.py`'s `/generate-tryon` (lines 161-224), replacing local tempfile juggling with in-memory `Blob`s since this runs in the browser:

```js
import { Client, handle_file } from "https://cdn.jsdelivr.net/npm/@gradio/client/dist/index.min.js";
import { sortByGarmentOrder, isProbablyBlank } from "./tryon-helpers.js";

const HF_SPACE = "yisol/IDM-VTON";
let hfTokenPromise = null;

function getHfToken() {
  if (!hfTokenPromise) {
    hfTokenPromise = fetch("/api/config")
      .then((r) => r.json())
      .then((d) => d.hfToken);
  }
  return hfTokenPromise;
}

export async function generateTryon(photoBase64, garments) {
  if (!photoBase64 || !garments || !garments.length) {
    throw new Error("Foto dan minimal 1 item rekomendasi wajib diisi");
  }

  const sorted = sortByGarmentOrder(garments);
  const token = await getHfToken();
  const client = await Client.connect(HF_SPACE, { token: token || undefined });

  const photoRes = await fetch(photoBase64);
  let currentBlob = await photoRes.blob();
  const applied = [];

  try {
    for (const g of sorted) {
      const garmentUrl = (g.image || "").trim();
      if (!garmentUrl) continue;

      const absoluteUrl = new URL(garmentUrl, window.location.origin).href;
      if (await isProbablyBlank(absoluteUrl)) continue;

      const result = await client.predict("/tryon", {
        dict: { background: handle_file(currentBlob), layers: [], composite: null },
        garm_img: handle_file(absoluteUrl),
        garment_des: g.label || "pakaian",
        is_checked: true,
        is_checked_crop: false,
        denoise_steps: 30,
        seed: 42,
      });

      const outUrl = result.data[0].url;
      const outRes = await fetch(outUrl);
      currentBlob = await outRes.blob();
      applied.push(g.label || "pakaian");
    }
  } catch (err) {
    throw new Error(
      `Gagal generate (Hugging Face Space mungkin sedang sibuk/tidur, coba lagi): ${err.message || err}`
    );
  }

  if (!applied.length) {
    throw new Error("Tidak ada item valid untuk di-generate");
  }

  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = () => reject(reader.error);
    reader.readAsDataURL(currentBlob);
  });
}
```

- [ ] **Step 7: Wire the legacy HTML's `generateTryon()` method to the new module**

In `web/public/La Silhouette.dc.html`, find this block (around lines 935-946):

```js
    try {
      const response = await fetch('/generate-tryon', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ photo: this.state.tryonPhoto, garments })
      });
      const data = await response.json();
      if (!response.ok || data.error) throw new Error(data.error || 'Gagal generate gambar');
      this.setState({ tryonResult: data.image, tryonLoading: false });
    } catch (err) {
      this.setState({ tryonLoading: false, tryonError: err.message || 'Terjadi kesalahan, coba lagi.' });
    }
```

Replace with:

```js
    try {
      const { generateTryon } = await import('./tryon.js');
      const image = await generateTryon(this.state.tryonPhoto, garments);
      this.setState({ tryonResult: image, tryonLoading: false });
    } catch (err) {
      this.setState({ tryonLoading: false, tryonError: err.message || 'Terjadi kesalahan, coba lagi.' });
    }
```

Everything above this block (the garment-building loop, the "Setelan" top/bottom split, the 2-garment cap) is untouched — it already builds the exact same `garments` array shape `tryon.js` expects.

- [ ] **Step 8: Run the full test suite**

```bash
cd "/home/raz/Unduhan/skripsi-puput-fix/ml-rekomendasi - skripsi - Copy/web"
node --test
```

Expected: `ℹ pass 10` (8 from Tasks 3-5 + 2 from this task), `ℹ fail 0`.

- [ ] **Step 9: Verify the build**

```bash
cd "/home/raz/Unduhan/skripsi-puput-fix/ml-rekomendasi - skripsi - Copy/web"
npm run build
```

Expected: `✓ Compiled successfully`, route table includes `/api/config`.

- [ ] **Step 10: Commit**

```bash
cd "/home/raz/Unduhan/skripsi-puput-fix/ml-rekomendasi - skripsi - Copy"
git add web/public/tryon-helpers.js web/lib/tryon-helpers.test.ts web/public/tryon.js \
        web/app/api/config/route.ts web/.env.example web/public/"La Silhouette.dc.html"
git commit -m "feat: client-side try-on via @gradio/client, no server round-trip"
```

---

### Task 9: End-to-end manual verification and cutover

**Files:** None created — this task is verification-only, plus a short note to the user about the one manual step they must do (fill in `web/.env.local`).

**Interfaces:** None — this task validates the integration of Tasks 1-8, it doesn't introduce new interfaces.

- [ ] **Step 1: Set up the local env file**

```bash
cd "/home/raz/Unduhan/skripsi-puput-fix/ml-rekomendasi - skripsi - Copy/web"
cp .env.example .env.local
```

Tell the user to edit `web/.env.local` and put their real Hugging Face token in `NEXT_PUBLIC_HF_TOKEN` before browser testing (a free HF account token, same one already used in `app/.env`'s `HF_TOKEN` — copy the value across). Without it, try-on still works but hits the tighter anonymous ZeroGPU quota.

- [ ] **Step 2: Full production build + start**

```bash
cd "/home/raz/Unduhan/skripsi-puput-fix/ml-rekomendasi - skripsi - Copy/web"
npm run build
npm start
```

Expected: `✓ Compiled successfully`, server listening on `http://localhost:3000`.

- [ ] **Step 3: Browser golden path (manual — do this in an actual browser, not curl)**

Open `http://localhost:3000`. Walk through:
1. Pick a body shape → pick at least one gaya → confirm the recommendation screen shows real items (not an error).
2. Pick a combo whose fokus is `fullbody` and whose recommended item name contains "setelan" (e.g. hourglass + classic → check `web/data/tree-fixtures.json` or just try a few combos in the UI until the result includes a "setelan ..." item) → go to Mix & Match detail → click "Coba Pakai Fotomu (AI) ✨" → upload a real photo of a person (not a cartoon avatar — IDM-VTON only handles real human photos, this is a documented system limitation) → click generate.
3. Confirm: no crash, the "setelan" item resolves into two garments (top + bottom split) rather than one broken combined image, generation eventually returns a result or a clear `tryonError` message (cold start / ZeroGPU quota errors are acceptable outcomes here — a JS crash or a stuck spinner is not).
4. Try a second, non-"setelan" recommendation through the same try-on flow, confirm it also completes or fails gracefully.
5. Confirm the 4 known-blank crop files never cause a crash: `setelan_atasan_berdetail_bottom.png`, `setelan_blazer_panjang_bottom.png`, `setelan_ikat_pinggang_top.png`, `setelan_rok_flared_top.png` — these should be silently skipped by `isProbablyBlank`, not sent to the API. (You'll only exercise this if the UI happens to route through one of these specific files — if it doesn't come up naturally, this is a lower-priority check since Step 3-4 already exercise the same skip logic on whichever files those combos use.)
6. Save a look, check it appears in History, click it, confirm it routes to Mix & Match and back-navigation returns to History (existing behavior, should be untouched — this step is a regression check, not new functionality).

- [ ] **Step 4: Stop the server**

```bash
# Ctrl+C in the terminal running `npm start`, or:
pkill -f "next start"
```

- [ ] **Step 5: Report to the user**

Summarize: full test suite pass count, build status, and the outcome of each browser golden-path check from Step 3. If any step failed, do not mark this task complete — file it as a bug against the specific task (3, 5, 6, or 8) whose code is responsible, fix there, and re-run this task's verification from Step 2.

- [ ] **Step 6: Final commit (if Step 5's report required any fixup commits, this step is just confirming clean state)**

```bash
cd "/home/raz/Unduhan/skripsi-puput-fix/ml-rekomendasi - skripsi - Copy"
git status
```

Expected: clean (only `web/.env.local` untracked, correctly ignored — confirm with `git status` that `.env.local` does not appear as untracked-and-about-to-be-added; if it does, `web/.gitignore` is missing the `.env*.local` line create-next-app normally includes, and needs a fix before this task is considered done).

---

## Self-Review Notes

- **Spec coverage:** All 5 components from the design spec (tree.ts/tree.json, recommend-data.ts, route.ts, tryon module, static assets) map to Tasks 2-8. Data flow steps 1-5 are covered by Tasks 6-9. Error handling requirements (400 for invalid input, try/catch around the HF call, silent blank-file skip) are implemented in Tasks 6 and 8. Testing/Verification section is covered by Task 2's parity check, Tasks 3-5's `node --test` suites, and Task 9's manual browser pass.
- **Deliberate deviation from the spec's literal file paths:** the spec names `lib/tryon.ts`; this plan uses `public/tryon.js` + `public/tryon-helpers.js` instead. Reason: `lib/` is TypeScript compiled by Next's bundler, but the legacy static HTML in `public/` is never bundled — a `.ts` file there would 404 as unparseable by the browser. Plain browser JS in `public/`, loaded via CDN ESM import and dynamic `import()`, satisfies every hard constraint the spec actually states (client-side only, no API route, works with the unbundled legacy page) without literally matching the stated path. Flagged here per the spec's own instruction to document such deviations transparently.
- **`gaya` empty-array handling:** the spec's Error Handling section says "gaya array boleh kosong," but `app/app.py`'s actual `/recommend` view rejects empty `gaya` with a 400 (`if not body_shape or not gaya:`). This plan resolves the tension by keeping `buildRecommendation()` (the pure lib function) permissive of empty `gaya`, while `route.ts` replicates Flask's literal 400 rejection — matching the spec's "sama struktur kayak sebelumnya" intent for the HTTP layer without contradicting either the pure-function testability or the original Flask source of truth.
