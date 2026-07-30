from flask import Flask, request, jsonify, send_file
import joblib
import pandas as pd
import os
import base64
import tempfile
import threading
from dotenv import load_dotenv

try:
    from gradio_client import Client as HFClient, file as hf_file
except ImportError:
    HFClient = None
    hf_file = None

load_dotenv()

app = Flask(__name__, static_folder='.', static_url_path='')

BASE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(BASE)

# Virtual try-on gratis via Hugging Face Space (community GPU, tanpa billing).
# HF_TOKEN opsional (isi di .env) — kalau ada, dapat prioritas antrean lebih baik.
HF_SPACE = "yisol/IDM-VTON"
HF_TOKEN = os.environ.get("HF_TOKEN", "").strip() or None
_hf_client = None
_hf_lock = threading.Lock()

def _get_hf_client():
    global _hf_client
    with _hf_lock:
        if _hf_client is None:
            # Timeout digedein — Space gratis suka butuh waktu "bangun" (cold start)
            # + proses generate-nya sendiri, default timeout httpx suka kepotong duluan.
            _hf_client = HFClient(HF_SPACE, token=HF_TOKEN, httpx_kwargs={"timeout": 300})
        return _hf_client

MODELS_DIR = os.path.join(PARENT, "research", "models")

model    = joblib.load(os.path.join(MODELS_DIR, "model_c45.pkl"))
le_body  = joblib.load(os.path.join(MODELS_DIR, "le_body.pkl"))
mlb      = joblib.load(os.path.join(MODELS_DIR, "mlb_gaya.pkl"))
le_label = joblib.load(os.path.join(MODELS_DIR, "le_label.pkl"))

gaya_cols = [f"gaya_{g}" for g in mlb.classes_]

BODY_GAYA_ITEM = {
    "apple": {
        "bohemian": {"atasan": ["blus flowy", "tunik"],          "bawahan": ["rok A-line"],                    "fullbody": ["dress wrap", "dress empire"],       "outer": ["cardigan panjang"]},
        "casual":   {"atasan": ["kaos oversize", "blus flowy"],  "bawahan": ["celana bootcut", "rok A-line"],  "fullbody": ["dress A-line", "jumpsuit longgar"],  "outer": ["outer panjang"]},
        "classic":  {"atasan": ["blus empire", "kemeja flowy"],  "bawahan": ["celana bootcut", "rok A-line"],  "fullbody": ["setelan blazer panjang"],            "outer": ["blazer panjang"]},
        "formal":   {"atasan": ["kemeja empire"],                "bawahan": ["celana bootcut"],                "fullbody": ["setelan blazer panjang"],            "outer": ["blazer panjang"]},
        "sporty":   {"atasan": ["kaos oversize"],                "bawahan": ["celana wide-leg"],               "fullbody": ["jumpsuit longgar"],                  "outer": ["outer panjang"]},
    },
    "hourglass": {
        "bohemian": {"atasan": ["blus wrap", "knit fitted"],      "bawahan": ["rok midi", "rok wrap"],           "fullbody": ["dress wrap", "dress fitted"],        "outer": ["outer berpotongan"]},
        "casual":   {"atasan": ["kaos fitted", "blus tucked-in"], "bawahan": ["jeans skinny", "celana straight"],"fullbody": ["dress wrap", "jumpsuit fitted"],     "outer": ["outer fitted"]},
        "classic":  {"atasan": ["kemeja tucked-in", "blus fitted"],"bawahan": ["rok pencil", "celana straight"], "fullbody": ["setelan fitted"],                    "outer": ["blazer fitted"]},
        "formal":   {"atasan": ["kemeja tucked-in"],              "bawahan": ["rok pencil"],                     "fullbody": ["setelan fitted"],                    "outer": ["blazer fitted"]},
        "sporty":   {"atasan": ["kaos fitted"],                   "bawahan": ["celana straight", "legging"],     "fullbody": ["jumpsuit fitted"],                   "outer": ["outer fitted"]},
    },
    "inverted": {
        "bohemian": {"atasan": ["blus basic", "knit V-neck"],    "bawahan": ["rok flared", "rok A-line"],      "fullbody": ["dress A-line", "dress flared"],      "outer": ["cardigan panjang"]},
        "casual":   {"atasan": ["kaos V-neck", "blus simple"],   "bawahan": ["celana wide-leg", "jeans flared"],"fullbody": ["dress A-line", "jumpsuit lebar bawah"],"outer": ["cardigan panjang"]},
        "classic":  {"atasan": ["kemeja V-neck", "blus basic"],  "bawahan": ["celana wide-leg", "rok A-line"], "fullbody": ["setelan rok flared"],                "outer": ["blazer single button"]},
        "formal":   {"atasan": ["kemeja V-neck"],                "bawahan": ["celana wide-leg"],               "fullbody": ["setelan rok flared"],                "outer": ["blazer single button"]},
        "sporty":   {"atasan": ["kaos V-neck"],                  "bawahan": ["celana wide-leg", "celana palazzo"],"fullbody": ["jumpsuit lebar bawah"],           "outer": ["cardigan panjang"]},
    },
    "pear": {
        "bohemian": {"atasan": ["blus ruffle", "knit off-shoulder"],"bawahan": ["rok A-line", "rok flared"],   "fullbody": ["dress A-line", "dress wrap"],        "outer": ["outer bahu tegas"]},
        "casual":   {"atasan": ["kaos grafis", "blus off-shoulder"],"bawahan": ["celana wide-leg", "rok A-line"],"fullbody": ["dress A-line", "jumpsuit bahu lebar"],"outer": ["outer bahu tegas"]},
        "classic":  {"atasan": ["kemeja berdetail dada", "blus berdetail bahu"],"bawahan": ["celana wide-leg", "rok midi flared"],"fullbody": ["setelan atasan berdetail"],"outer": ["blazer bahu tegas"]},
        "formal":   {"atasan": ["kemeja berdetail bahu"],        "bawahan": ["celana wide-leg"],               "fullbody": ["setelan atasan berdetail"],          "outer": ["blazer bahu tegas"]},
        "sporty":   {"atasan": ["kaos grafis dada", "kaos bahu lebar"],"bawahan": ["celana wide-leg", "celana palazzo"],"fullbody": ["jumpsuit bahu lebar"],      "outer": ["outer bahu tegas"]},
    },
    "rectangle": {
        "bohemian": {"atasan": ["blus ruffle", "knit peplum"],   "bawahan": ["rok flared", "rok ruffled"],     "fullbody": ["dress wrap", "dress berpotongan"],   "outer": ["outer cropped"]},
        "casual":   {"atasan": ["kaos crop", "blus tied"],       "bawahan": ["rok flared", "celana wide-leg"], "fullbody": ["dress wrap", "jumpsuit ikat pinggang"],"outer": ["outer cropped"]},
        "classic":  {"atasan": ["kemeja peplum", "blus tucked-in"],"bawahan": ["rok flared", "celana wide-leg"],"fullbody": ["setelan ikat pinggang"],            "outer": ["blazer cropped"]},
        "formal":   {"atasan": ["kemeja peplum"],                "bawahan": ["rok flared"],                    "fullbody": ["setelan ikat pinggang"],             "outer": ["blazer cropped"]},
        "sporty":   {"atasan": ["kaos crop", "kaos tied"],       "bawahan": ["celana wide-leg", "rok flared"], "fullbody": ["jumpsuit ikat pinggang"],            "outer": ["outer cropped"]},
    },
}


def get_items(body_shape: str, gaya_list: list, kategori: str) -> list:
    items = []
    bs_map = BODY_GAYA_ITEM.get(body_shape, {})
    for g in gaya_list:
        for item in bs_map.get(g, {}).get(kategori, []):
            if item not in items:
                items.append(item)
    return items


@app.route("/")
def index():
    return send_file(os.path.join(BASE, "La Silhouette.dc.html"))


@app.route("/recommend", methods=["POST"])
def recommend():
    data = request.get_json()
    body_shape = (data.get("body_shape") or "").strip().lower()
    gaya = [g.strip().lower() for g in (data.get("gaya") or [])]

    if not body_shape or not gaya:
        return jsonify({"error": "Mohon pilih bentuk tubuh dan gaya pakaian"}), 400

    try:
        bs = le_body.transform([body_shape])[0]
        gaya_bin = mlb.transform([gaya])[0]
        inp = pd.DataFrame([[bs] + list(gaya_bin)], columns=["body_shape_enc"] + gaya_cols)
        enc = int(model.predict(inp)[0])
        fokus = le_label.inverse_transform([enc])[0]

        result = {"fokus": fokus}
        if fokus == "fullbody":
            result["fullbody"] = get_items(body_shape, gaya, "fullbody")
        elif fokus == "atasan":
            result["atasan"] = get_items(body_shape, gaya, "atasan")
            result["bawahan"] = get_items(body_shape, gaya, "bawahan")
        elif fokus == "bawahan":
            result["bawahan"] = get_items(body_shape, gaya, "bawahan")
            result["atasan"] = get_items(body_shape, gaya, "atasan")
        elif fokus == "outer":
            result["outer"] = get_items(body_shape, gaya, "outer")
            result["atasan"] = get_items(body_shape, gaya, "atasan")
            result["bawahan"] = get_items(body_shape, gaya, "bawahan")

        return jsonify(result)

    except ValueError as e:
        return jsonify({"error": f"Data tidak dikenali: {e}"}), 422

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def _write_tmp_png(img_bytes):
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        f.write(img_bytes)
        return f.name


def _is_probably_blank(path, min_bytes=8000):
    # Sebagian file crop _top/_bottom hasil autocrop lama ternyata kosong/putih polos
    # (ukurannya cuma beberapa KB, dibanding foto asli yang puluhan-ratusan KB).
    # Daripada kirim gambar kosong ke AI (bikin hasil ngaco), potongan ini di-skip.
    try:
        return os.path.getsize(path) < min_bytes
    except OSError:
        return True


# Urutan tempel: bawah/fullbody dulu, lalu atasan, lalu outer paling atas.
GARMENT_ORDER = {"fullbody": 0, "atasan": 1, "bawahan": 2, "outer": 3}


@app.route("/generate-tryon", methods=["POST"])
def generate_tryon():
    if HFClient is None:
        return jsonify({"error": "Library gradio_client belum terpasang. Jalankan: pip install gradio_client"}), 500

    data = request.get_json() or {}
    photo = data.get("photo") or ""
    garments = data.get("garments") or []
    if not photo or not garments:
        return jsonify({"error": "Foto dan minimal 1 item rekomendasi wajib diisi"}), 400

    try:
        b64 = photo.split(",", 1)[1] if "," in photo else photo
        current_bytes = base64.b64decode(b64)
    except Exception:
        return jsonify({"error": "Format foto tidak valid"}), 400

    garments_sorted = sorted(garments, key=lambda g: GARMENT_ORDER.get(g.get("category", ""), 9))

    current_tmp = None
    applied = []
    try:
        current_tmp = _write_tmp_png(current_bytes)
        client = _get_hf_client()

        for g in garments_sorted:
            garment_url = (g.get("image") or "").strip()
            garment_label = (g.get("label") or "pakaian").strip()
            if not garment_url:
                continue
            garment_path = os.path.join(BASE, garment_url.split("?")[0].replace("/", os.sep))
            if not os.path.exists(garment_path):
                return jsonify({"error": f"Gambar pakaian tidak ditemukan: {garment_url}"}), 404
            if _is_probably_blank(garment_path):
                continue

            result = client.predict(
                dict={"background": hf_file(current_tmp), "layers": [], "composite": None},
                garm_img=hf_file(garment_path),
                garment_des=garment_label,
                is_checked=True,
                is_checked_crop=False,
                denoise_steps=30,
                seed=42,
                api_name="/tryon",
            )
            out_path = result[0] if isinstance(result, (list, tuple)) else result
            with open(out_path, "rb") as f:
                current_bytes = f.read()

            os.remove(current_tmp)
            current_tmp = _write_tmp_png(current_bytes)
            applied.append(garment_label)

        if not applied:
            return jsonify({"error": "Tidak ada item valid untuk di-generate"}), 400

        out_b64 = base64.b64encode(current_bytes).decode()
        return jsonify({"image": f"data:image/png;base64,{out_b64}", "applied": applied})
    except Exception as e:
        return jsonify({"error": f"Gagal generate (Hugging Face Space mungkin sedang sibuk/tidur, coba lagi): {e}"}), 502
    finally:
        if current_tmp and os.path.exists(current_tmp):
            os.remove(current_tmp)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
