import os, requests
from dotenv import load_dotenv
from collections import Counter

load_dotenv()
URL = os.environ["SUPABASE_URL"]
KEY = os.environ["SUPABASE_KEY"]
HEADERS = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}

r = requests.get(f"{URL}/rest/v1/responses?select=body_shape,gaya,outfit&limit=300", headers=HEADERS)
data = r.json()

shapes = Counter(row["body_shape"] for row in data if row.get("body_shape"))
print("Body shape values:")
for k, v in sorted(shapes.items()):
    print(f"  '{k}' : {v} records")

print("\nContoh gaya (5 data pertama):")
for row in data[:5]:
    print(f"  {row['body_shape']} | {row['gaya']} | {row['outfit']}")
