# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```powershell
# Install dependencies
pip install -r requirements.txt

# Training model utama (ambil semua data dari Supabase)
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
2. `main.py` fetch seluruh data dari tabel `responses`
3. `outfit` dipetakan ke 4 kategori label menggunakan majority voting: `fullbody`, `bawahan`, `atasan`, `outer`
4. Fitur: `body_shape` (LabelEncoder) + `gaya` (MultiLabelBinarizer → kolom biner per gaya)
5. Model disimpan sebagai `model_c45.pkl`, `le_body.pkl`, `mlb_gaya.pkl`, `le_label.pkl`

**Fungsi prediksi** (`main.py`) menerima `body_shape: str` dan `gaya: list`, contoh:
```python
rekomendasi("hourglass", ["casual", "classic"])
```
