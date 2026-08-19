# Skripsi Structure Reorg Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Split the skripsi project's research artifacts (notebook, data, models, output figures) from its Flask demo implementation into a clean `research/` vs `app/` top-level layout, remove stray/junk files, and eliminate the `app.py` model auto-sync path hack.

**Architecture:** Pure filesystem reorg (`mv` + `rmdir`) plus two small code edits: `app.py` model-loading paths, and `recomendation.ipynb` markdown headers + relative-path fixes caused by its relocation. No behavioral change to `/recommend` or `/generate-tryon` logic.

**Tech Stack:** Bash (`mv`, `git`), Python 3 stdlib only (`py_compile`, `json`, `os.path`) for verification — no ML libraries are installed in this environment, so verification never imports `joblib`/`pandas`/`sklearn`.

## Global Constraints

- Root project dir: `/home/raz/Unduhan/skripsi-puput-fix/ml-rekomendasi - skripsi - Copy` (path has spaces — always quote it).
- Never use `git add -A`. Add explicit paths only.
- Model/data/plot logic must not change — only file location and the paths that point at those locations.
- Environment has no `joblib`/`pandas`/`sklearn`/`flask` installed — verification steps must not depend on them.

---

### Task 1: Scaffold `research/` and move research artifacts, delete empty root dirs

**Files:**
- Create dirs: `research/notebook/`, `research/data/`, `research/models/`, `research/outputs/figures/`, `research/outputs/rules/`
- Move: `recomendation.ipynb` → `research/notebook/recomendation.ipynb`
- Move: `data_latih.csv` → `research/data/data_latih.csv`
- Move: `model_c45.pkl`, `le_body.pkl`, `le_label.pkl`, `mlb_gaya.pkl` → `research/models/`
- Move: `confusion_matrix_70_30.png`, `metrics.png`, `pohon_keputusan.png`, `roc_auc_curve.png` → `research/outputs/figures/`
- Move: `outputs/rules/rules.py` → `research/outputs/rules/rules.py`
- Delete (now empty): `outputs/` (root), `templates/` (root), `static/` (root)

**Interfaces:**
- Produces: `research/notebook/recomendation.ipynb`, `research/data/data_latih.csv`, `research/models/*.pkl`, `research/outputs/figures/*.png`, `research/outputs/rules/rules.py` — paths later tasks (Task 3, Task 6) depend on.

- [ ] **Step 1: Create the research/ directory tree**

```bash
cd "/home/raz/Unduhan/skripsi-puput-fix/ml-rekomendasi - skripsi - Copy"
mkdir -p research/notebook research/data research/models research/outputs/figures research/outputs/rules
```

- [ ] **Step 2: Move research files into place**

```bash
cd "/home/raz/Unduhan/skripsi-puput-fix/ml-rekomendasi - skripsi - Copy"
mv recomendation.ipynb research/notebook/
mv data_latih.csv research/data/
mv model_c45.pkl le_body.pkl le_label.pkl mlb_gaya.pkl research/models/
mv confusion_matrix_70_30.png metrics.png pohon_keputusan.png roc_auc_curve.png research/outputs/figures/
mv outputs/rules/rules.py research/outputs/rules/
```

- [ ] **Step 3: Delete now-empty root dirs**

```bash
cd "/home/raz/Unduhan/skripsi-puput-fix/ml-rekomendasi - skripsi - Copy"
rmdir outputs/data outputs/rules outputs templates static
```

Expected: no errors (all four are empty at this point — `rmdir` fails loudly if not, which is the point: it refuses to delete anything with unexpected content).

- [ ] **Step 4: Verify the move**

```bash
cd "/home/raz/Unduhan/skripsi-puput-fix/ml-rekomendasi - skripsi - Copy"
test -f research/notebook/recomendation.ipynb && \
test -f research/data/data_latih.csv && \
test -f research/models/model_c45.pkl && \
test -f research/models/le_body.pkl && \
test -f research/models/le_label.pkl && \
test -f research/models/mlb_gaya.pkl && \
test -f research/outputs/figures/confusion_matrix_70_30.png && \
test -f research/outputs/figures/metrics.png && \
test -f research/outputs/figures/pohon_keputusan.png && \
test -f research/outputs/figures/roc_auc_curve.png && \
test -f research/outputs/rules/rules.py && \
test ! -e outputs && test ! -e templates && test ! -e static && \
echo "OK: Task 1 verified"
```

Expected: prints `OK: Task 1 verified`.

- [ ] **Step 5: Commit**

```bash
cd "/home/raz/Unduhan/skripsi-puput-fix/ml-rekomendasi - skripsi - Copy"
git add research outputs templates static recomendation.ipynb data_latih.csv \
  model_c45.pkl le_body.pkl le_label.pkl mlb_gaya.pkl \
  confusion_matrix_70_30.png metrics.png pohon_keputusan.png roc_auc_curve.png 2>/dev/null
git add -u
git commit -m "$(cat <<'EOF'
Move research artifacts into research/, drop empty root dirs

Notebook, training data, model pkl files, output figures, and
exported decision rules now live under research/ as a single
coherent tree instead of scattered at project root.
EOF
)"
```

---

### Task 2: Rename Flask app dir to `app/`, remove its internal junk

**Files:**
- Move: `Design prototype machine learning/` → `app/`
- Delete: `app/uploads/main.py`
- Delete: `app/.thumbnail/`
- Delete: `app/scratch/`

**Interfaces:**
- Produces: `app/app.py`, `app/La Silhouette.dc.html`, `app/image-slot.js`, `app/support.js`, `app/images/`, `app/uploads/`, `app/screenshots/`, `app/.env` — paths Task 3 and Task 4 depend on.

- [ ] **Step 1: Rename the directory**

```bash
cd "/home/raz/Unduhan/skripsi-puput-fix/ml-rekomendasi - skripsi - Copy"
mv "Design prototype machine learning" app
```

- [ ] **Step 2: Delete stray files**

```bash
cd "/home/raz/Unduhan/skripsi-puput-fix/ml-rekomendasi - skripsi - Copy"
rm -f "app/uploads/main.py"
rm -rf "app/.thumbnail"
rmdir "app/scratch"
```

- [ ] **Step 3: Verify**

```bash
cd "/home/raz/Unduhan/skripsi-puput-fix/ml-rekomendasi - skripsi - Copy"
test -f "app/app.py" && \
test -f "app/La Silhouette.dc.html" && \
test ! -e "app/uploads/main.py" && \
test ! -e "app/.thumbnail" && \
test ! -e "app/scratch" && \
test ! -e "Design prototype machine learning" && \
echo "OK: Task 2 verified"
```

Expected: prints `OK: Task 2 verified`.

- [ ] **Step 4: Commit**

```bash
cd "/home/raz/Unduhan/skripsi-puput-fix/ml-rekomendasi - skripsi - Copy"
git add app "Design prototype machine learning" 2>/dev/null
git add -u
git commit -m "$(cat <<'EOF'
Rename Design prototype machine learning/ to app/, drop junk

Removes app/uploads/main.py (a stray full duplicate of the notebook
logic left in the uploads folder), app/.thumbnail (OS thumbnail
cache), and the empty app/scratch dir.
EOF
)"
```

---

### Task 3: Update `app.py` to load models from `research/models/`, drop the auto-sync hack

**Files:**
- Modify: `app/app.py:20-48`

**Interfaces:**
- Consumes: `research/models/model_c45.pkl`, `research/models/le_body.pkl`, `research/models/le_label.pkl`, `research/models/mlb_gaya.pkl` (produced by Task 1).
- Produces: `model`, `le_body`, `mlb`, `le_label` module-level objects in `app/app.py` — unchanged names/types, consumed by the existing `/recommend` route (`app/app.py:106-142`), which does not need to change.

- [ ] **Step 1: Read current lines 20-48 to confirm context**

```bash
cd "/home/raz/Unduhan/skripsi-puput-fix/ml-rekomendasi - skripsi - Copy"
sed -n '18,50p' app/app.py
```

Expected output (before edit):

```python
app = Flask(__name__, static_folder='.', static_url_path='')

BASE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(BASE)
...
def get_pkl_path(filename):
    parent_path = os.path.join(PARENT, filename)
    if os.path.exists(parent_path):
        return parent_path
    return os.path.join(BASE, filename)

model    = joblib.load(get_pkl_path("model_c45.pkl"))
le_body  = joblib.load(get_pkl_path("le_body.pkl"))
mlb      = joblib.load(get_pkl_path("mlb_gaya.pkl"))
le_label = joblib.load(get_pkl_path("le_label.pkl"))
```

- [ ] **Step 2: Replace the auto-sync hack with a direct path to `research/models/`**

Replace this block (lines 39-48 of `app/app.py`):

```python
def get_pkl_path(filename):
    parent_path = os.path.join(PARENT, filename)
    if os.path.exists(parent_path):
        return parent_path
    return os.path.join(BASE, filename)

model    = joblib.load(get_pkl_path("model_c45.pkl"))
le_body  = joblib.load(get_pkl_path("le_body.pkl"))
mlb      = joblib.load(get_pkl_path("mlb_gaya.pkl"))
le_label = joblib.load(get_pkl_path("le_label.pkl"))
```

with:

```python
MODELS_DIR = os.path.join(PARENT, "research", "models")

model    = joblib.load(os.path.join(MODELS_DIR, "model_c45.pkl"))
le_body  = joblib.load(os.path.join(MODELS_DIR, "le_body.pkl"))
mlb      = joblib.load(os.path.join(MODELS_DIR, "mlb_gaya.pkl"))
le_label = joblib.load(os.path.join(MODELS_DIR, "le_label.pkl"))
```

- [ ] **Step 3: Syntax-check the file (no ML libs installed here, so this is the available check)**

```bash
cd "/home/raz/Unduhan/skripsi-puput-fix/ml-rekomendasi - skripsi - Copy"
python3 -m py_compile app/app.py && echo "OK: syntax valid"
```

Expected: prints `OK: syntax valid`.

- [ ] **Step 4: Verify the resolved model paths actually exist on disk (stdlib-only check, mirrors app.py's own path logic without importing joblib)**

```bash
cd "/home/raz/Unduhan/skripsi-puput-fix/ml-rekomendasi - skripsi - Copy"
python3 -c "
import os
BASE = os.path.abspath('app')
PARENT = os.path.dirname(BASE)
MODELS_DIR = os.path.join(PARENT, 'research', 'models')
for f in ['model_c45.pkl', 'le_body.pkl', 'mlb_gaya.pkl', 'le_label.pkl']:
    p = os.path.join(MODELS_DIR, f)
    assert os.path.isfile(p), f'missing: {p}'
print('OK: all model paths resolve')
"
```

Expected: prints `OK: all model paths resolve`.

- [ ] **Step 5: Confirm the old hack is gone**

```bash
cd "/home/raz/Unduhan/skripsi-puput-fix/ml-rekomendasi - skripsi - Copy"
grep -n "get_pkl_path" app/app.py || echo "OK: get_pkl_path removed"
```

Expected: prints `OK: get_pkl_path removed`.

- [ ] **Step 6: Commit**

```bash
cd "/home/raz/Unduhan/skripsi-puput-fix/ml-rekomendasi - skripsi - Copy"
git add app/app.py
git commit -m "$(cat <<'EOF'
app.py: load models from research/models/, drop auto-sync hack

get_pkl_path() used to probe the project root before falling back
to a local copy, so app.py always picked up whatever the notebook
last dumped without a manual copy step. Now that research/models/
is the single source of truth, that indirection is unnecessary —
load directly from the one path that exists.
EOF
)"
```

---

### Task 4: Split `requirements.txt` into `research/` and `app/`

**Files:**
- Create: `research/requirements.txt`
- Create: `app/requirements.txt`
- Delete: `requirements.txt` (root)

**Interfaces:**
- None (leaf task, no other task depends on these files).

- [ ] **Step 1: Create `research/requirements.txt`**

```
pandas
scikit-learn
matplotlib
joblib
requests
python-dotenv
imbalanced-learn
```

- [ ] **Step 2: Create `app/requirements.txt`**

```
flask
joblib
gradio_client
requests
python-dotenv
```

- [ ] **Step 3: Delete the root file**

```bash
cd "/home/raz/Unduhan/skripsi-puput-fix/ml-rekomendasi - skripsi - Copy"
rm requirements.txt
```

- [ ] **Step 4: Verify**

```bash
cd "/home/raz/Unduhan/skripsi-puput-fix/ml-rekomendasi - skripsi - Copy"
test -f research/requirements.txt && \
test -f app/requirements.txt && \
test ! -e requirements.txt && \
echo "OK: Task 4 verified"
```

Expected: prints `OK: Task 4 verified`.

- [ ] **Step 5: Commit**

```bash
cd "/home/raz/Unduhan/skripsi-puput-fix/ml-rekomendasi - skripsi - Copy"
git add research/requirements.txt app/requirements.txt requirements.txt 2>/dev/null
git add -u
git commit -m "$(cat <<'EOF'
Split requirements.txt into research/ and app/

research/ (notebook) and app/ (Flask demo) have non-overlapping
dependency sets — one shared root file mixed sklearn/matplotlib
with flask/gradio_client for no reason.
EOF
)"
```

---

### Task 5: Update `.gitignore` for OS thumbnail cache

**Files:**
- Modify: `.gitignore`

- [ ] **Step 1: Read current `.gitignore`**

Current content (3 lines):

```
.env
__pycache__/
*.pyc
```

- [ ] **Step 2: Append thumbnail cache entries**

New content:

```
.env
__pycache__/
*.pyc
.thumbnail/
*.thumbnail
```

- [ ] **Step 3: Verify**

```bash
cd "/home/raz/Unduhan/skripsi-puput-fix/ml-rekomendasi - skripsi - Copy"
grep -qx ".thumbnail/" .gitignore && grep -qx "*.thumbnail" .gitignore && echo "OK: Task 5 verified"
```

Expected: prints `OK: Task 5 verified`.

- [ ] **Step 4: Commit**

```bash
cd "/home/raz/Unduhan/skripsi-puput-fix/ml-rekomendasi - skripsi - Copy"
git add .gitignore
git commit -m "$(cat <<'EOF'
gitignore: ignore OS thumbnail cache dirs/files

app/.thumbnail (deleted in an earlier commit) is regenerated by the
OS file browser — ignore it so it doesn't get re-tracked.
EOF
)"
```

---

### Task 6: Notebook — add markdown section headers, fix numbering, fix relative paths

**Files:**
- Modify: `research/notebook/recomendation.ipynb` (edit the JSON directly via a Python script — this is the reliable way to insert cells and edit `source` arrays without corrupting notebook structure)

**Interfaces:**
- None (leaf task).

**Context:** The notebook has 10 code cells and 0 markdown cells. Section headers live only as `# ── N. TITLE ──` comments inside code cells, and numbering skips from 7 to 9 (no 8). Additionally, cell 1 reads `data_latih.csv`, cell 4/5/6 save `.png` figures, and cell 7 dumps `.pkl` files — all via bare relative filenames that assumed the notebook lived at the project root. Since Task 1 moved the notebook to `research/notebook/`, these five calls now resolve to the wrong place and must be updated to `../data/...`, `../outputs/figures/...`, and `../models/...` respectively, or the notebook silently writes its outputs into `research/notebook/` on next run.

- [ ] **Step 1: Write and run the notebook-editing script**

Create a one-off script (not committed — run and discard):

```bash
cd "/home/raz/Unduhan/skripsi-puput-fix/ml-rekomendasi - skripsi - Copy"
python3 <<'PYEOF'
import json

path = "research/notebook/recomendation.ipynb"
nb = json.load(open(path))
cells = nb["cells"]

def md(text):
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": [text],
    }

def src(i):
    return "".join(cells[i]["source"])

# --- 1. Fix relative paths (5 call sites) ---
cells[1]["source"] = [
    line.replace('pd.read_csv("data_latih.csv")', 'pd.read_csv("../data/data_latih.csv")') + "\n"
    for line in src(1).splitlines()
]
cells[4]["source"] = [
    line.replace(
        'plt.savefig("pohon_keputusan.png", dpi=150)',
        'plt.savefig("../outputs/figures/pohon_keputusan.png", dpi=150)',
    ) + "\n"
    for line in src(4).splitlines()
]
cells[5]["source"] = [
    line.replace(
        'plt.savefig("confusion_matrix_70_30.png", dpi=150)',
        'plt.savefig("../outputs/figures/confusion_matrix_70_30.png", dpi=150)',
    ) + "\n"
    for line in src(5).splitlines()
]
cells[6]["source"] = [
    line.replace(
        'plt.savefig("metrics.png", dpi=150)',
        'plt.savefig("../outputs/figures/metrics.png", dpi=150)',
    ) + "\n"
    for line in src(6).splitlines()
]
cells[7]["source"] = [
    line.replace('"model_c45.pkl"', '"../models/model_c45.pkl"')
        .replace('"le_body.pkl"', '"../models/le_body.pkl"')
        .replace('"mlb_gaya.pkl"', '"../models/mlb_gaya.pkl"')
        .replace('"le_label.pkl"', '"../models/le_label.pkl"') + "\n"
    for line in src(7).splitlines()
]

# --- 2. Fix section numbering: cell 8 "9." -> "8.", cell 9 gets "9." ---
cells[8]["source"] = [
    line.replace("9. FUNGSI REKOMENDASI", "8. FUNGSI REKOMENDASI") + "\n"
    for line in src(8).splitlines()
]
cells[9]["source"] = [
    line.replace("Contoh Rekomendasi", "9. Contoh Rekomendasi") + "\n"
    for line in src(9).splitlines()
]

# --- 3. Insert markdown headings before each cell (highest index first, so
#         earlier insertions don't shift later indices) ---
headings = [
    (9, "## 9. Contoh Rekomendasi\n\nMenjalankan `rekomendasi()` untuk 5 kombinasi body shape + gaya contoh, untuk verifikasi manual bahwa output sesuai ekspektasi."),
    (8, "## 8. Fungsi Rekomendasi\n\nFungsi `rekomendasi(body_shape, gaya)` membungkus encoding input, `model.predict()`, dan pemetaan hasil ke item outfit — ini fungsi yang sama yang dipakai `app/app.py` di endpoint `/recommend`."),
    (7, "## 7. Simpan Model dan Encoder\n\nModel terlatih dan ketiga encoder disimpan sebagai `.pkl` ke `research/models/` via `joblib.dump`, agar aplikasi tidak perlu melatih ulang model setiap kali dijalankan."),
    (6, "## 6. Evaluasi Model\n\nMenghitung akurasi dan classification report untuk data latih (training) dan data uji (testing) secara terpisah, untuk memastikan model tidak overfit."),
    (5, "## 5. Confusion Matrix\n\nMenghitung confusion matrix pada data uji dan menyimpannya sebagai gambar ke `research/outputs/figures/`."),
    (4, "## 4. Training Model C4.5\n\nMelatih `DecisionTreeClassifier` dengan kriteria entropy (pendekatan C4.5), lalu menyimpan visualisasi pohon keputusan ke `research/outputs/figures/`."),
    (3, "## 3. Encoding Fitur & Split Data\n\nMengubah fitur kategorikal (body_shape, gaya, label rekomendasi) menjadi representasi numerik, lalu membagi data menjadi 70% latih / 30% uji dan menerapkan Random Over Sampler hanya pada data latih."),
    (2, "## 2. Preprocessing Data\n\nMemetakan tiap jenis outfit ke salah satu dari 4 kategori rekomendasi (atasan/bawahan/fullbody/outer). Data yang dibaca sudah melalui proses cleaning sebelumnya."),
    (1, "## 1. Pengambilan Data dari CSV\n\nMembaca data responden yang sudah dibersihkan dari `research/data/data_latih.csv`."),
    (0, "## Setup dan Import Library\n\nImport seluruh library yang dipakai di notebook ini: manipulasi data (pandas, numpy), machine learning (scikit-learn, imbalanced-learn), visualisasi (matplotlib), penyimpanan model (joblib), dan akses environment (python-dotenv)."),
]
for idx, text in headings:
    cells.insert(idx, md(text))

nb["cells"] = cells
json.dump(nb, open(path, "w"), indent=1, ensure_ascii=False)
print(f"OK: wrote {len(cells)} cells ({sum(1 for c in cells if c['cell_type']=='markdown')} markdown, {sum(1 for c in cells if c['cell_type']=='code')} code)")
PYEOF
```

Expected: prints `OK: wrote 20 cells (10 markdown, 10 code)`.

- [ ] **Step 2: Verify the notebook is still valid JSON and the path fixes landed**

```bash
cd "/home/raz/Unduhan/skripsi-puput-fix/ml-rekomendasi - skripsi - Copy"
python3 -c "
import json
nb = json.load(open('research/notebook/recomendation.ipynb'))
cells = nb['cells']
assert len(cells) == 20, f'expected 20 cells, got {len(cells)}'
assert sum(1 for c in cells if c['cell_type']=='markdown') == 10
full = '\n'.join(''.join(c['source']) for c in cells)
assert '../data/data_latih.csv' in full
assert '../outputs/figures/pohon_keputusan.png' in full
assert '../outputs/figures/confusion_matrix_70_30.png' in full
assert '../outputs/figures/metrics.png' in full
assert '../models/model_c45.pkl' in full
assert '../models/le_body.pkl' in full
assert '../models/mlb_gaya.pkl' in full
assert '../models/le_label.pkl' in full
assert '8. FUNGSI REKOMENDASI' in full
assert '9. Contoh Rekomendasi' in full
assert 'data_latih.csv\")' not in full.replace('../data/data_latih.csv\")', '')
print('OK: Task 6 verified')
"
```

Expected: prints `OK: Task 6 verified`.

- [ ] **Step 3: Commit**

```bash
cd "/home/raz/Unduhan/skripsi-puput-fix/ml-rekomendasi - skripsi - Copy"
git add research/notebook/recomendation.ipynb
git commit -m "$(cat <<'EOF'
Notebook: add markdown headings, fix section numbering, fix paths

Adds a markdown heading + short explanation before each of the 10
code cells, renumbers the two final sections (7 -> 8 -> 9, closing
the gap where "8" was skipped), and updates 5 relative file paths
(data_latih.csv, 3x plt.savefig, 4x joblib.dump) that broke when
the notebook moved from project root to research/notebook/.
EOF
)"
```

---

## Self-Review Notes

- **Spec coverage:** all 6 spec sections covered — Task 1+2 = section "Pemindahan file"/"Penghapusan sampah", Task 3 = "app.py hilangkan auto-sync hack", Task 4 = "requirements.txt split", Task 5 = ".gitignore", Task 6 = "Notebook cleanup" (plus the necessary path-fix addendum discovered during planning, flagged to user before writing this plan).
- **Placeholder scan:** none — every step has literal commands/code, no "TBD"/"similar to above".
- **Type consistency:** `MODELS_DIR`/`model`/`le_body`/`mlb`/`le_label` names in Task 3 match exactly what `/recommend` (untouched, `app/app.py:106-142`) already references.
