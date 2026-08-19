import itertools
import json
import os

import joblib
import pandas as pd

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
MODELS_DIR = os.path.join(REPO_ROOT, "research", "models")
OUT_DIR = os.path.join(REPO_ROOT, "web", "data")
os.makedirs(OUT_DIR, exist_ok=True)

model = joblib.load(os.path.join(MODELS_DIR, "model_c45.pkl"))
le_body = joblib.load(os.path.join(MODELS_DIR, "le_body.pkl"))
mlb = joblib.load(os.path.join(MODELS_DIR, "mlb_gaya.pkl"))
le_label = joblib.load(os.path.join(MODELS_DIR, "le_label.pkl"))

gaya_cols = [f"gaya_{g}" for g in mlb.classes_]
feature_names = ["body_shape_enc"] + gaya_cols

tree = model.tree_


def export_node(node_id):
    if tree.feature[node_id] == -2:  # sklearn's TREE_UNDEFINED = leaf
        class_idx = int(tree.value[node_id][0].argmax())
        return {"leaf": str(le_label.classes_[class_idx])}
    return {
        "feature": feature_names[tree.feature[node_id]],
        "threshold": float(tree.threshold[node_id]),
        "left": export_node(int(tree.children_left[node_id])),
        "right": export_node(int(tree.children_right[node_id])),
    }


tree_json = export_node(0)
with open(os.path.join(OUT_DIR, "tree.json"), "w") as f:
    json.dump(tree_json, f, indent=2)

# 160-combo fixtures: 5 body shapes x 32 gaya boolean combos (2^5, incl. empty set)
fixtures = []
for body_shape in le_body.classes_:
    bs_enc = int(le_body.transform([body_shape])[0])
    for combo in itertools.product([0, 1], repeat=5):
        gaya_selected = [g for g, bit in zip(mlb.classes_, combo) if bit]
        gaya_bin = mlb.transform([gaya_selected])[0]
        inp = pd.DataFrame([[bs_enc] + list(gaya_bin)], columns=feature_names)
        enc = int(model.predict(inp)[0])
        expected = str(le_label.classes_[enc])

        input_row = {"body_shape_enc": bs_enc}
        for g, bit in zip(mlb.classes_, combo):
            input_row[f"gaya_{g}"] = int(bit)
        fixtures.append({"input": input_row, "expected": expected})

print("total fixtures:", len(fixtures))

with open(os.path.join(OUT_DIR, "tree-fixtures.json"), "w") as f:
    json.dump(fixtures, f, indent=2)


# Parity check: walk tree.json in pure Python (mirrors the TS walk in web/lib/tree.ts)
# against model.predict directly — this is the 0-mismatch proof the spec requires.
def walk(node, row):
    if "leaf" in node:
        return node["leaf"]
    val = row[node["feature"]]
    if val <= node["threshold"]:
        return walk(node["left"], row)
    return walk(node["right"], row)


mismatch_count = 0
for fx in fixtures:
    got = walk(tree_json, fx["input"])
    if got != fx["expected"]:
        mismatch_count += 1
        print("MISMATCH:", fx["input"], "expected", fx["expected"], "got", got)

print("mismatches:", mismatch_count)
assert mismatch_count == 0, f"{mismatch_count} mismatches found — do not commit tree.json"
