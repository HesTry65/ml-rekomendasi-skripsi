// Urutan tempel: bawah/fullbody dulu, lalu atasan, lalu outer paling atas
// (matches GARMENT_ORDER in the old app/app.py).
export const GARMENT_ORDER = { fullbody: 0, atasan: 1, bawahan: 2, outer: 3 };

export function sortByGarmentOrder(garments) {
  return garments
    .slice()
    .sort((a, b) => (GARMENT_ORDER[a.category] ?? 9) - (GARMENT_ORDER[b.category] ?? 9));
}

// Same 8000-byte threshold as the old app.py's _is_probably_blank(min_bytes=8000).
export function isBlankBySize(byteLength, minBytes = 8000) {
  return byteLength < minBytes;
}

export async function isProbablyBlank(url, minBytes = 8000) {
  try {
    const headRes = await fetch(url, { method: "HEAD" });
    const len = headRes.headers.get("content-length");
    if (len !== null) return isBlankBySize(Number(len), minBytes);
    const res = await fetch(url);
    const blob = await res.blob();
    return isBlankBySize(blob.size, minBytes);
  } catch {
    return true;
  }
}
