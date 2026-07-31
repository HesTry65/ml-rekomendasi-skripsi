import { Client, handle_file } from "https://cdn.jsdelivr.net/npm/@gradio/client/dist/index.min.js";
import { sortByGarmentOrder, isProbablyBlank } from "./tryon-helpers.js";

const HF_SPACE = "yisol/IDM-VTON";
let hfTokenPromise = null;

function getHfToken() {
  if (!hfTokenPromise) {
    hfTokenPromise = fetch("/api/config")
      .then((r) => r.json())
      .then((d) => d.hfToken);
  }
  return hfTokenPromise;
}

export async function generateTryon(photoBase64, garments) {
  if (!photoBase64 || !garments || !garments.length) {
    throw new Error("Foto dan minimal 1 item rekomendasi wajib diisi");
  }

  const sorted = sortByGarmentOrder(garments);
  const token = await getHfToken();
  const client = await Client.connect(HF_SPACE, { token: token || undefined });

  const photoRes = await fetch(photoBase64);
  let currentBlob = await photoRes.blob();
  const applied = [];

  try {
    for (const g of sorted) {
      const garmentUrl = (g.image || "").trim();
      if (!garmentUrl) continue;

      const absoluteUrl = new URL(garmentUrl, window.location.origin).href;
      if (await isProbablyBlank(absoluteUrl)) continue;

      const result = await client.predict("/tryon", {
        dict: { background: handle_file(currentBlob), layers: [], composite: null },
        garm_img: handle_file(absoluteUrl),
        garment_des: g.label || "pakaian",
        is_checked: true,
        is_checked_crop: false,
        denoise_steps: 30,
        seed: 42,
      });

      const outUrl = result.data[0].url;
      const outRes = await fetch(outUrl);
      currentBlob = await outRes.blob();
      applied.push(g.label || "pakaian");
    }
  } catch (err) {
    throw new Error(
      `Gagal generate (Hugging Face Space mungkin sedang sibuk/tidur, coba lagi): ${err.message || err}`
    );
  }

  if (!applied.length) {
    throw new Error("Tidak ada item valid untuk di-generate");
  }

  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = () => reject(reader.error);
    reader.readAsDataURL(currentBlob);
  });
}
