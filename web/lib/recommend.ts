import { predict } from "./tree.ts";
import { BODY_GAYA_ITEM, type BodyShape, type Gaya, type Kategori } from "./recommend-data.ts";

const BODY_SHAPES: readonly BodyShape[] = ["apple", "hourglass", "inverted", "pear", "rectangle"];
const GAYA_LIST: readonly Gaya[] = ["bohemian", "casual", "classic", "formal", "sporty"];

function isBodyShape(v: string): v is BodyShape {
  return (BODY_SHAPES as readonly string[]).includes(v);
}

function isGaya(v: string): v is Gaya {
  return (GAYA_LIST as readonly string[]).includes(v);
}

function getItems(bodyShape: BodyShape, gayaList: string[], kategori: Kategori): string[] {
  const items: string[] = [];
  const bsMap = BODY_GAYA_ITEM[bodyShape];
  for (const g of gayaList) {
    if (!isGaya(g)) continue;
    for (const item of bsMap[g][kategori]) {
      if (!items.includes(item)) items.push(item);
    }
  }
  return items;
}

export interface RecommendResult {
  fokus: Kategori;
  fullbody?: string[];
  atasan?: string[];
  bawahan?: string[];
  outer?: string[];
}

export function buildRecommendation(bodyShape: string, gaya: string[]): RecommendResult {
  if (!isBodyShape(bodyShape)) {
    throw new Error(`body_shape tidak dikenali: ${bodyShape}`);
  }

  const bodyShapeEnc = BODY_SHAPES.indexOf(bodyShape);
  const fokus = predict({
    body_shape_enc: bodyShapeEnc,
    gaya_bohemian: gaya.includes("bohemian") ? 1 : 0,
    gaya_casual: gaya.includes("casual") ? 1 : 0,
    gaya_classic: gaya.includes("classic") ? 1 : 0,
    gaya_formal: gaya.includes("formal") ? 1 : 0,
    gaya_sporty: gaya.includes("sporty") ? 1 : 0,
  });

  const result: RecommendResult = { fokus };

  if (fokus === "fullbody") {
    result.fullbody = getItems(bodyShape, gaya, "fullbody");
  } else if (fokus === "atasan") {
    result.atasan = getItems(bodyShape, gaya, "atasan");
    result.bawahan = getItems(bodyShape, gaya, "bawahan");
  } else if (fokus === "bawahan") {
    result.bawahan = getItems(bodyShape, gaya, "bawahan");
    result.atasan = getItems(bodyShape, gaya, "atasan");
  } else if (fokus === "outer") {
    result.outer = getItems(bodyShape, gaya, "outer");
    result.atasan = getItems(bodyShape, gaya, "atasan");
    result.bawahan = getItems(bodyShape, gaya, "bawahan");
  }

  return result;
}
