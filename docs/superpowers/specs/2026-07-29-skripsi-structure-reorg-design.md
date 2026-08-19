# Skripsi Structure Reorg — Design

## Context

Project skripsi "Sistem Rekomendasi Outfit Berbasis C4.5" punya dua bagian:
- **Penelitian**: notebook (`recomendation.ipynb`), data training, model artifacts (`.pkl`), output figures (confusion matrix, ROC, decision tree plot), exported decision rules.
- **Implementasi**: Flask app (`Design prototype machine learning/`) yang serve model via `/recommend` dan fitur virtual try-on via `/generate-tryon` (panggil HF Space `IDM-VTON` lewat `gradio_client`).

Saat ini file-file penelitian & implementasi tercampur di root project, model `.pkl` terduplikasi di dua lokasi dengan hack auto-sync path di `app.py`, dan ada beberapa file/folder sampah (stray duplicate script, OS thumbnail cache, folder kosong).

**Scope**: hanya reorganisasi struktur file/folder + pembersihan sampah + rapikan notebook. Migrasi serving layer ke Next.js adalah fase terpisah berikutnya (di luar scope spec ini) — reorg ini adalah prasyaratnya.

## Target Structure

```
ml-rekomendasi - skripsi - Copy/
├── research/
│   ├── notebook/
│   │   └── recomendation.ipynb
│   ├── data/
│   │   └── data_latih.csv
│   ├── models/                      # single source of truth untuk semua .pkl
│   │   ├── model_c45.pkl
│   │   ├── le_body.pkl
│   │   ├── le_label.pkl
│   │   └── mlb_gaya.pkl
│   ├── outputs/
│   │   ├── figures/
│   │   │   ├── confusion_matrix_70_30.png
│   │   │   ├── metrics.png
│   │   │   ├── pohon_keputusan.png
│   │   │   └── roc_auc_curve.png
│   │   └── rules/
│   │       └── rules.py
│   └── requirements.txt
├── app/                             # renamed from "Design prototype machine learning"
│   ├── app.py
│   ├── La Silhouette.dc.html
│   ├── image-slot.js
│   ├── support.js
│   ├── images/
│   ├── uploads/
│   ├── screenshots/
│   ├── .env
│   └── requirements.txt
├── docs/
│   └── superpowers/specs/           # spec ini
└── CLAUDE.md
```

## Perubahan Detail

### 1. Pemindahan file
- `recomendation.ipynb` → `research/notebook/`
- `data_latih.csv` → `research/data/`
- `*.pkl` (root, single copy) → `research/models/`
- `confusion_matrix_70_30.png`, `metrics.png`, `pohon_keputusan.png`, `roc_auc_curve.png` → `research/outputs/figures/`
- `outputs/rules/rules.py` → `research/outputs/rules/rules.py`
- `Design prototype machine learning/` → `app/` (rename)

### 2. Penghapusan sampah
- Root `templates/` (kosong)
- Root `static/` (kosong)
- Root `outputs/data/` (kosong)
- `app/scratch/` (kosong)
- `app/.thumbnail/` (OS thumbnail cache)
- `app/uploads/main.py` (456 baris, duplikat penuh dari logic notebook, salah taruh di folder uploads)
- Duplikat `.pkl` yang lama tersebar di `app/` (setelah app.py diarahkan ke `research/models/`)

### 3. `app.py` — hilangkan auto-sync hack
Fungsi `get_pkl_path()` saat ini secara dinamis cek folder parent/root dulu sebelum load lokal (workaround supaya app selalu sinkron dengan model terbaru dari notebook tanpa copy manual). Setelah reorg, model cuma ada di satu tempat (`research/models/`), jadi hack ini dibuang — `app.py` load langsung dari path relatif `../research/models/<file>.pkl`.

### 4. Notebook cleanup
`recomendation.ipynb` sekarang 10 code cell, 0 markdown cell, section header berupa comment (`# ── 1. ... ─`) dengan penomoran yang loncat (7 → 9, tidak ada 8). Perbaikan:
- Tambah markdown cell heading + 1-2 kalimat penjelasan singkat sebelum tiap code cell section.
- Perbaiki penomoran section jadi urut 1-9.
- Logic/kode di dalam code cell **tidak diubah** — murni penambahan dokumentasi + fix numbering.

### 5. `requirements.txt` split
Root `requirements.txt` dihapus, diganti 2 file:
- `research/requirements.txt`: `pandas`, `scikit-learn`, `matplotlib`, `joblib`, `requests`, `python-dotenv`, `imbalanced-learn`
- `app/requirements.txt`: `flask`, `joblib`, `gradio_client`, `requests`, `python-dotenv`

### 6. `.gitignore`
Tambah entry `.thumbnail` / `*.thumbnail` supaya OS thumbnail cache tidak ke-track lagi kalau regenerate.

## Out of Scope
- Migrasi Flask → Next.js (fase 2, spec terpisah — perlu keputusan arsitektur soal inference model sklearn `.pkl` dan pemanggilan HF Space `gradio_client` dari Node/Next.js).
- Perubahan logic `/recommend` atau `/generate-tryon`.
- Perubahan isi/tampilan `La Silhouette.dc.html`.
- Membersihkan working-tree git yang saat ini messy (banyak file lama ter-delete belum di-commit) — tidak disentuh, di luar scope reorg ini.
