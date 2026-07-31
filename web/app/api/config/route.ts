import { NextResponse } from "next/server";

export async function GET() {
  return NextResponse.json({ hfToken: process.env.NEXT_PUBLIC_HF_TOKEN || null });
}
