import os, requests, json
from dotenv import load_dotenv

load_dotenv()

url = os.environ["SUPABASE_URL"] + "/rest/v1/responses"
headers = {
    "apikey":        os.environ["SUPABASE_KEY"],
    "Authorization": "Bearer " + os.environ["SUPABASE_KEY"],
    "Content-Type":  "application/json",
    "Prefer":        "return=minimal"
}

# ── Hapus data dummy lama (created_at >= 2026-06-07) ──────────────────────────
print("Menghapus data dummy lama...")
del_url = url + "?created_at=gte.2026-06-07T00:00:00+00:00"
r = requests.delete(del_url, headers=headers)
print(f"  Status hapus: {r.status_code}\n")

# ── Data dummy baru (konsisten, outfit jelas mayoritas) ───────────────────────
# Aturan konsistensi:
#   apple    + formal → outer    (outfit mayoritas: blazer/outer)
#   hourglass+ formal → fullbody (outfit mayoritas: setelan/dress)
#   inverted + formal → outer    (outfit mayoritas: blazer/outer)
#   pear     + formal → outer    (outfit mayoritas: blazer/outer)
#   rectangle+ formal → fullbody (outfit mayoritas: setelan/dress)

data = [
    # ── Apple + formal → outer ─────────────────────────────────────────────────
    {"nama": "Kartika Sari",     "tahu_shape": "no",  "tinggi": 157, "shoulder": 41, "bust": 92, "waist": 88, "hip": 90, "body_shape": "apple",     "gaya": ["formal"], "outfit": ["blazer", "outer"],          "created_at": "2026-06-07T08:15:32+00:00"},
    {"nama": "Melani Oktaviani", "tahu_shape": "no",  "tinggi": 160, "shoulder": 42, "bust": 95, "waist": 91, "hip": 93, "body_shape": "apple",     "gaya": ["formal"], "outfit": ["blazer", "outer", "kemeja"], "created_at": "2026-06-08T14:32:17+00:00"},
    {"nama": "Sekar Arum",       "tahu_shape": "yes", "tinggi": 155, "shoulder": 40, "bust": 89, "waist": 85, "hip": 88, "body_shape": "apple",     "gaya": ["formal"], "outfit": ["outer", "blazer"],           "created_at": "2026-06-09T09:47:53+00:00"},
    {"nama": "Ratna Puspita",    "tahu_shape": "no",  "tinggi": 158, "shoulder": 41, "bust": 93, "waist": 89, "hip": 91, "body_shape": "apple",     "gaya": ["formal"], "outfit": ["blazer", "outer", "celana"], "created_at": "2026-06-10T16:23:41+00:00"},
    {"nama": "Prilia Aini",      "tahu_shape": "no",  "tinggi": 154, "shoulder": 40, "bust": 90, "waist": 86, "hip": 89, "body_shape": "apple",     "gaya": ["formal"], "outfit": ["blazer", "outer"],           "created_at": "2026-06-11T11:08:29+00:00"},
    {"nama": "Anisa Rahma",      "tahu_shape": "yes", "tinggi": 156, "shoulder": 41, "bust": 91, "waist": 87, "hip": 90, "body_shape": "apple",     "gaya": ["formal"], "outfit": ["outer", "blazer", "kemeja"], "created_at": "2026-06-12T19:44:15+00:00"},
    {"nama": "Kirana Dewi",      "tahu_shape": "no",  "tinggi": 159, "shoulder": 42, "bust": 94, "waist": 90, "hip": 92, "body_shape": "apple",     "gaya": ["formal"], "outfit": ["blazer", "outer"],           "created_at": "2026-06-13T08:31:57+00:00"},
    {"nama": "Bella Oktavia",    "tahu_shape": "no",  "tinggi": 160, "shoulder": 41, "bust": 92, "waist": 88, "hip": 91, "body_shape": "apple",     "gaya": ["formal"], "outfit": ["outer", "blazer", "celana"], "created_at": "2026-06-14T15:17:43+00:00"},

    # ── Hourglass + formal → fullbody ──────────────────────────────────────────
    {"nama": "Nadia Permata",    "tahu_shape": "yes", "tinggi": 163, "shoulder": 40, "bust": 88, "waist": 68, "hip": 89, "body_shape": "hourglass", "gaya": ["formal"], "outfit": ["setelan", "dress"],           "created_at": "2026-06-07T14:52:38+00:00"},
    {"nama": "Cantika Indah",    "tahu_shape": "yes", "tinggi": 165, "shoulder": 41, "bust": 90, "waist": 70, "hip": 91, "body_shape": "hourglass", "gaya": ["formal"], "outfit": ["dress", "setelan"],           "created_at": "2026-06-08T09:28:14+00:00"},
    {"nama": "Maharani Putri",   "tahu_shape": "no",  "tinggi": 162, "shoulder": 39, "bust": 87, "waist": 67, "hip": 88, "body_shape": "hourglass", "gaya": ["formal"], "outfit": ["setelan", "dress", "kemeja"], "created_at": "2026-06-09T17:43:52+00:00"},
    {"nama": "Safira Wulan",     "tahu_shape": "yes", "tinggi": 160, "shoulder": 40, "bust": 89, "waist": 69, "hip": 90, "body_shape": "hourglass", "gaya": ["formal"], "outfit": ["dress", "setelan", "kemeja"], "created_at": "2026-06-10T10:15:37+00:00"},
    {"nama": "Citra Lestari",    "tahu_shape": "no",  "tinggi": 164, "shoulder": 41, "bust": 91, "waist": 71, "hip": 92, "body_shape": "hourglass", "gaya": ["formal"], "outfit": ["setelan", "dress"],           "created_at": "2026-06-11T20:29:48+00:00"},
    {"nama": "Desi Ratnasari",   "tahu_shape": "no",  "tinggi": 161, "shoulder": 40, "bust": 88, "waist": 68, "hip": 89, "body_shape": "hourglass", "gaya": ["formal"], "outfit": ["dress", "setelan", "blazer"], "created_at": "2026-06-12T07:54:21+00:00"},
    {"nama": "Lilis Susanti",    "tahu_shape": "yes", "tinggi": 162, "shoulder": 39, "bust": 87, "waist": 67, "hip": 88, "body_shape": "hourglass", "gaya": ["formal"], "outfit": ["setelan", "dress"],           "created_at": "2026-06-13T13:38:09+00:00"},
    {"nama": "Qisthy Amara",     "tahu_shape": "yes", "tinggi": 166, "shoulder": 41, "bust": 90, "waist": 70, "hip": 91, "body_shape": "hourglass", "gaya": ["formal"], "outfit": ["dress", "setelan", "blazer"], "created_at": "2026-06-14T21:12:56+00:00"},

    # ── Inverted + formal → outer ───────────────────────────────────────────────
    {"nama": "Larasati Dewi",    "tahu_shape": "no",  "tinggi": 162, "shoulder": 44, "bust": 92, "waist": 74, "hip": 84, "body_shape": "inverted",  "gaya": ["formal"], "outfit": ["blazer", "outer"],           "created_at": "2026-06-07T19:27:43+00:00"},
    {"nama": "Nabila Zahra",     "tahu_shape": "yes", "tinggi": 165, "shoulder": 45, "bust": 94, "waist": 76, "hip": 86, "body_shape": "inverted",  "gaya": ["formal"], "outfit": ["outer", "blazer", "kemeja"], "created_at": "2026-06-08T11:43:28+00:00"},
    {"nama": "Intan Permata",    "tahu_shape": "no",  "tinggi": 163, "shoulder": 44, "bust": 91, "waist": 73, "hip": 83, "body_shape": "inverted",  "gaya": ["formal"], "outfit": ["blazer", "outer"],           "created_at": "2026-06-09T15:18:54+00:00"},
    {"nama": "Erika Santoso",    "tahu_shape": "no",  "tinggi": 164, "shoulder": 45, "bust": 93, "waist": 75, "hip": 85, "body_shape": "inverted",  "gaya": ["formal"], "outfit": ["outer", "blazer", "celana"], "created_at": "2026-06-10T08:52:37+00:00"},
    {"nama": "Feby Amalia",      "tahu_shape": "yes", "tinggi": 162, "shoulder": 44, "bust": 92, "waist": 74, "hip": 84, "body_shape": "inverted",  "gaya": ["formal"], "outfit": ["blazer", "outer"],           "created_at": "2026-06-11T14:37:19+00:00"},
    {"nama": "Maya Anggraini",   "tahu_shape": "no",  "tinggi": 165, "shoulder": 46, "bust": 95, "waist": 77, "hip": 87, "body_shape": "inverted",  "gaya": ["formal"], "outfit": ["outer", "blazer", "kemeja"], "created_at": "2026-06-12T10:23:45+00:00"},
    {"nama": "Rena Agustina",    "tahu_shape": "yes", "tinggi": 164, "shoulder": 44, "bust": 92, "waist": 74, "hip": 84, "body_shape": "inverted",  "gaya": ["formal"], "outfit": ["blazer", "outer"],           "created_at": "2026-06-13T17:48:32+00:00"},
    {"nama": "Dinda Ayu",        "tahu_shape": "no",  "tinggi": 160, "shoulder": 43, "bust": 90, "waist": 72, "hip": 82, "body_shape": "inverted",  "gaya": ["formal"], "outfit": ["outer", "blazer", "celana"], "created_at": "2026-06-14T09:14:27+00:00"},

    # ── Pear + formal → outer ───────────────────────────────────────────────────
    {"nama": "Yasmin Fitri",     "tahu_shape": "no",  "tinggi": 158, "shoulder": 38, "bust": 82, "waist": 70, "hip": 97, "body_shape": "pear",      "gaya": ["formal"], "outfit": ["blazer", "outer"],           "created_at": "2026-06-07T11:34:28+00:00"},
    {"nama": "Zahra Maulida",    "tahu_shape": "yes", "tinggi": 160, "shoulder": 39, "bust": 84, "waist": 72, "hip": 99, "body_shape": "pear",      "gaya": ["formal"], "outfit": ["outer", "blazer", "rok"],    "created_at": "2026-06-08T17:28:53+00:00"},
    {"nama": "Shinta Lestari",   "tahu_shape": "no",  "tinggi": 155, "shoulder": 37, "bust": 80, "waist": 68, "hip": 95, "body_shape": "pear",      "gaya": ["formal"], "outfit": ["blazer", "outer"],           "created_at": "2026-06-09T07:53:41+00:00"},
    {"nama": "Gita Nirmala",     "tahu_shape": "no",  "tinggi": 156, "shoulder": 38, "bust": 81, "waist": 69, "hip": 96, "body_shape": "pear",      "gaya": ["formal"], "outfit": ["outer", "blazer", "celana"], "created_at": "2026-06-10T14:17:36+00:00"},
    {"nama": "Hana Ramadhani",   "tahu_shape": "yes", "tinggi": 159, "shoulder": 39, "bust": 83, "waist": 71, "hip": 98, "body_shape": "pear",      "gaya": ["formal"], "outfit": ["blazer", "outer"],           "created_at": "2026-06-11T18:42:23+00:00"},
    {"nama": "Bunga Citra",      "tahu_shape": "no",  "tinggi": 157, "shoulder": 38, "bust": 82, "waist": 70, "hip": 97, "body_shape": "pear",      "gaya": ["formal"], "outfit": ["outer", "blazer", "rok"],    "created_at": "2026-06-12T13:27:48+00:00"},
    {"nama": "Novita Sari",      "tahu_shape": "yes", "tinggi": 157, "shoulder": 38, "bust": 82, "waist": 70, "hip": 97, "body_shape": "pear",      "gaya": ["formal"], "outfit": ["blazer", "outer"],           "created_at": "2026-06-13T20:53:17+00:00"},
    {"nama": "Silva Maharani",   "tahu_shape": "no",  "tinggi": 156, "shoulder": 37, "bust": 80, "waist": 68, "hip": 95, "body_shape": "pear",      "gaya": ["formal"], "outfit": ["outer", "blazer", "celana"], "created_at": "2026-06-14T12:38:54+00:00"},

    # ── Rectangle + formal → fullbody ───────────────────────────────────────────
    {"nama": "Viona Maharani",   "tahu_shape": "no",  "tinggi": 165, "shoulder": 40, "bust": 84, "waist": 80, "hip": 83, "body_shape": "rectangle", "gaya": ["formal"], "outfit": ["setelan", "dress"],           "created_at": "2026-06-07T16:48:37+00:00"},
    {"nama": "Windy Saraswati",  "tahu_shape": "yes", "tinggi": 163, "shoulder": 41, "bust": 86, "waist": 82, "hip": 85, "body_shape": "rectangle", "gaya": ["formal"], "outfit": ["dress", "setelan"],           "created_at": "2026-06-08T20:13:42+00:00"},
    {"nama": "Yuliana Putri",    "tahu_shape": "no",  "tinggi": 160, "shoulder": 40, "bust": 84, "waist": 80, "hip": 83, "body_shape": "rectangle", "gaya": ["formal"], "outfit": ["setelan", "dress", "kemeja"], "created_at": "2026-06-09T12:27:18+00:00"},
    {"nama": "Zerlinda Amara",   "tahu_shape": "yes", "tinggi": 162, "shoulder": 41, "bust": 85, "waist": 81, "hip": 84, "body_shape": "rectangle", "gaya": ["formal"], "outfit": ["dress", "setelan", "kemeja"], "created_at": "2026-06-10T19:52:43+00:00"},
    {"nama": "Ike Puspita",      "tahu_shape": "no",  "tinggi": 163, "shoulder": 40, "bust": 84, "waist": 80, "hip": 83, "body_shape": "rectangle", "gaya": ["formal"], "outfit": ["setelan", "dress"],           "created_at": "2026-06-11T08:17:34+00:00"},
    {"nama": "Jihan Amelia",     "tahu_shape": "yes", "tinggi": 161, "shoulder": 40, "bust": 84, "waist": 80, "hip": 83, "body_shape": "rectangle", "gaya": ["formal"], "outfit": ["dress", "setelan", "blazer"], "created_at": "2026-06-12T15:43:28+00:00"},
    {"nama": "Octavia Putri",    "tahu_shape": "no",  "tinggi": 160, "shoulder": 40, "bust": 83, "waist": 79, "hip": 82, "body_shape": "rectangle", "gaya": ["formal"], "outfit": ["setelan", "dress"],           "created_at": "2026-06-13T09:28:54+00:00"},
    {"nama": "Tika Purnama",     "tahu_shape": "yes", "tinggi": 161, "shoulder": 40, "bust": 84, "waist": 80, "hip": 83, "body_shape": "rectangle", "gaya": ["formal"], "outfit": ["dress", "setelan", "kemeja"], "created_at": "2026-06-14T17:53:42+00:00"},
]

print(f"Memasukkan {len(data)} data dummy ke Supabase...")
berhasil = 0
gagal    = 0

for i, row in enumerate(data):
    r = requests.post(url, headers=headers, data=json.dumps(row))
    if r.status_code in (200, 201):
        berhasil += 1
        print(f"  [{i+1:02d}] OK {row['nama']}")
    else:
        gagal += 1
        print(f"  [{i+1:02d}] GAGAL {row['nama']} -> {r.status_code}: {r.text}")

print(f"\nSelesai: {berhasil} berhasil, {gagal} gagal")
