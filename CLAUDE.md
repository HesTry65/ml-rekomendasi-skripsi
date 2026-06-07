# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```powershell
# Install dependencies
pip install -r requirements.txt

# Generate & insert dummy data ke Supabase (hapus dummy lama dulu)
py seed_dummy.py

# Cari random seed yang menghasilkan akurasi target
py find_seed.py

# Training model utama (pakai data responden asli dari Supabase)
py main.py
```

## Environment

Butuh file `.env` di root dengan isi:
```
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_KEY=your_anon_key
```

## Architecture

Proyek skripsi sistem rekomendasi outfit berbasis **C4.5 Decision Tree** (sklearn `DecisionTreeClassifier` dengan `criterion="entropy"`).

**Alur data:**
1. Data kuesioner responden disimpan di Supabase tabel `responses` dengan kolom: `body_shape` (string), `gaya` (array multi-select), `outfit` (array multi-select)
2. `main.py` fetch data responden asli (filter `created_at < 2026-06-07`)
3. `outfit[0]` dipetakan ke 4 kategori label: `fullbody`, `bawahan`, `atasan`, `outer`
4. Fitur: `body_shape` (LabelEncoder) + `gaya` (MultiLabelBinarizer → kolom biner per gaya)
5. Model disimpan sebagai `model_c45.pkl`, `le_body.pkl`, `mlb_gaya.pkl`, `le_label.pkl`

**Pemisahan data dummy vs asli di Supabase:**
- Data dummy: `created_at >= 2026-06-07` (diinsert oleh `seed_dummy.py`)
- Data responden asli: `created_at < 2026-06-07`
- `main.py` hanya ambil data asli; `seed_dummy.py` tidak menghapus data asli

**Fungsi prediksi** (`main.py`) menerima `body_shape: str` dan `gaya: list`, contoh:
```python
prediksi("hourglass", ["casual", "classic"])
```
