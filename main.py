import os
import requests
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import joblib
from dotenv import load_dotenv
from sklearn.tree import DecisionTreeClassifier, export_text, plot_tree
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
from sklearn.metrics import classification_report, accuracy_score
from sklearn.preprocessing import LabelEncoder, MultiLabelBinarizer

# Membaca file .env agar SUPABASE_URL dan SUPABASE_KEY bisa diakses lewat os.environ
load_dotenv()

# ── 1. Fetch data dari Supabase ────────────────────────────────────────────────
# Mengambil semua data responden dari tabel 'responses' di Supabase
# lewat REST API yang disediakan Supabase secara otomatis
print("Mengambil data dari Supabase...")
url     = os.environ["SUPABASE_URL"] + "/rest/v1/responses?select=*&order=id.asc"
headers = {
    "apikey":        os.environ["SUPABASE_KEY"],   # kunci autentikasi Supabas
    "Authorization": "Bearer " + os.environ["SUPABASE_KEY"],
}
resp    = requests.get(url, headers=headers)
records = resp.json()  # hasil berupa list of dict (tiap dict = 1 baris data)

if not records:
    print("Tidak ada data di tabel responses. Kumpulkan data dulu.")
    exit()

df = pd.DataFrame(records)  # ubah list of dict menjadi DataFrame agar mudah diolah
print(f"Total data: {len(df)} responden\n")

# ── 2. Preprocessing ───────────────────────────────────────────────────────────
# Hanya ambil 3 kolom yang dibutuhkan untuk training, buang baris yang ada nilai kosong
df = df[["body_shape", "gaya", "outfit"]].dropna()

# Kolom 'gaya' dari Supabase bertipe array JSON (bisa multi-select)
# Pastikan isinya benar-benar list dan tidak kosong; kalau tidak valid, jadikan None lalu hapus
df["gaya"] = df["gaya"].apply(lambda x: x if isinstance(x, list) and len(x) > 0 else None)
df = df.dropna(subset=["gaya"])

# Mapping nama outfit spesifik ke 4 kategori rekomendasi
# Kategori ini yang akan menjadi label/output dari model
KATEGORI = {
    "dress":    "fullbody",   # pakaian satu potong yang menutupi badan penuh
    "jumpsuit": "fullbody",
    "setelan":  "fullbody",
    "rok":      "bawahan",    # pakaian bagian bawah
    "celana":   "bawahan",
    "jeans":    "bawahan",
    "blus":     "atasan",     # pakaian bagian atas
    "kemeja":   "atasan",
    "kaos":     "atasan",
    "knit":     "atasan",
    "blazer":   "outer",      # pakaian luar / layer tambahan
    "outer":    "outer",
}

# Ambil outfit pilihan pertama responden sebagai acuan label
# (outfit[0] = pilihan utama/prioritas responden)
df["outfit_utama"] = df["outfit"].apply(lambda x: x[0] if isinstance(x, list) and len(x) > 0 else None)
# Petakan nama outfit ke kategori; outfit yang tidak ada di mapping akan jadi NaN
df["rekomendasi"]  = df["outfit_utama"].map(KATEGORI)
df = df.dropna(subset=["rekomendasi"])  # hapus baris yang outfit-nya tidak dikenali

print(f"Total baris setelah preprocessing: {len(df)}\n")

# Tampilkan distribusi: untuk tiap kombinasi body_shape + gaya, label apa yang paling sering muncul
print("Distribusi rekomendasi per kombinasi:")
df["gaya_str"] = df["gaya"].apply(lambda x: ", ".join(x))
print(df.groupby(["body_shape", "gaya_str"])["rekomendasi"].agg(lambda x: x.value_counts().index[0]).to_string())
print()

# ── 3. Encode fitur ────────────────────────────────────────────────────────────
# Model machine learning hanya bisa membaca angka, bukan teks
# Maka semua fitur kategorikal harus diubah ke bentuk numerik

le_body  = LabelEncoder()       # mengubah body_shape (teks) → angka (misal: hourglass=1, pear=3)
mlb      = MultiLabelBinarizer()# mengubah gaya (list) → kolom biner per gaya (0 atau 1)
le_label = LabelEncoder()       # mengubah label rekomendasi (teks) → angka

df["body_shape_enc"] = le_body.fit_transform(df["body_shape"])
df["label_enc"]      = le_label.fit_transform(df["rekomendasi"])

# fit_transform pada mlb menghasilkan matrix biner:
# misal gaya=['casual','classic'] → gaya_bohemian=0, gaya_casual=1, gaya_classic=1, gaya_formal=0, gaya_sporty=0
gaya_encoded = mlb.fit_transform(df["gaya"])
gaya_cols    = [f"gaya_{g}" for g in mlb.classes_]  # nama kolom: gaya_casual, gaya_formal, dst
gaya_df      = pd.DataFrame(gaya_encoded, columns=gaya_cols, index=df.index)

# Gabungkan fitur body_shape + semua kolom gaya menjadi input model (X)
X = pd.concat([df[["body_shape_enc"]], gaya_df], axis=1)
y = df["label_enc"]  # label/target yang ingin diprediksi

# Bagi data menjadi 80% training dan 20% testing
# random_state=42 agar pembagian selalu sama setiap kali dijalankan
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42
)
print(f"Data training : {len(X_train)} sampel (80%)")
print(f"Data testing  : {len(X_test)} sampel (20%)\n")

# ── 4. Training C4.5 ───────────────────────────────────────────────────────────
# C4.5 menggunakan entropy sebagai kriteria pemilihan atribut (information gain)
# max_depth=5 membatasi kedalaman pohon agar tidak overfitting
print("Training pohon keputusan C4.5...")
model = DecisionTreeClassifier(
    criterion="entropy",      # pakai entropy = pendekatan C4.5 (bukan gini = CART)
    max_depth=5,              # maksimum 5 level kedalaman pohon
    min_samples_split=2,      # minimal 2 sampel untuk membuat percabangan baru
    min_samples_leaf=1,       # minimal 1 sampel di tiap daun pohon
    random_state=42,
)
model.fit(X_train, y_train)  # model belajar pola dari data training

# ── 5. Evaluasi ────────────────────────────────────────────────────────────────
# Uji model dengan data testing (data yang tidak dilihat saat training)
y_pred = model.predict(X_test)
acc    = accuracy_score(y_test, y_pred)
print(f"\nAkurasi model: {acc * 100:.1f}%\n")

# Classification report menampilkan precision, recall, dan f1-score per kategori:
# - Precision : dari semua yang diprediksi kelas X, berapa % yang benar
# - Recall    : dari semua data asli kelas X, berapa % yang berhasil terdeteksi
# - F1-Score  : rata-rata harmonis precision dan recall
print("Classification Report:")
labels_present = sorted(y.unique())
class_names    = le_label.inverse_transform(labels_present)
report         = classification_report(
    y_test, y_pred,
    labels=labels_present,
    target_names=class_names,
    zero_division=0,
    output_dict=True,  # output dict dipakai untuk membuat grafik di bawah
)
print(classification_report(
    y_test, y_pred,
    labels=labels_present,
    target_names=class_names,
    zero_division=0,
))

# Visualisasi precision, recall, f1-score dalam satu grafik batang kelompok
metrics_df = pd.DataFrame(report).T.loc[list(class_names), ["precision", "recall", "f1-score"]]

x     = np.arange(len(class_names))  # posisi label di sumbu X
width = 0.25                          # lebar tiap batang

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

# Tampilkan nilai angka di atas tiap batang
for bars in [bars1, bars2, bars3]:
    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, h + 0.02, f"{h:.2f}",
                ha="center", va="bottom", fontsize=9, fontweight="bold")

plt.tight_layout()
plt.savefig("metrics.png", dpi=150)
plt.show()
print("Grafik metrics disimpan: metrics.png")

# ── 6. Confusion Matrix ────────────────────────────────────────────────────────
# Confusion matrix menunjukkan berapa prediksi yang benar dan salah per kategori
# Diagonal = prediksi benar; luar diagonal = prediksi salah (tertukar ke kategori mana)
class_names = le_label.inverse_transform(labels_present)
cm  = confusion_matrix(y_test, y_pred, labels=labels_present)
fig, ax = plt.subplots(figsize=(7, 5))
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=class_names)
disp.plot(ax=ax, colorbar=False, cmap="Blues")
plt.title("Confusion Matrix — C4.5 Rekomendasi Outfit")
plt.tight_layout()
plt.savefig("confusion_matrix.png", dpi=150)
plt.show()
print("Confusion matrix disimpan: confusion_matrix.png\n")

# ── 7. Tampilkan rules pohon keputusan ────────────────────────────────────────
# Menampilkan aturan if-then yang dihasilkan pohon C4.5 dalam format teks
# Berguna untuk memahami logika keputusan model (interpretability)
feature_names = ["body_shape"] + gaya_cols
print("\nRules Pohon Keputusan (C4.5):")
print("=" * 60)
rules = export_text(
    model,
    feature_names=feature_names,
)
print(rules)

# ── 8. Simpan model & label encoders ──────────────────────────────────────────
# Model dan encoder disimpan sebagai file .pkl agar bisa digunakan ulang
# tanpa harus training ulang (dipakai oleh aplikasi/API prediksi)
joblib.dump(model,    "model_c45.pkl")
joblib.dump(le_body,  "le_body.pkl")
joblib.dump(mlb,      "mlb_gaya.pkl")   # MultiLabelBinarizer untuk gaya
joblib.dump(le_label, "le_label.pkl")
print("Model tersimpan: model_c45.pkl")

# ── 9. Visualisasi pohon keputusan ────────────────────────────────────────────
# Gambar pohon keputusan secara visual — tiap node menunjukkan atribut yang dipakai
# untuk memisahkan data, tiap daun menunjukkan label hasil prediksi
plt.figure(figsize=(14, 6))
plot_tree(
    model,
    feature_names=feature_names,
    class_names=le_label.classes_,
    filled=True,    # warna node sesuai kelas mayoritas
    rounded=True,
    fontsize=10,
)
plt.title("Pohon Keputusan C4.5 — Rekomendasi Outfit", fontsize=14)
plt.tight_layout()
plt.savefig("pohon_keputusan.png", dpi=150)
plt.show()
print("Visualisasi disimpan: pohon_keputusan.png")

# ── 10. Fungsi prediksi ────────────────────────────────────────────────────────
# Fungsi ini dipakai untuk memprediksi rekomendasi outfit berdasarkan input baru
# Input: body_shape (string) dan gaya (list of string)
# Output: kategori rekomendasi outfit (fullbody / bawahan / atasan / outer)
def prediksi(body_shape: str, gaya: list) -> str:
    try:
        bs           = le_body.transform([body_shape])[0]     # encode body_shape ke angka
        gaya_enc     = mlb.transform([gaya])                  # encode gaya ke biner
        gaya_enc_df  = pd.DataFrame(gaya_enc, columns=gaya_cols)
        inp          = pd.concat([pd.DataFrame([[bs]], columns=["body_shape_enc"]), gaya_enc_df], axis=1)
        enc          = model.predict(inp)[0]                  # prediksi angka label
        return le_label.inverse_transform([enc])[0]           # ubah angka kembali ke nama kategori
    except Exception:
        return "Kombinasi tidak ditemukan dalam data training"

# Contoh prediksi dengan beberapa kombinasi body_shape dan gaya
print("\nContoh prediksi:")
contoh = [
    ("hourglass", ["casual"]),
    ("pear",      ["formal"]),
    ("rectangle", ["bohemian", "casual"]),
    ("inverted",  ["sporty"]),
    ("apple",     ["classic", "formal"]),
]
for bs, g in contoh:
    hasil = prediksi(bs, g)
    print(f"  body_shape={bs}, gaya={g} -> rekomendasi: {hasil}")
