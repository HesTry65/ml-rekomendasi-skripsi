import { NextResponse } from "next/server";
import { buildRecommendation } from "@/lib/recommend";

export async function POST(request: Request) {
  const data = await request.json().catch(() => null);
  const bodyShape = String(data?.body_shape ?? "").trim().toLowerCase();
  const gayaRaw = Array.isArray(data?.gaya) ? data.gaya : [];
  const gaya = gayaRaw.map((g: unknown) => String(g).trim().toLowerCase());

  if (!bodyShape || gaya.length === 0) {
    return NextResponse.json(
      { error: "Mohon pilih bentuk tubuh dan gaya pakaian" },
      { status: 400 }
    );
  }

  try {
    const result = buildRecommendation(bodyShape, gaya);
    return NextResponse.json(result);
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    return NextResponse.json({ error: `Data tidak dikenali: ${message}` }, { status: 422 });
  }
}
