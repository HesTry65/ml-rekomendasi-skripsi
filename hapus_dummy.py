import os, requests
from dotenv import load_dotenv

load_dotenv()

url     = os.environ["SUPABASE_URL"] + "/rest/v1/responses"
headers = {
    "apikey":        os.environ["SUPABASE_KEY"],
    "Authorization": "Bearer " + os.environ["SUPABASE_KEY"],
    "Content-Type":  "application/json",
}

# Ambil semua ID
get_url = url + "?select=id"
r       = requests.get(get_url, headers=headers)
rows    = r.json()
print(f"Total baris ditemukan: {len(rows)}")

berhasil = 0
for row in rows:
    id_val = row["id"]
    del_r  = requests.delete(url + f"?id=eq.{id_val}", headers=headers)
    if del_r.status_code in (200, 204):
        berhasil += 1
    else:
        print(f"  Gagal hapus id={id_val}: {del_r.status_code}")

print(f"Berhasil dihapus: {berhasil} baris")
