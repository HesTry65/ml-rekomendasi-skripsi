export async function onRequestGet({ env }: { env: { HF_TOKEN?: string } }) {
  return Response.json({ hfToken: env.HF_TOKEN || null });
}
