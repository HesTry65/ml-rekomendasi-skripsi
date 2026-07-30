# Fase 2a: Migrasi Backend ke Next.js — Design Spec

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:writing-plans to turn this spec into an implementation plan, then superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to execute it.

**Goal:** Ganti Flask (`app/app.py`) jadi Next.js (App Router, TypeScript), deploy-ready ke Vercel (Hobby/free), tanpa ubah UI lama (masih HTML/JS statis dulu — React rewrite itu Fase 2b, terpisah).

**Architecture:** Next.js App Router jadi host tunggal: `/api/recommend` (route handler) port murni logic C4.5 dari Python ke TypeScript (tree walk + `BODY_GAYA_ITEM` lookup, tanpa sklearn/Python runtime). Try-on (`generateTryon`) pindah 100% ke client — browser panggil `@gradio/client` langsung ke HF Space `yisol/IDM-VTON`, gak lewat server Next.js sama sekali (sidestep limit durasi function Vercel Hobby yang cuma ~10-60 detik). Aset gambar (`app/images/`, dst) pindah ke `public/`. `La Silhouette.dc.html` + `support.js` + `image-slot.js` disajikan static dari `public/` tanpa diubah, cukup ganti endpoint fetch-nya biar nunjuk ke `/api/recommend` (path sama) dan generate-tryon manggil `lib/tryon.ts` langsung.

**Tech Stack:** Next.js 14+ (App Router, TypeScript), `@gradio/client`, Vercel Hobby.

## Global Constraints

- Model C4.5 harus 100% sama perilakunya dengan model sklearn asli (`research/models/model_c45.pkl`) — tree JSON hasil ekstraksi harus divalidasi ulang lawan model asli sebelum dipakai (parity check, seluruh ruang input: 5 body shape × 32 kombinasi gaya = 160 kombo, 0 mismatch).
- Vercel Hobby plan: function duration max ~60s — try-on TIDAK BOLEH lewat server Next.js, wajib client-side.
- `HF_TOKEN` boleh exposed di client (keputusan user, sudah disetujui) — tapi taruh di `NEXT_PUBLIC_HF_TOKEN` biar eksplisit itu env var publik, bukan pura-pura rahasia.
- Gak ada DB/persistence baru — history/riwayat tetap in-memory client state (konfirmasi: gak ada `localStorage` di kode lama).
- UI lama (`La Silhouette.dc.html`, `support.js`, `image-slot.js`) TIDAK diubah strukturnya di fase ini — cuma endpoint URL yang disesuaikan kalau perlu. React rewrite = Fase 2b, spec terpisah.
- Semua behavior yang didokumentasikan di CLAUDE.md project (setelan split-image, blank-crop skip 4 file, `isSingleItem` layout, `?v=2` cache-busting, flat-lay only/no-mannequin) harus tetap jalan sama persis setelah migrasi.

---

## Komponen

### 1. `lib/tree.ts` + `data/tree.json` — Model C4.5 murni TS

- `data/tree.json`: hasil ekstraksi `model.tree_` (sklearn) jadi struktur node `{feature, threshold, left, right}` / leaf `{leaf: className}`. Diregenerasi dari `research/models/model_c45.pkl` via script Python sekali jalan (bukan bagian dari app), lalu di-commit sebagai file statis.
- `lib/tree.ts`: fungsi `predict(input: {body_shape_enc: number, gaya_bohemian: 0|1, ...}): 'atasan'|'bawahan'|'fullbody'|'outer'` — walk tree JSON, replikasi logic `walk()` yang sudah divalidasi (160/160 parity) di sesi brainstorming sebelumnya.
- Wajib: script ekstraksi + script validasi 160-kombo ditulis ke repo (mis. `research/scripts/export_tree.py`) supaya reproducible, bukan cuma dijalanin sekali di venv buangan.

### 2. `lib/recommend-data.ts` — Port `BODY_GAYA_ITEM`

- Port langsung dict Python `BODY_GAYA_ITEM` (5 body shape × 5 gaya × up to 4 kategori) jadi objek TS bertipe sama persis. Tidak ada logic tambahan, murni transkripsi data.

### 3. `app/api/recommend/route.ts` — Route handler

- Terima POST body sama seperti Flask `/recommend` (body shape + array gaya terpilih).
- Encode input (body_shape → enc via mapping tetap `['apple','hourglass','inverted','pear','rectangle']`; gaya → binary flags sama urutan `mlb.classes_`).
- Panggil `predict()` dari `lib/tree.ts` → dapat label kategori utama.
- Terapkan logic pelengkap yang sudah ada di CLAUDE.md (bukan logic baru — port apa adanya):
  - `fullbody` → cuma `fullbody`.
  - `atasan` → `atasan` + `bawahan`.
  - `bawahan` → `bawahan` + `atasan`.
  - `outer` → `outer` + `atasan` + `bawahan`.
- Lookup item suggestion per kategori dari `lib/recommend-data.ts`.
- Return JSON, struktur sama persis dengan respons Flask lama (biar `support.js`/HTML lama gak perlu ubah parsing).

### 4. `lib/tryon.ts` — Try-on client-side module

- Fungsi `generateTryon(photoBase64: string, garments: {image, label, category}[]): Promise<string>` — jalan di browser.
- Pakai `@gradio/client`, `Client.connect('yisol/IDM-VTON', {hf_token: process.env.NEXT_PUBLIC_HF_TOKEN})`, panggil endpoint `/tryon`.
- Replikasi logic existing apa adanya:
  - Urutan prioritas `GARMENT_ORDER` (`fullbody:0, atasan:1, bawahan:2, outer:3`), ambil maksimal 2 layer (sesuai batasan yang sudah ada, bukan 3-chain).
  - Setelan-split: kalau kategori `fullbody` dan nama file mengandung "setelan", pecah jadi `_top.png` (atasan) + `_bottom.png` (bawahan) alih-alih kirim 1 foto gabungan.
  - Skip file blank: cek ukuran file < 8000 bytes → skip (`_is_probably_blank` equivalent). 4 file yang udah diketahui rusak (`setelan_atasan_berdetail_bottom.png`, `setelan_blazer_panjang_bottom.png`, `setelan_ikat_pinggang_top.png`, `setelan_rok_flared_top.png`) otomatis ke-skip lewat cek ini.
- Gambar garment diambil dari `public/images/...` (path client-accessible, bukan lagi baca file server-side).
- Error handling: request ke HF Space bisa timeout/gagal (cold start, ZeroGPU quota habis) — tangkap error, propagate pesan yang jelas ke UI (`tryonError` state di HTML lama sudah ada slot buat ini).

### 5. Aset statis

- Pindah `app/images/`, `app/screenshots/`, shape/hero PNG ke `public/` (struktur folder dipertahankan sama, cuma root-nya pindah).
- `app/uploads/` — folder ini nampung upload user runtime di Flask (server-side temp storage). Di arsitektur baru, upload foto try-on diproses di browser (FileReader → base64, langsung ke `@gradio/client`), jadi `uploads/` **tidak diperlukan lagi** — tidak diporting.
- `La Silhouette.dc.html`, `support.js`, `image-slot.js` pindah ke `public/` apa adanya, disajikan sebagai halaman statis (bisa lewat route `app/page.tsx` yang redirect/serve, atau taruh langsung di `public/index.html` — detail teknis diputuskan saat implementation plan).

## Data Flow

1. User isi form body shape + gaya di UI lama → JS lama `fetch('/recommend', {method:'POST', body: {...}})`.
2. Next.js route `app/api/recommend/route.ts` proses: decode input → `predict()` via tree.ts → lookup item via recommend-data.ts → return JSON sama struktur kayak sebelumnya.
3. UI lama render hasil (kode render gak berubah, cuma response asal beda origin — sama-sama same-origin Next.js).
4. User klik "Coba Pakai Fotomu (AI)" → upload foto → JS lama panggil (yang tadinya `fetch('/generate-tryon')`) sekarang panggil `generateTryon()` dari `lib/tryon.ts` langsung di browser → `@gradio/client` → HF Space → hasil base64/URL image → render di UI.
5. Gak ada roundtrip ke server Next.js buat try-on sama sekali — server cuma serve static assets + `/api/recommend`.

## Error Handling

- `/api/recommend`: input tervalidasi minimal (body shape harus salah satu dari 5 enum, gaya array boleh kosong) — kalau invalid, return 400 dengan pesan jelas. Tidak perlu validasi berlapis (YAGNI) karena UI lama sudah cuma kirim value dari dropdown/checkbox terkontrol.
- `lib/tryon.ts`: try/catch di sekeliling panggilan `@gradio/client` — network error, timeout, ZeroGPU quota exceeded semua ditangkap dan dilempar sebagai `Error` dengan pesan yang bisa langsung ditampilkan ke `tryonError` state (UI lama sudah punya slot ini, gak perlu desain baru).
- Blank-crop file di-skip diam-diam (bukan error) — sama seperti behavior lama, karena itu memang by design (file rusak dilewatin, bukan bikin generate gagal total).

## Testing / Verification

- **Tree parity:** script ekstraksi + validasi 160-kombo (sudah divalidasi manual di sesi brainstorming) jadi bagian dari implementation plan — dijalankan ulang dan hasilnya (0 mismatch) jadi bukti commit sebelum tree.json dipakai di route handler.
- **`/api/recommend`:** test dengan beberapa kombinasi input (minimal cover 4 kelas output: atasan/bawahan/fullbody/outer) dan bandingkan responsnya sama respons Flask lama (`app/app.py` bisa dijalanin paralel buat cross-check manual selama development, tapi Flask app itu sendiri gak ikut di-porting/dipertahankan setelah migrasi selesai).
- **`lib/tryon.ts`:** karena manggil service eksternal (HF Space, ada cold start + quota kuota harian), testing otomatis penuh gak realistis (YAGNI — gak bikin mock HF Space). Verifikasi manual: minimal 1 kali generate try-on end-to-end di browser real, termasuk 1 kasus "setelan" (verifikasi split top/bottom jalan) dan pastikan 4 file blank yang diketahui rusak ke-skip tanpa crash.
- **UI lama tetap jalan:** buka halaman di browser, jalanin golden path (pilih body shape → gaya → lihat rekomendasi → coba try-on) sebelum nyatain 2a selesai — sesuai aturan project (test UI manual di browser, bukan cuma type-check).

---

## Yang TIDAK termasuk di scope 2a (sengaja, YAGNI)

- React rewrite UI — itu Fase 2b, spec terpisah.
- `app/uploads/` — gak diporting, gak relevan lagi di arsitektur client-side upload.
- Supabase — `app/.env` punya `SUPABASE_URL`/`SUPABASE_KEY` tapi itu cuma dipakai `research/notebook/recomendation.ipynb` (bukan runtime app), gak ikut diporting.
- CI/testing framework baru — pakai apa yang paling ringan cukup (manual verification + 1 script validasi tree), gak instalasi Jest/Vitest kalau gak ada kebutuhan nyata lain.
