import os, ast, requests, json
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

# ── Pola expected label per body_shape + gaya (dari distribusi data asli) ──────
EXPECTED = {
    # apple
    ("apple", "bohemian"):                          "bawahan",
    ("apple", "casual"):                            "atasan",
    ("apple", "classic"):                           "fullbody",
    ("apple", "formal"):                            "outer",
    ("apple", "sporty"):                            "outer",
    ("apple", "bohemian_casual"):                   "atasan",
    ("apple", "casual_classic"):                    "atasan",
    ("apple", "casual_formal"):                     "atasan",
    ("apple", "casual_sporty"):                     "atasan",
    ("apple", "bohemian_casual_classic_formal_sporty"): "outer",
    # hourglass
    ("hourglass", "bohemian"):                      "fullbody",
    ("hourglass", "casual"):                        "fullbody",
    ("hourglass", "classic"):                       "fullbody",
    ("hourglass", "formal"):                        "fullbody",
    ("hourglass", "sporty"):                        "fullbody",
    ("hourglass", "bohemian_casual"):               "fullbody",
    ("hourglass", "casual_classic"):                "fullbody",
    ("hourglass", "casual_classic_formal"):         "fullbody",
    ("hourglass", "casual_formal"):                 "fullbody",
    ("hourglass", "casual_sporty"):                 "fullbody",
    ("hourglass", "classic_formal"):                "fullbody",
    ("hourglass", "bohemian_casual_classic_formal_sporty"): "fullbody",
    # inverted
    ("inverted", "bohemian"):                       "bawahan",
    ("inverted", "casual"):                         "atasan",
    ("inverted", "classic"):                        "bawahan",
    ("inverted", "formal"):                         "outer",
    ("inverted", "sporty"):                         "outer",
    ("inverted", "bohemian_casual"):                "atasan",
    ("inverted", "casual_bohemian"):                "atasan",
    ("inverted", "casual_classic"):                 "atasan",
    ("inverted", "casual_formal"):                  "atasan",
    ("inverted", "casual_sporty"):                  "atasan",
    ("inverted", "classic_formal"):                 "outer",
    ("inverted", "formal_classic"):                 "outer",
    ("inverted", "bohemian_formal"):                "outer",
    ("inverted", "bohemian_casual_classic_formal_sporty"): "atasan",
    # pear
    ("pear", "bohemian"):                           "bawahan",
    ("pear", "casual"):                             "atasan",
    ("pear", "classic"):                            "bawahan",
    ("pear", "formal"):                             "outer",
    ("pear", "sporty"):                             "atasan",
    ("pear", "bohemian_casual"):                    "bawahan",
    ("pear", "casual_bohemian"):                    "atasan",
    ("pear", "casual_classic"):                     "atasan",
    ("pear", "casual_formal"):                      "atasan",
    ("pear", "casual_sporty"):                      "atasan",
    ("pear", "classic_formal"):                     "outer",
    ("pear", "bohemian_formal"):                    "bawahan",
    ("pear", "formal_sporty"):                      "bawahan",
    ("pear", "casual_classic_sporty_formal"):       "atasan",
    ("pear", "bohemian_casual_classic_formal_sporty"): "atasan",
    # rectangle
    ("rectangle", "bohemian"):                      "bawahan",
    ("rectangle", "casual"):                        "atasan",
    ("rectangle", "classic"):                       "atasan",
    ("rectangle", "formal"):                        "fullbody",
    ("rectangle", "sporty"):                        "outer",
    ("rectangle", "bohemian_casual"):               "atasan",
    ("rectangle", "casual_bohemian"):               "atasan",
    ("rectangle", "casual_classic"):                "atasan",
    ("rectangle", "casual_formal"):                 "atasan",
    ("rectangle", "casual_sporty"):                 "atasan",
    ("rectangle", "bohemian_casual_classic"):       "atasan",
    ("rectangle", "bohemian_casual_classic_formal_sporty"): "atasan",
}

# ── Outfit items per label + gaya ───────────────────────────────────────────────
GAYA_ITEM = {
    "bohemian": {"atasan": ["blus", "knit"],        "bawahan": ["rok"],             "fullbody": ["dress"],           "outer": ["outer"]},
    "casual":   {"atasan": ["kaos", "blus"],         "bawahan": ["jeans", "celana"], "fullbody": ["dress", "jumpsuit"],"outer": ["outer"]},
    "classic":  {"atasan": ["kemeja", "blus"],       "bawahan": ["celana", "rok"],   "fullbody": ["setelan"],         "outer": ["blazer"]},
    "formal":   {"atasan": ["kemeja"],               "bawahan": ["celana"],          "fullbody": ["setelan"],         "outer": ["blazer"]},
    "sporty":   {"atasan": ["kaos"],                 "bawahan": ["celana"],          "fullbody": ["jumpsuit"],        "outer": ["outer"]},
}

DEFAULT_ITEMS = {
    "atasan":   ["kaos", "kemeja"],
    "bawahan":  ["rok", "celana"],
    "fullbody": ["setelan", "dress"],
    "outer":    ["blazer", "outer"],
}

KATEGORI = {
    "dress": "fullbody", "jumpsuit": "fullbody", "setelan": "fullbody",
    "rok": "bawahan", "celana": "bawahan", "jeans": "bawahan",
    "blus": "atasan", "kemeja": "atasan", "kaos": "atasan", "knit": "atasan",
    "blazer": "outer", "outer": "outer",
}

def get_label_mayoritas(outfit_list):
    from collections import Counter
    kat = [KATEGORI.get(o) for o in outfit_list if KATEGORI.get(o)]
    if not kat:
        return None
    count = Counter(kat)
    max_c = max(count.values())
    maj   = [k for k, v in count.items() if v == max_c]
    if len(maj) == 1:
        return maj[0]
    return KATEGORI.get(outfit_list[0])

def get_outfit_for_label(gaya_list, label):
    items = []
    for g in gaya_list:
        if g in GAYA_ITEM:
            for item in GAYA_ITEM[g].get(label, []):
                if item not in items:
                    items.append(item)
    if len(items) < 2:
        for item in DEFAULT_ITEMS[label]:
            if item not in items:
                items.append(item)
    return items[:3]

# ── Ambil semua data dari Supabase ─────────────────────────────────────────────
r    = requests.get(url + "?select=*&order=id.asc", headers=headers)
rows = r.json()
print(f"Total data: {len(rows)} baris\n")

difix  = 0
skip   = 0

for row in rows:
    try:
        gaya_raw   = row.get("gaya", [])
        outfit_raw = row.get("outfit", [])
        body_shape = row.get("body_shape", "")
        row_id     = row["id"]

        if isinstance(gaya_raw, str):
            gaya_raw = ast.literal_eval(gaya_raw)
        if isinstance(outfit_raw, str):
            outfit_raw = ast.literal_eval(outfit_raw)

        gaya_sorted = "_".join(sorted(gaya_raw))
        key = (body_shape, gaya_sorted)

        # Cari expected label
        expected_label = EXPECTED.get(key)
        if not expected_label:
            skip += 1
            continue

        # Cek label sekarang
        current_label = get_label_mayoritas(outfit_raw)

        # Kalau sudah sesuai, skip
        if current_label == expected_label:
            skip += 1
            continue

        # Fix outfit
        new_outfit = get_outfit_for_label(gaya_raw, expected_label)

        # Update di Supabase (hanya kolom outfit)
        patch_url = url + f"?id=eq.{row_id}"
        patch_r   = requests.patch(
            patch_url,
            headers=headers,
            data=json.dumps({"outfit": new_outfit})
        )

        if patch_r.status_code in (200, 204):
            difix += 1
            print(f"  Fix [{row_id}] {row.get('nama','?'):15s} | {body_shape:10s} | {gaya_sorted:30s} | {current_label} -> {expected_label} | outfit: {new_outfit}")
        else:
            print(f"  GAGAL [{row_id}]: {patch_r.status_code} {patch_r.text}")

    except Exception as e:
        print(f"  ERROR row {row.get('id','?')}: {e}")

print(f"\nSelesai: {difix} baris difix, {skip} baris sudah benar/dilewati")
