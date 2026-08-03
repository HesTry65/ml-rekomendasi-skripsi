import { buildRecommendation } from "../../lib/recommend";

export async function onRequestPost({ request }: { request: Request }) {
  const data = await request.json().catch(() => null) as Record<string, unknown> | null;
  const bodyShape = String(data?.body_shape ?? "").trim().toLowerCase();
  const gayaRaw = Array.isArray(data?.gaya) ? data.gaya : [];
  const gaya = (gayaRaw as unknown[]).map((g) => String(g).trim().toLowerCase());

  if (!bodyShape || gaya.length === 0) {
    return Response.json({ error: "Mohon pilih bentuk tubuh dan gaya pakaian" }, { status: 400 });
  }

  try {
    const result = buildRecommendation(bodyShape, gaya);
    return Response.json(result);
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    return Response.json({ error: `Data tidak dikenali: ${message}` }, { status: 422 });
  }
}
