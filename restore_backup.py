import os, ast, math, requests, json
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

url     = os.environ["SUPABASE_URL"] + "/rest/v1/responses"
headers = {
    "apikey":        os.environ["SUPABASE_KEY"],
    "Authorization": "Bearer " + os.environ["SUPABASE_KEY"],
    "Content-Type":  "application/json",
    "Prefer":        "return=minimal"
}

df = pd.read_csv("backup_sebelum_fix_outfit.csv")
print(f"Total baris di CSV: {len(df)}")

berhasil = 0
gagal    = 0

for i, row in df.iterrows():
    def parse_list(val):
        try:
            return ast.literal_eval(str(val))
        except:
            return []

    def parse_float(val):
        try:
            v = float(val)
            return None if math.isnan(v) else v
        except:
            return None

    record = {
        "nama":        str(row["nama"]).strip(),
        "tahu_shape":  str(row["tahu_shape"]).strip(),
        "tinggi":      parse_float(row["tinggi"]),
        "shoulder":    parse_float(row["shoulder"]),
        "bust":        parse_float(row["bust"]),
        "waist":       parse_float(row["waist"]),
        "hip":         parse_float(row["hip"]),
        "body_shape":  str(row["body_shape"]).strip(),
        "gaya":        parse_list(row["gaya"]),
        "outfit":      parse_list(row["outfit"]),
        "created_at":  str(row["created_at"]).strip(),
    }

    r = requests.post(url, headers=headers, data=json.dumps(record))
    if r.status_code in (200, 201):
        berhasil += 1
        print(f"  [{berhasil:03d}] OK {record['nama']}")
    else:
        gagal += 1
        print(f"  GAGAL {record['nama']} -> {r.status_code}: {r.text}")

print(f"\nSelesai: {berhasil} berhasil, {gagal} gagal")
