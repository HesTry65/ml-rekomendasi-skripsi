import os
import requests
from dotenv import load_dotenv
import random

load_dotenv()
random.seed(11)

BASE_URL = os.environ["SUPABASE_URL"] + "/rest/v1/responses"
HEADERS  = {
    "apikey":        os.environ["SUPABASE_KEY"],
    "Authorization": "Bearer " + os.environ["SUPABASE_KEY"],
    "Content-Type":  "application/json",
    "Prefer":        "return=minimal",
}

# ── Hapus semua dummy (lama & baru), data asli responden Juni 6 tetap aman ────
print("Menghapus data dummy lama...")
r1 = requests.delete(BASE_URL + "?created_at=lte.2026-06-03T23:59:59", headers=HEADERS)
print(f"Hapus dummy lama: {r1.status_code}")
r2 = requests.delete(BASE_URL + "?created_at=gte.2026-06-07T00:00:00", headers=HEADERS)
print(f"Hapus dummy baru: {r2.status_code}")

# ── Mapping seimbang: ~6-7 kombinasi per kategori ─────────────────────────────
# fullbody (7): hourglass×5, rectangle+formal, apple+classic  → 7×8 = 56
# bawahan  (6): pear×2, inverted×2, rectangle+bohemian, apple+bohemian → 6×8 = 48
# outer    (6): pear+formal, inverted+formal, apple+formal, sporty×3   → 6×8 = 48
# atasan   (6): pear×2, rectangle×2, inverted+casual, apple+casual     → 6×8 = 48
mapping = {
    # ── FULLBODY ──
    ("hourglass", "casual"):   ["dress",    "jeans",  "blus"],
    ("hourglass", "formal"):   ["setelan",  "blazer", "kemeja"],
    ("hourglass", "classic"):  ["dress",    "rok",    "blus"],
    ("hourglass", "bohemian"): ["dress",    "blus",   "outer"],
    ("hourglass", "sporty"):   ["jumpsuit", "kaos",   "jeans"],
    ("rectangle", "formal"):   ["setelan",  "kemeja", "blazer"],
    ("apple",     "classic"):  ["setelan",  "kemeja", "blazer"],

    # ── BAWAHAN ──
    ("pear",      "classic"):  ["rok",  "blus",  "kemeja"],
    ("pear",      "bohemian"): ["rok",  "blus",  "outer"],
    ("inverted",  "classic"):  ["rok",  "blus",  "kemeja"],
    ("inverted",  "bohemian"): ["rok",  "blus",  "knit"],
    ("rectangle", "bohemian"): ["rok",  "blus",  "outer"],
    ("apple",     "bohemian"): ["rok",  "blus",  "outer"],

    # ── OUTER ──
    ("pear",      "formal"):   ["blazer", "setelan", "celana"],
    ("inverted",  "formal"):   ["blazer", "celana",  "kemeja"],
    ("apple",     "formal"):   ["blazer", "celana",  "kemeja"],
    ("rectangle", "sporty"):   ["outer",  "kaos",    "celana"],
    ("inverted",  "sporty"):   ["outer",  "kaos",    "celana"],
    ("apple",     "sporty"):   ["outer",  "kaos",    "celana"],

    # ── ATASAN ──
    ("pear",      "casual"):   ["blus",  "jeans",  "kaos"],
    ("pear",      "sporty"):   ["kaos",  "celana", "outer"],
    ("rectangle", "casual"):   ["kaos",  "jeans",  "outer"],
    ("rectangle", "classic"):  ["kemeja","celana",  "blazer"],
    ("inverted",  "casual"):   ["kaos",  "rok",    "jeans"],
    ("apple",     "casual"):   ["blus",  "celana", "kaos"],
}

body_shapes = ["hourglass", "pear", "rectangle", "inverted", "apple"]
gayas       = ["casual", "formal", "classic", "bohemian", "sporty"]

names = [
    "Siti", "Rina", "Dewi", "Ayu", "Maya", "Lina", "Fera", "Nisa", "Dian", "Reni",
    "Yuni", "Hana", "Tari", "Wulan", "Sari", "Mega", "Indah", "Putri", "Citra", "Rara",
    "Devi", "Ami", "Lia", "Novi", "Titi", "Riri", "Mila", "Vina", "Gita", "Fani",
]

# ── Buat 200 responden — 40 per body shape, 8 per kombinasi gaya ─────────────
dummy_data = []
name_idx   = 0
PER_COMBO  = 8   # 5 body shape × 5 gaya × 8 = 200

for bs in body_shapes:
    for gaya in gayas:
        outfit = mapping[(bs, gaya)]
        for i in range(PER_COMBO):
            gaya_list = [gaya]

            # 5% chance outfit noise (simulasi data real)
            all_outfits = sorted(set(o for v in mapping.values() for o in v))
            final_outfit = outfit if random.random() > 0.05 else [random.choice(all_outfits)] + outfit[1:]

            dummy_data.append({
                "nama":       names[name_idx % len(names)],
                "tahu_shape": random.choice(["yes", "no"]),
                "body_shape": bs,
                "gaya":       gaya_list,
                "outfit":     final_outfit,
            })
            name_idx += 1

# tidak di-shuffle agar urutan konsisten dengan simulasi

# ── Insert ke Supabase ────────────────────────────────────────────────────────
print(f"Mengirim {len(dummy_data)} data...")
resp = requests.post(BASE_URL, headers=HEADERS, json=dummy_data)
print(f"Status: {resp.status_code}")

if resp.status_code in (200, 201):
    print(f"Berhasil insert {len(dummy_data)} responden.")
    print(f"Breakdown: {len(body_shapes)} body shape × {len(gayas)} gaya × {PER_COMBO} orang = {len(dummy_data)} total")
else:
    print(f"Gagal: {resp.text[:300]}")
