export type BodyShape = "apple" | "hourglass" | "inverted" | "pear" | "rectangle";
export type Gaya = "bohemian" | "casual" | "classic" | "formal" | "sporty";
export type Kategori = "atasan" | "bawahan" | "fullbody" | "outer";

type ItemMap = Record<Kategori, string[]>;

export const BODY_GAYA_ITEM: Record<BodyShape, Record<Gaya, ItemMap>> = {
  apple: {
    bohemian: { atasan: ["blus flowy", "tunik"], bawahan: ["rok A-line"], fullbody: ["dress wrap", "dress empire"], outer: ["cardigan panjang"] },
    casual: { atasan: ["kaos oversize", "blus flowy"], bawahan: ["celana bootcut", "rok A-line"], fullbody: ["dress A-line", "jumpsuit longgar"], outer: ["outer panjang"] },
    classic: { atasan: ["blus empire", "kemeja flowy"], bawahan: ["celana bootcut", "rok A-line"], fullbody: ["setelan blazer panjang"], outer: ["blazer panjang"] },
    formal: { atasan: ["kemeja empire"], bawahan: ["celana bootcut"], fullbody: ["setelan blazer panjang"], outer: ["blazer panjang"] },
    sporty: { atasan: ["kaos oversize"], bawahan: ["celana wide-leg"], fullbody: ["jumpsuit longgar"], outer: ["outer panjang"] },
  },
  hourglass: {
    bohemian: { atasan: ["blus wrap", "knit fitted"], bawahan: ["rok midi", "rok wrap"], fullbody: ["dress wrap", "dress fitted"], outer: ["outer berpotongan"] },
    casual: { atasan: ["kaos fitted", "blus tucked-in"], bawahan: ["jeans skinny", "celana straight"], fullbody: ["dress wrap", "jumpsuit fitted"], outer: ["outer fitted"] },
    classic: { atasan: ["kemeja tucked-in", "blus fitted"], bawahan: ["rok pencil", "celana straight"], fullbody: ["setelan fitted"], outer: ["blazer fitted"] },
    formal: { atasan: ["kemeja tucked-in"], bawahan: ["rok pencil"], fullbody: ["setelan fitted"], outer: ["blazer fitted"] },
    sporty: { atasan: ["kaos fitted"], bawahan: ["celana straight", "legging"], fullbody: ["jumpsuit fitted"], outer: ["outer fitted"] },
  },
  inverted: {
    bohemian: { atasan: ["blus basic", "knit V-neck"], bawahan: ["rok flared", "rok A-line"], fullbody: ["dress A-line", "dress flared"], outer: ["cardigan panjang"] },
    casual: { atasan: ["kaos V-neck", "blus simple"], bawahan: ["celana wide-leg", "jeans flared"], fullbody: ["dress A-line", "jumpsuit lebar bawah"], outer: ["cardigan panjang"] },
    classic: { atasan: ["kemeja V-neck", "blus basic"], bawahan: ["celana wide-leg", "rok A-line"], fullbody: ["setelan rok flared"], outer: ["blazer single button"] },
    formal: { atasan: ["kemeja V-neck"], bawahan: ["celana wide-leg"], fullbody: ["setelan rok flared"], outer: ["blazer single button"] },
    sporty: { atasan: ["kaos V-neck"], bawahan: ["celana wide-leg", "celana palazzo"], fullbody: ["jumpsuit lebar bawah"], outer: ["cardigan panjang"] },
  },
  pear: {
    bohemian: { atasan: ["blus ruffle", "knit off-shoulder"], bawahan: ["rok A-line", "rok flared"], fullbody: ["dress A-line", "dress wrap"], outer: ["outer bahu tegas"] },
    casual: { atasan: ["kaos grafis", "blus off-shoulder"], bawahan: ["celana wide-leg", "rok A-line"], fullbody: ["dress A-line", "jumpsuit bahu lebar"], outer: ["outer bahu tegas"] },
    classic: { atasan: ["kemeja berdetail dada", "blus berdetail bahu"], bawahan: ["celana wide-leg", "rok midi flared"], fullbody: ["setelan atasan berdetail"], outer: ["blazer bahu tegas"] },
    formal: { atasan: ["kemeja berdetail bahu"], bawahan: ["celana wide-leg"], fullbody: ["setelan atasan berdetail"], outer: ["blazer bahu tegas"] },
    sporty: { atasan: ["kaos grafis dada", "kaos bahu lebar"], bawahan: ["celana wide-leg", "celana palazzo"], fullbody: ["jumpsuit bahu lebar"], outer: ["outer bahu tegas"] },
  },
  rectangle: {
    bohemian: { atasan: ["blus ruffle", "knit peplum"], bawahan: ["rok flared", "rok ruffled"], fullbody: ["dress wrap", "dress berpotongan"], outer: ["outer cropped"] },
    casual: { atasan: ["kaos crop", "blus tied"], bawahan: ["rok flared", "celana wide-leg"], fullbody: ["dress wrap", "jumpsuit ikat pinggang"], outer: ["outer cropped"] },
    classic: { atasan: ["kemeja peplum", "blus tucked-in"], bawahan: ["rok flared", "celana wide-leg"], fullbody: ["setelan ikat pinggang"], outer: ["blazer cropped"] },
    formal: { atasan: ["kemeja peplum"], bawahan: ["rok flared"], fullbody: ["setelan ikat pinggang"], outer: ["blazer cropped"] },
    sporty: { atasan: ["kaos crop", "kaos tied"], bawahan: ["celana wide-leg", "rok flared"], fullbody: ["jumpsuit ikat pinggang"], outer: ["outer cropped"] },
  },
};
