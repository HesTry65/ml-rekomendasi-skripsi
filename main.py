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
from sklearn.preprocessing import LabelEncoder

load_dotenv()

# ── 1. Fetch data dari Supabase ────────────────────────────────────────────────
print("Mengambil data dari Supabase...")
url     = os.environ["SUPABASE_URL"] + "/rest/v1/responses?select=*&created_at=lt.2026-06-07T00:00:00&order=id.asc"
headers = {
    "apikey":        os.environ["SUPABASE_KEY"],
    "Authorization": "Bearer " + os.environ["SUPABASE_KEY"],
}
resp    = requests.get(url, headers=headers)
records = resp.json()

if not records:
    print("Tidak ada data di tabel responses. Kumpulkan data dulu.")
    exit()

df = pd.DataFrame(records)
print(f"Total data: {len(df)} responden\n")

# ── 2. Preprocessing ───────────────────────────────────────────────────────────
df = df[["body_shape", "gaya", "outfit"]].dropna()

# Ambil gaya dominan (pilihan pertama)
df["gaya_dominan"] = df["gaya"].apply(lambda x: x[0] if isinstance(x, list) and len(x) > 0 else None)
df = df.dropna(subset=["gaya_dominan"])

# Ambil outfit utama (pilihan pertama) lalu kelompokkan ke kategori
KATEGORI = {
    "dress":    "fullbody",
    "jumpsuit": "fullbody",
    "setelan":  "fullbody",
    "rok":      "bawahan",
    "celana":   "bawahan",
    "jeans":    "bawahan",
    "blus":     "atasan",
    "kemeja":   "atasan",
    "kaos":     "atasan",
    "knit":     "atasan",
    "blazer":   "outer",
    "outer":    "outer",
}
df["outfit_utama"]  = df["outfit"].apply(lambda x: x[0] if isinstance(x, list) and len(x) > 0 else None)
df["rekomendasi"]   = df["outfit_utama"].map(KATEGORI)
df = df.dropna(subset=["rekomendasi"])

print(f"Total baris setelah preprocessing: {len(df)}\n")
print("Distribusi rekomendasi per kombinasi:")
print(df.groupby(["body_shape", "gaya_dominan"])["rekomendasi"].agg(lambda x: x.value_counts().index[0]).to_string())
print()

# ── 3. Encode fitur ────────────────────────────────────────────────────────────
le_body  = LabelEncoder()
le_gaya  = LabelEncoder()
le_label = LabelEncoder()

df["body_shape_enc"] = le_body.fit_transform(df["body_shape"])
df["gaya_enc"]       = le_gaya.fit_transform(df["gaya_dominan"])
df["label_enc"]      = le_label.fit_transform(df["rekomendasi"])

X = df[["body_shape_enc", "gaya_enc"]]
y = df["label_enc"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42
)
print(f"Data training : {len(X_train)} sampel (80%)")
print(f"Data testing  : {len(X_test)} sampel (20%)\n")

# ── 4. Training C4.5 ───────────────────────────────────────────────────────────
print("Training pohon keputusan C4.5...")
model = DecisionTreeClassifier(
    criterion="entropy",
    max_depth=5,
    min_samples_split=2,
    min_samples_leaf=1,
    random_state=42,
)
model.fit(X_train, y_train)

# ── 5. Evaluasi ────────────────────────────────────────────────────────────────
y_pred = model.predict(X_test)
acc    = accuracy_score(y_test, y_pred)
print(f"\nAkurasi model: {acc * 100:.1f}%\n")
print("Classification Report:")
labels_present = sorted(y.unique())
class_names    = le_label.inverse_transform(labels_present)
report         = classification_report(
    y_test, y_pred,
    labels=labels_present,
    target_names=class_names,
    zero_division=0,
    output_dict=True,
)
print(classification_report(
    y_test, y_pred,
    labels=labels_present,
    target_names=class_names,
    zero_division=0,
))

# Visualisasi precision, recall, f1-score — satu grafik gabungan
metrics_df = pd.DataFrame(report).T.loc[list(class_names), ["precision", "recall", "f1-score"]]

x     = np.arange(len(class_names))
width = 0.25

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
feature_names = ["body_shape", "gaya_dominan"]
print("\nRules Pohon Keputusan (C4.5):")
print("=" * 60)
rules = export_text(
    model,
    feature_names=feature_names,
)
print(rules)

# ── 8. Simpan model & label encoders ──────────────────────────────────────────
joblib.dump(model,    "model_c45.pkl")
joblib.dump(le_body,  "le_body.pkl")
joblib.dump(le_gaya,  "le_gaya.pkl")
joblib.dump(le_label, "le_label.pkl")
print("Model tersimpan: model_c45.pkl")

# ── 9. Visualisasi pohon keputusan ────────────────────────────────────────────
plt.figure(figsize=(14, 6))
plot_tree(
    model,
    feature_names=feature_names,
    class_names=le_label.classes_,
    filled=True,
    rounded=True,
    fontsize=10,
)
plt.title("Pohon Keputusan C4.5 — Rekomendasi Outfit", fontsize=14)
plt.tight_layout()
plt.savefig("pohon_keputusan.png", dpi=150)
plt.show()
print("Visualisasi disimpan: pohon_keputusan.png")

# ── 10. Fungsi prediksi ────────────────────────────────────────────────────────
def prediksi(body_shape: str, gaya: str) -> str:
    try:
        bs  = le_body.transform([body_shape])[0]
        g   = le_gaya.transform([gaya])[0]
        inp = pd.DataFrame([[bs, g]], columns=["body_shape_enc", "gaya_enc"])
        enc = model.predict(inp)[0]
        return le_label.inverse_transform([enc])[0]
    except Exception:
        return "Kombinasi tidak ditemukan dalam data training"

# Contoh prediksi
print("\nContoh prediksi:")
contoh = [
    ("hourglass", "casual"),
    ("pear",      "formal"),
    ("rectangle", "bohemian"),
    ("inverted",  "sporty"),
    ("apple",     "classic"),
]
for bs, g in contoh:
    hasil = prediksi(bs, g)
    print(f"  body_shape={bs}, gaya={g} → rekomendasi: {hasil}")
