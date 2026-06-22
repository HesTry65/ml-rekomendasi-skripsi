# ──────────────────────────────────────────────────────────────────────────────
# SISTEM REKOMENDASI OUTFIT BERBASIS ALGORITMA C4.5
# Menggunakan Decision Tree dengan kriteria Entropy (Information Gain)
# ──────────────────────────────────────────────────────────────────────────────

# ── Import Library ─────────────────────────────────────────────────────────────
import os                          # untuk membaca variabel lingkungan (.env)
import requests                    # untuk mengambil data dari Supabase via HTTP
import numpy as np                 # operasi array numerik
import pandas as pd                # manipulasi data dalam bentuk tabel (DataFrame)
import matplotlib.pyplot as plt    # membuat grafik dan visualisasi
import joblib                      # menyimpan dan memuat model ke file .pkl
from dotenv import load_dotenv     # membaca file .env berisi URL dan KEY Supabase

# sklearn: library machine learning utama
from sklearn.tree import DecisionTreeClassifier, export_text, plot_tree
from sklearn.model_selection import train_test_split   # membagi data training & testing
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
from sklearn.metrics import classification_report, accuracy_score
from sklearn.preprocessing import LabelEncoder, MultiLabelBinarizer

# Membaca file .env agar SUPABASE_URL dan SUPABASE_KEY tersedia sebagai variabel lingkungan
# File .env tidak di-upload ke GitHub untuk menjaga keamanan kredensial
load_dotenv()

# ── 1. PENGAMBILAN DATA DARI SUPABASE ─────────────────────────────────────────
# Data kuesioner responden disimpan di Supabase (database berbasis cloud)
# Supabase menyediakan REST API otomatis sehingga data bisa diambil via HTTP GET
# Endpoint: /rest/v1/responses → mengambil seluruh baris dari tabel 'responses'
# Parameter: select=* (semua kolom), order=id.asc (urut berdasarkan ID)
print("Mengambil data dari Supabase...")

url = os.environ["SUPABASE_URL"] + "/rest/v1/responses?select=*&order=id.asc"
headers = {
    "apikey":        os.environ["SUPABASE_KEY"],          # kunci publik autentikasi Supabase
    "Authorization": "Bearer " + os.environ["SUPABASE_KEY"],  # header wajib untuk REST API
}

resp    = requests.get(url, headers=headers)
records = resp.json()   # data dikembalikan sebagai list of dict, tiap dict = 1 responden

if not records:
    print("Tidak ada data di tabel responses. Kumpulkan data dulu.")
    exit()

# Ubah list of dict menjadi DataFrame pandas agar mudah diolah
df = pd.DataFrame(records)
print(f"Total data: {len(df)} responden\n")

# ── 2. PREPROCESSING DATA ──────────────────────────────────────────────────────
# Preprocessing = proses membersihkan dan menyiapkan data sebelum dilatih ke model
# Hanya 3 kolom yang relevan untuk model: body_shape, gaya, outfit
# Baris yang memiliki nilai kosong (null/NaN) di kolom tersebut dihapus
awal = len(df)
df = df[["body_shape", "gaya", "outfit"]].dropna()
setelah_dropna = len(df)
sebelum = len(df)
df["gaya"] = df["gaya"].apply(lambda x: x if isinstance(x, list) and len(x) > 0 else None)
df = df.dropna(subset=["gaya"])

print("Hasil Data Cleaning:")
print("+------------------------------+-------+---------+")
print("| Tahapan                      | Data  | Dihapus |")
print("+------------------------------+-------+---------+")
print(f"| {'Data awal':<28} | {awal:<5} | {'-':<7} |")
print(f"| {'Setelah seleksi kolom':<28} | {setelah_dropna:<5} | {awal - setelah_dropna:<7} |")
print(f"| {'Setelah validasi gaya':<28} | {len(df):<5} | {sebelum - len(df):<7} |")
print("+------------------------------+-------+---------+")
print(f"| {'Total lolos cleaning':<28} | {len(df):<5} | {'0':<7} |")
print("+------------------------------+-------+---------+\n")

# ── Mapping Outfit ke 4 Kategori Rekomendasi ──────────────────────────────────
# Output model bukan nama outfit spesifik, melainkan KATEGORI outfit
# 4 kategori: fullbody, bawahan, atasan, outer
# Setiap nama outfit dipetakan ke salah satu kategori berikut:
KATEGORI = {
    # Fullbody: pakaian satu potong yang menutupi badan atas dan bawah sekaligus
    "dress":    "fullbody",
    "jumpsuit": "fullbody",
    "setelan":  "fullbody",

    # Bawahan: pakaian bagian bawah tubuh
    "rok":    "bawahan",
    "celana": "bawahan",
    "jeans":  "bawahan",

    # Atasan: pakaian bagian atas tubuh
    "blus":   "atasan",
    "kemeja": "atasan",
    "kaos":   "atasan",
    "knit":   "atasan",

    # Outer: pakaian luar yang dipakai di atas atasan sebagai layer tambahan
    "blazer": "outer",
    "outer":  "outer",
}

# Mapping gaya → item spesifik per kategori (untuk mix and match)
GAYA_ITEM = {
    "bohemian": {"atasan": ["blus", "knit"],        "bawahan": ["rok"],             "fullbody": ["dress"],           "outer": ["outer"]},
    "casual":   {"atasan": ["kaos", "blus"],         "bawahan": ["jeans", "celana"], "fullbody": ["dress", "jumpsuit"],"outer": ["outer"]},
    "classic":  {"atasan": ["kemeja", "blus"],       "bawahan": ["celana", "rok"],   "fullbody": ["setelan"],         "outer": ["blazer"]},
    "formal":   {"atasan": ["kemeja"],               "bawahan": ["celana"],          "fullbody": ["setelan"],         "outer": ["blazer"]},
    "sporty":   {"atasan": ["kaos"],                 "bawahan": ["celana"],          "fullbody": ["jumpsuit"],        "outer": ["outer"]},
}

def get_items(gaya_list, kategori):
    items = []
    for g in gaya_list:
        if g in GAYA_ITEM:
            for item in GAYA_ITEM[g].get(kategori, []):
                if item not in items:
                    items.append(item)
    return items

# Tentukan label rekomendasi berdasarkan kategori yang paling sering muncul
# dari semua pilihan outfit responden (majority voting)
# Jika seri, gunakan outfit[0] sebagai tiebreaker
def get_label_mayoritas(outfit_list):
    if not isinstance(outfit_list, list) or len(outfit_list) == 0:
        return None
    kategori_list = [KATEGORI.get(o) for o in outfit_list if KATEGORI.get(o)]
    if not kategori_list:
        return None
    # Hitung frekuensi tiap kategori
    from collections import Counter
    count = Counter(kategori_list)
    max_count = max(count.values())
    mayoritas = [k for k, v in count.items() if v == max_count]
    if len(mayoritas) == 1:
        return mayoritas[0]
    # Kalau seri, pakai kategori dari outfit[0] sebagai tiebreaker
    return KATEGORI.get(outfit_list[0])

df["rekomendasi"] = df["outfit"].apply(get_label_mayoritas)
df = df.dropna(subset=["rekomendasi"])

print(f"Total baris setelah preprocessing: {len(df)}\n")

print("Hasil Labeling:")
print("+------------+--------+")
print("| Label      | Jumlah |")
print("+------------+--------+")
dist_label = df["rekomendasi"].value_counts().sort_index()
for label, count in dist_label.items():
    print(f"| {label:<10} | {count:<6} |")
print("+------------+--------+")
print(f"| {'Total':<10} | {len(df):<6} |")
print("+------------+--------+\n")

# Tampilkan distribusi rekomendasi dominan per kombinasi body_shape dan gaya
# Berguna untuk memverifikasi pola data sebelum training
print("Distribusi rekomendasi per kombinasi:")
df["gaya_str"] = df["gaya"].apply(lambda x: ", ".join(x))
print(df.groupby(["body_shape", "gaya_str"])["rekomendasi"]
      .agg(lambda x: x.value_counts().index[0]).to_string())
print()

# ── 3. ENCODING FITUR ─────────────────────────────────────────────────────────
# Algoritma C4.5 (Decision Tree) hanya bisa memproses angka, bukan teks
# Maka semua fitur kategorikal harus dikonversi ke representasi numerik

# --- LabelEncoder untuk body_shape ---
# Mengubah teks body_shape menjadi angka integer:
# apple=0, hourglass=1, inverted=2, pear=3, rectangle=4 (urut alfabet)
le_body = LabelEncoder()
df["body_shape_enc"] = le_body.fit_transform(df["body_shape"])

# --- LabelEncoder untuk label rekomendasi ---
# Mengubah kategori rekomendasi menjadi angka integer:
# atasan=0, bawahan=1, fullbody=2, outer=3 (urut alfabet)
le_label = LabelEncoder()
df["label_enc"] = le_label.fit_transform(df["rekomendasi"])

# --- MultiLabelBinarizer untuk gaya ---
# Gaya bersifat multi-pilihan → dikonversi ke kolom biner per gaya
# Setiap gaya menjadi kolom tersendiri: 1 = dipilih, 0 = tidak dipilih
mlb = MultiLabelBinarizer()
gaya_matrix = mlb.fit_transform(df["gaya"])
gaya_cols   = [f"gaya_{g}" for g in mlb.classes_]
gaya_df     = pd.DataFrame(gaya_matrix, columns=gaya_cols, index=df.index)
df          = pd.concat([df, gaya_df], axis=1)

# ── Menyusun Fitur (X) dan Label (y) ─────────────────────────────────────────
X = df[["body_shape_enc"] + gaya_cols]
y = df["label_enc"]

bs_names = list(le_body.classes_)
bs_codes = list(range(len(bs_names)))
bs_w     = [max(len(n), 3) for n in bs_names]
bs_sep   = "+" + "+".join("-" * (w + 2) for w in bs_w) + "+"
bs_hdr   = "|" + "|".join(f" {n:^{w}} " for n, w in zip(bs_names, bs_w)) + "|"
bs_vals  = "|" + "|".join(f" {v:^{w}} " for v, w in zip(bs_codes, bs_w)) + "|"

gaya_label_names = list(mlb.classes_)
gaya_label_w     = [max(len(n), 3) for n in gaya_label_names]
gaya_sep  = "+" + "+".join("-" * (w + 2) for w in gaya_label_w) + "+"
gaya_hdr  = "|" + "|".join(f" {n:^{w}} " for n, w in zip(gaya_label_names, gaya_label_w)) + "|"
gaya_vals = "|" + "|".join(f" {'Ya/Tidak':^{w}} " for w in gaya_label_w) + "|"

print("Hasil Encoding Preferensi Gaya (MultiLabelBinarizer):")
print(gaya_sep)
print(gaya_hdr)
print(gaya_sep)
print(gaya_vals)
print(gaya_sep)
print()

print("Hasil Encoding Body Shape:")
print(bs_sep)
print(bs_hdr)
print(bs_sep)
print(bs_vals)
print(bs_sep)
print()

lbl_names = list(le_label.classes_)
lbl_codes = list(range(len(lbl_names)))
lbl_w     = [max(len(n), 3) for n in lbl_names]
lbl_sep   = "+" + "+".join("-" * (w + 2) for w in lbl_w) + "+"
lbl_hdr   = "|" + "|".join(f" {n:^{w}} " for n, w in zip(lbl_names, lbl_w)) + "|"
lbl_vals  = "|" + "|".join(f" {v:^{w}} " for v, w in zip(lbl_codes, lbl_w)) + "|"

print("Hasil Encoding Rekomendasi:")
print(lbl_sep)
print(lbl_hdr)
print(lbl_sep)
print(lbl_vals)
print(lbl_sep)
print()

row      = X.iloc[0]
bs_val   = int(row["body_shape_enc"])
bs_name  = le_body.inverse_transform([bs_val])[0]
lbl_val  = int(y.iloc[0])
lbl_name = le_label.inverse_transform([lbl_val])[0]
gaya_asli = df["gaya"].iloc[0]
gaya_bin  = [int(row[col]) for col in gaya_cols]

print("Contoh 1 baris data setelah encoding:")
print(f"  body_shape_enc = {bs_val} ({bs_name})")
print(f"  gaya           = {gaya_asli} -> {gaya_bin}")
print(f"  label_enc      = {lbl_val} ({lbl_name})\n")

# ── Pembagian Data Training dan Testing ───────────────────────────────────────
# Data dibagi menjadi 80% training dan 20% testing
# Training: digunakan model untuk belajar pola
# Testing : digunakan untuk mengukur kemampuan model pada data baru (belum pernah dilihat)
# random_state=1207: memastikan pembagian data selalu sama setiap kali program dijalankan
#                    (reprodusibilitas hasil eksperimen)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=1207
)
print(f"Data training : {len(X_train)} sampel (80%)")
print(f"Data testing  : {len(X_test)} sampel (20%)\n")

# ── 4. TRAINING MODEL C4.5 ────────────────────────────────────────────────────
# Algoritma C4.5 adalah pengembangan dari ID3, menggunakan Entropy dan Information Gain
# sebagai kriteria pemilihan atribut percabangan pohon keputusan
#
# Parameter model:
# - criterion="entropy" : gunakan entropy (bukan gini), sesuai pendekatan C4.5
# - max_depth=5         : kedalaman maksimal pohon 5 level (mencegah overfitting)
# - min_samples_split=2 : minimal 2 data untuk membuat percabangan baru
# - min_samples_leaf=1  : minimal 1 data di setiap daun pohon
# - random_state=42     : reprodusibilitas internal model
print("Training pohon keputusan C4.5...")
model = DecisionTreeClassifier(
    criterion="entropy",
    max_depth=5,
    min_samples_split=2,
    min_samples_leaf=1,
    random_state=42,
)
model.fit(X_train, y_train)

print("Parameter Model C4.5:")
print(f"  criterion         : {model.criterion}")
print(f"  max_depth         : {model.max_depth}")
print(f"  min_samples_split : {model.min_samples_split}")
print(f"  min_samples_leaf  : {model.min_samples_leaf}")
print(f"  random_state      : {model.random_state}")
print()

feature_names = ["body_shape"] + gaya_cols
print("Rules Pohon Keputusan (C4.5):")
print("=" * 60)
rules = export_text(model, feature_names=feature_names)
print(rules)

# ── Visualisasi Pohon Keputusan ───────────────────────────────────────────────
plt.figure(figsize=(14, 6))
plot_tree(
    model,
    feature_names=feature_names,
    class_names=le_label.classes_,
    filled=True,
    rounded=True,
    fontsize=10,
)
plt.title("Pohon Keputusan C4.5 - Rekomendasi Outfit", fontsize=14)
plt.tight_layout()
plt.savefig("pohon_keputusan.png", dpi=150)
plt.show()
print("Visualisasi pohon keputusan disimpan: pohon_keputusan.png\n")

# ── 5. EVALUASI MODEL ─────────────────────────────────────────────────────────
# Model diuji menggunakan data testing yang belum pernah dilihat saat training
# Ini mensimulasikan kondisi nyata ketika model menerima input baru dari pengguna

# Prediksi label untuk data testing
y_pred = model.predict(X_test)

# Hitung akurasi: jumlah prediksi benar dibagi total data testing
acc = accuracy_score(y_test, y_pred)
print(f"\nAkurasi model: {acc * 100:.1f}%\n")

# ── Classification Report ─────────────────────────────────────────────────────
# Menampilkan metrik evaluasi per kategori:
# - Precision : dari semua prediksi kelas X, berapa persen yang benar?
#               Rumus: TP / (TP + FP)
# - Recall    : dari semua data asli kelas X, berapa persen yang berhasil diprediksi?
#               Rumus: TP / (TP + FN)
# - F1-Score  : rata-rata harmonis Precision dan Recall
#               Rumus: 2 x (Precision x Recall) / (Precision + Recall)
# - Support   : jumlah data asli untuk kelas tersebut di data testing
print("Classification Report:")
labels_present = sorted(y.unique())
class_names    = le_label.inverse_transform(labels_present)
report         = classification_report(
    y_test, y_pred,
    labels=labels_present,
    target_names=class_names,
    zero_division=0,
    output_dict=True,   # output berupa dict agar bisa diolah untuk grafik
)
print(classification_report(
    y_test, y_pred,
    labels=labels_present,
    target_names=class_names,
    zero_division=0,
))

# ── Grafik Precision, Recall, F1-Score ───────────────────────────────────────
# Visualisasi metrik evaluasi dalam bentuk grafik batang per kategori
# Memudahkan perbandingan performa model antar kategori rekomendasi
metrics_df = pd.DataFrame(report).T.loc[list(class_names), ["precision", "recall", "f1-score"]]

x     = np.arange(len(class_names))   # posisi tiap kelompok di sumbu X
width = 0.25                           # lebar tiap batang

fig, ax = plt.subplots(figsize=(9, 5))
bars1 = ax.bar(x - width, metrics_df["precision"], width, label="Precision", color="#4C72B0")
bars2 = ax.bar(x,         metrics_df["recall"],    width, label="Recall",    color="#55A868")
bars3 = ax.bar(x + width, metrics_df["f1-score"],  width, label="F1-Score",  color="#C44E52")

ax.set_ylim(0, 1.15)
ax.set_ylabel("Nilai")
ax.set_title("Precision, Recall, dan F1-Score per Kategori")
ax.set_xticks(x)
ax.set_xticklabels(class_names)
ax.legend()

# Tampilkan nilai angka di atas tiap batang untuk kemudahan pembacaan
for bars in [bars1, bars2, bars3]:
    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, h + 0.02, f"{h:.2f}",
                ha="center", va="bottom", fontsize=9, fontweight="bold")

plt.tight_layout()
plt.savefig("metrics.png", dpi=150)
plt.show()
print("Grafik metrics disimpan: metrics.png")

# ── 6. CONFUSION MATRIX ───────────────────────────────────────────────────────
# Confusion Matrix adalah tabel yang menunjukkan hasil prediksi vs label asli
# - Diagonal utama (kiri atas ke kanan bawah) = prediksi BENAR
# - Di luar diagonal = prediksi SALAH (tertukar ke kategori mana)
# Contoh: baris "atasan", kolom "bawahan" = data asli atasan tapi diprediksi bawahan
class_names = le_label.inverse_transform(labels_present)
cm          = confusion_matrix(y_test, y_pred, labels=labels_present)
fig, ax     = plt.subplots(figsize=(7, 5))
disp        = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=class_names)
disp.plot(ax=ax, colorbar=False, cmap="Blues")
plt.title("Confusion Matrix - C4.5 Rekomendasi Outfit")
plt.tight_layout()
plt.savefig("confusion_matrix.png", dpi=150)
plt.show()
print("Confusion matrix disimpan: confusion_matrix.png\n")


# ── 8. SIMPAN MODEL DAN ENCODER ───────────────────────────────────────────────
# Model dan semua encoder disimpan ke file .pkl menggunakan joblib
# Tujuan: model tidak perlu dilatih ulang setiap kali aplikasi dijalankan
# File .pkl ini yang digunakan oleh aplikasi/API untuk melakukan prediksi
# - model_c45.pkl : pohon keputusan C4.5 yang sudah dilatih
# - le_body.pkl   : encoder untuk kolom body_shape
# - mlb_gaya.pkl  : encoder untuk kolom gaya (MultiLabelBinarizer)
# - le_label.pkl  : encoder untuk label rekomendasi
joblib.dump(model,    "model_c45.pkl")
joblib.dump(le_body,  "le_body.pkl")
joblib.dump(mlb,      "mlb_gaya.pkl")
joblib.dump(le_label, "le_label.pkl")
print("Model tersimpan: model_c45.pkl")

# ── 9. FUNGSI REKOMENDASI ────────────────────────────────────────────────────

def rekomendasi(body_shape: str, gaya: list) -> dict:
    """Rekomendasi outfit mix and match berdasarkan body_shape dan preferensi gaya."""
    try:
        bs       = le_body.transform([body_shape])[0]
        gaya_bin = mlb.transform([gaya])[0]
        inp      = pd.DataFrame([[bs] + list(gaya_bin)], columns=["body_shape_enc"] + gaya_cols)
        enc      = model.predict(inp)[0]
        fokus    = le_label.inverse_transform([enc])[0]

        if fokus == "fullbody":
            return {"fokus": fokus, "fullbody": get_items(gaya, "fullbody")}
        elif fokus == "atasan":
            return {"fokus": fokus, "atasan": get_items(gaya, "atasan"), "bawahan": get_items(gaya, "bawahan")}
        elif fokus == "bawahan":
            return {"fokus": fokus, "bawahan": get_items(gaya, "bawahan"), "atasan": get_items(gaya, "atasan")}
        elif fokus == "outer":
            return {"fokus": fokus, "outer": get_items(gaya, "outer"), "atasan": get_items(gaya, "atasan"), "bawahan": get_items(gaya, "bawahan")}
        else:
            return {"fokus": fokus}

    except Exception:
        return {"fokus": "Kombinasi tidak ditemukan dalam data training"}

# ── Contoh Rekomendasi ────────────────────────────────────────────────────────
print("\nContoh Rekomendasi:")
contoh = [
    ("hourglass", ["casual"]),
    ("pear",      ["bohemian", "classic"]),
    ("rectangle", ["bohemian"]),
    ("inverted",  ["sporty", "formal"]),
    ("apple",     ["classic"]),
]
for bs, g in contoh:
    hasil = rekomendasi(bs, g)
    fokus = hasil["fokus"]
    print(f"\n  body_shape={bs}, gaya={g}")
    if fokus == "fullbody":
        print(f"  Fokus    : Fullbody -> {', '.join(hasil.get('fullbody', []))}")
    elif fokus == "atasan":
        print(f"  Fokus    : Atasan   -> {', '.join(hasil.get('atasan', []))}")
        print(f"  Pelengkap: Bawahan  -> {', '.join(hasil.get('bawahan', []))}")
    elif fokus == "bawahan":
        print(f"  Fokus    : Bawahan  -> {', '.join(hasil.get('bawahan', []))}")
        print(f"  Pelengkap: Atasan   -> {', '.join(hasil.get('atasan', []))}")
    elif fokus == "outer":
        print(f"  Fokus    : Outer    -> {', '.join(hasil.get('outer', []))}")
        print(f"  Pelengkap: Atasan   -> {', '.join(hasil.get('atasan', []))}")
        print(f"             Bawahan  -> {', '.join(hasil.get('bawahan', []))}")
