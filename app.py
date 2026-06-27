from flask import Flask, request, jsonify, send_file
import joblib
import pandas as pd
import os

app = Flask(__name__)

BASE = os.path.dirname(os.path.abspath(__file__))

model    = joblib.load(os.path.join(BASE, "model_c45.pkl"))
le_body  = joblib.load(os.path.join(BASE, "le_body.pkl"))
mlb      = joblib.load(os.path.join(BASE, "mlb_gaya.pkl"))
le_label = joblib.load(os.path.join(BASE, "le_label.pkl"))

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
    return send_file(os.path.join(BASE, "index.html"))


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
            result["outer"]   = get_items(body_shape, gaya, "outer")
            result["atasan"]  = get_items(body_shape, gaya, "atasan")
            result["bawahan"] = get_items(body_shape, gaya, "bawahan")

        return jsonify(result)

    except ValueError as e:
        return jsonify({"error": f"Data tidak dikenali: {e}"}), 422
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
