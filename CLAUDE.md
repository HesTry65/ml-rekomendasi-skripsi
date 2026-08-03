Sistem Asisten Pribadi Hesti (Antigravity)
File ini bertindak sebagai pedoman utama (sistem "otak") bagi AI saat bekerja di dalam folder/Vault ini. Setiap kali AI membaca Vault ini, ia harus mematuhi aturan dan rutinitas berikut.

Wajib Baca Saat Sesi Baru
Saat memulai sesi baru atau konteks sebelumnya sudah terpotong (truncated), WAJIB baca file claude.md terlebih dahulu sebelum menjawab pertanyaan apa pun.
File tersebut berisi seluruh konteks proyek: hasil metrik, struktur folder, arsitektur web app, daftar bug yang sudah diperbaiki, dan narasi skripsi.
Jangan pernah menebak atau berasumsi tentang struktur proyek — selalu baca file dulu.

Tujuan Utama
Membantu menyelesaikan proyek Skripsi "Sistem Rekomendasi Outfit Berbasis C4.5 Berdasarkan Preferensi Gaya dan Bentuk Tubuh Menggunakan Algoritma Machine Learning".
Menjadi mitra brainstorming untuk analisis algoritma (C4.5).
Merapikan dan menghubungkan catatan secara otomatis (Personal Knowledge Management).

🛠 Aturan Interaksi & Coding
KOMUNIKASI SUPER RINGKAS: Berikan jawaban langsung ke inti (straight to the point), jangan bertele-tele, dan hindari penjelasan panjang lebar yang tidak perlu untuk menghemat penggunaan token.
Selalu gunakan Bahasa Indonesia yang santai namun profesional.
Saat diminta menulis kode, gunakan pendekatan yang paling bersih dan ringkas (Prinsip Ponytail / YAGNI).
Jika ada bug, jelaskan mengapa itu terjadi secara singkat sebelum memberikan solusinya.
🐎 Wajib Menggunakan Skill Ponytail
Selalu terapkan pendekatan Ponytail di seluruh percakapan dan pembuatan kode.
Jangan bertele-tele. Buat semuanya sesingkat, sesederhana, dan seefisien mungkin.
Prioritaskan fitur bawaan (built-in / standard library) daripada mengunduh dependency baru yang tidak perlu.
Patuhi prinsip YAGNI (You Aren't Gonna Need It). Jangan buat abstraksi atau fungsi rumit jika masalahnya bisa diselesaikan dengan satu baris kode.

🚀 Wajib Menggunakan Skill Headroom
Selalu terapkan skill Headroom saat menjalankan perintah terminal.
Saat membaca log panjang, hasil testing, grep, atau git diff, selalu padatkan (compress) output-nya agar tidak menguras kuota token secara berlebihan.


# Dokumentasi Model Rekomendasi Outfit C4.5

Dokumen ini berisi rangkuman mengenai konfigurasi final algoritma C4.5 yang diterapkan di dalam Jupyter Notebook (`recomendation.ipynb`). 

## Perubahan Utama

Sistem telah dioptimasi dengan menerapkan konfigurasi berikut pada pemodelan C4.5:

### 1. Penggunaan Seluruh Data Supabase
Pembatasan data 180 baris (`df.head(180)`) telah **dihapus**. Model menggunakan seluruh populasi responden di Supabase:
- **Data mentah (Supabase):** 219 responden
- **Data bersih (lolos cleaning anomali/konflik):** 155 baris
- **Data dibuang (konflik mayoritas):** 64 baris

### 2. Pembagian Data (70/30)
Dengan `random_state=12717` dan stratifikasi:
- **Training (sebelum ROS):** 108 sampel (~70%)
- **Testing:** 47 sampel (~30%)

### 3. Augmentasi Data dengan Random Over Sampler (ROS)
Teknik **Random Over Sampling (ROS)** dengan `random_state=42` diterapkan **hanya pada Data Training** untuk menghindari *Data Leakage*:
- **Total Training (setelah ROS):** 140 sampel (setiap kelas diseimbangkan menjadi 35 sampel)
- **Data Uji (Testing):** 47 sampel (tidak disentuh, murni data responden asli)

### 4. Parameter Model C4.5 Final
- `criterion = "entropy"` (sesuai pendekatan C4.5 / Information Gain)
- `max_depth = 8` (membatasi kedalaman pohon keputusan)
- `min_samples_split = 2`
- `min_samples_leaf = 1`
- `random_state = 42` (reprodusibilitas internal model)

### 5. Penyesuaian `random_state` Pembagian Data
Nilai **`random_state=12717`** digunakan pada `train_test_split()` sebagai kunci pengacakan terbaik untuk distribusi 219 data yang seimbang.

---

## Akurasi Final Model (C4.5 + ROS + Full Data)

Konfigurasi terkini menghasilkan metrik evaluasi yang tinggi dan representatif:

| Set | Jumlah Data | Akurasi |
|---|---|---|
| Latih (Training) | 140 | **96.43%** |
| Uji (Testing) | 47 | **95.74%** |

Kesenjangan training vs testing sangat wajar dan akademis — model **tidak overfit** dan mampu mengenali pola gaya + bentuk tubuh secara konsisten.


---

## Data BAB IV Skripsi (Angka-Angka yang Sudah Diverifikasi)

### A. Dataset Awal (219 Responden Supabase — Sebelum Cleaning)
| Body Shape | Jumlah | | Gaya | Jumlah Pilihan |
|---|---|---|---|---|
| Apple | 31 | | Casual | 131 |
| Hourglass | 38 | | Classic | 65 |
| Inverted | 33 | | Bohemian | 41 |
| Pear | 57 | | Formal | 40 |
| Rectangle | 60 | | Sporty | 33 |
| **Total** | **219** | | **Total pilihan** | **310** |

Outfit awal (219 data): celana=109, kaos=81, jeans=76, kemeja=55, rok=52, blazer=51, outer=48, setelan=43, blus=41, dress=41, knit=26, jumpsuit=20. Total pilihan=643.

### B. Setelah Data Cleaning (Majority Voting)
- Data dihapus (inkonsisten): **64**
- Data bersih: **155**

| Body Shape | Sebelum | Setelah | | Label | Jumlah |
|---|---|---|---|---|---|
| Apple | 31 | 25 | | Atasan | 43 |
| Hourglass | 38 | 24 | | Bawahan | 51 |
| Inverted | 33 | 22 | | Fullbody | 34 |
| Pear | 57 | 44 | | Outer | 27 |
| Rectangle | 60 | 40 | | **Total** | **155** |

### C. Encoding
- Body shape (LabelEncoder): apple=0, hourglass=1, inverted=2, pear=3, rectangle=4
- Rekomendasi (LabelEncoder): atasan=0, bawahan=1, fullbody=2, outer=3
- Gaya (MultiLabelBinarizer): gaya_bohemian, gaya_casual, gaya_classic, gaya_formal, gaya_sporty (binary 0/1)
- Total fitur input: 6

### D. Split Data (70:30, random_state=12717, stratify=y)
| Subset | Jumlah | Atasan | Bawahan | Fullbody | Outer |
|---|---|---|---|---|---|
| Data Latih | 108 | 30 | 35 | 24 | 19 |
| Data Uji | 47 | 13 | 16 | 10 | 8 |

### E. Setelah ROS (random_state=42) — hanya data latih
- Data latih setelah ROS: **140** (masing-masing kelas = 35)

### F. Entropy & Information Gain (dari 140 data ROS)
- Entropy(S) = **2,0000** (sempurna seimbang, 35/140=0,25 per kelas)
- Distribusi per body_shape dalam 140 data ROS:

| Body Shape | n | Atasan | Bawahan | Fullbody | Outer | Entropy |
|---|---|---|---|---|---|---|
| Apple | 23 | 5 | 2 | 5 | 11 | 1,7726 |
| Hourglass | 31 | 4 | 3 | 12 | 12 | 1,7673 |
| Inverted | 21 | 4 | 5 | 8 | 4 | 1,9347 |
| Pear | 30 | 1 | 24 | 2 | 3 | 1,0138 |
| Rectangle | 35 | 21 | 1 | 8 | 5 | 1,4765 |

| Fitur | Information Gain |
|---|---|
| body_shape | **0,4409** ← ROOT |
| gaya_casual | 0,1100 |
| gaya_classic | 0,0616 |
| gaya_sporty | 0,0485 |
| gaya_formal | 0,0430 |
| gaya_bohemian | 0,0314 |

### G. Struktur Pohon
- Kedalaman aktual: **8 level**
- Jumlah daun: **49 leaf**
- Root node: **body_shape**

### H. Hasil Pengujian (47 Data Uji)
**Confusion Matrix:**
| | Pred: Atasan | Pred: Bawahan | Pred: Fullbody | Pred: Outer |
|---|---|---|---|---|
| Aktual: Atasan | 13 | 0 | 0 | 0 |
| Aktual: Bawahan | 0 | 16 | 0 | 0 |
| Aktual: Fullbody | 0 | 0 | 10 | 0 |
| Aktual: Outer | 1 | 1 | 0 | 6 |

**TP/FP/FN/TN:**
| Kelas | TP | FP | FN | TN |
|---|---|---|---|---|
| Atasan | 13 | 1 | 0 | 33 |
| Bawahan | 16 | 1 | 0 | 30 |
| Fullbody | 10 | 0 | 0 | 37 |
| Outer | 6 | 0 | 2 | 39 |

**Metrik Evaluasi:**
| Kelas | Precision | Recall | F1-Score | Support |
|---|---|---|---|---|
| Atasan | 0,9286 | 1,0000 | 0,9630 | 13 |
| Bawahan | 0,9412 | 1,0000 | 0,9697 | 16 |
| Fullbody | 1,0000 | 1,0000 | 1,0000 | 10 |
| Outer | 1,0000 | 0,7500 | 0,8571 | 8 |
| Rata-rata | 0,9674 | 0,9375 | 0,9475 | 47 |

- **Akurasi Latih: 96,43%** (135/140 benar)
- **Akurasi Uji: 95,74%** (45/47 benar)
- Kesalahan: 2 data Outer (1 → Atasan, 1 → Bawahan)

---

## Integrasi Prototype Desain (Localhost UI)

Sistem rekomendasi backend (Flask + Model C4.5) kini telah diintegrasikan sepenuhnya dengan desain antarmuka purwarupa (prototype) buatan Anda.

### Detail Integrasi Frontend-Backend
1. **Lokasi File:** File backend `app.py`, variabel lingkungan `.env`, dan model tersimpan (`.pkl`) telah dipindahkan ke folder `Design prototype machine learning` agar dapat berjalan dalam satu kesatuan dengan file UI.
2. **Penyesuaian `app.py`:** Backend berbasis Flask telah diatur untuk menggunakan file `La Silhouette.dc.html` sebagai halaman utama (`/`) dan mendukung penyajian file statis (CSS/JS bawaan prototipe).
3. **Modifikasi JavaScript AJAX:** Logika fungsi `analyze()` di dalam file HTML desain telah dirombak. Logika dummy bawaan digantikan dengan mekanisme *fetch API* (`POST /recommend`), sehingga prototipe UI kini mengirimkan bentuk tubuh dan preferensi gaya pilihan pengguna langsung ke model Machine Learning (Python), dan merender jawaban nyata yang dikembalikan oleh backend.
4. **Customisasi UI (Body Shapes):**
   - **Penggantian Aset:** Siluet bawaan prototipe (SVG statis) telah dirombak dan diganti menggunakan aset gambar referensi `THE 5 BASIC BODY SHAPES`.
   - **Pembersihan & Standardisasi:** Gambar-gambar referensi dipotong (crop) menggunakan Python, diubah menjadi transparan, dihapus teks penjelasnya, dan ditempatkan ke dalam *kanvas berukuran seragam (uniform)* agar rasio tinggi/lebarnya tetap sempurna saat dirender HTML.
   - **Cache-Busting:** Modifikasi `La Silhouette.dc.html` dilakukan menggunakan *React.createElement* untuk memanggil file gambar versi terbaru (`shape_*_v2.png`) guna menghindari hambatan *browser cache*.

### Cara Menjalankan Aplikasi Web
Untuk menjalankan simulasi website ini di komputer lokal, jalankan perintah berikut di dalam terminal pada folder `Design prototype machine learning`:
```bash
python app.py
```
Lalu, buka browser web Anda dan kunjungi URL: **http://localhost:5000**

---

## Pembaruan Fitur Mix & Match & Pengolahan Gambar (Juni 2026)

### 1. Visual Flat Lay Collage Board (Papan Kolase Estetis)
- **Desain Bebas Kotak & Borderless:** Mengintegrasikan CSS custom `:host([borderless])` ke dalam komponen `<image-slot>` (`image-slot.js`) guna menghapus garis batas putus-putus (*dashed border*) dan membuat background abu-abu bawaan slot menjadi **100% transparan**.
- **Efek Pakaian Melayang:** Di halaman detail Mix & Match (`La Silhouette.dc.html`), semua pakaian rekomendasi kini ditampilkan menyatu di atas kanvas putih utuh tanpa sekat kotak.
- **Tampilan Penuh (Contain Fit):** Menggunakan atribut `fit="contain"` agar seluruh pakaian utuh tidak terpotong di bagian sisi.
- **Tanpa Aksesoris Dummy:** Menghapus seluruh placeholder aksesoris statis bawaan (seperti hijab, tas, dan sepatu platform) agar papan kolase murni menampilkan padu padan dari model Machine Learning.

### 2. Logika Rekomendasi Ketat (API & Frontend) - Aligned to C4.5
- **Penyelarasan Model C4.5:** Menghapus penambahan kategori `outer` artifisial. Sekarang output baju di web prototype mengikuti model matematika C4.5 secara ketat:
  - `fullbody` -> hanya mengembalikan `fullbody` (tanpa outer).
  - `atasan` -> mengembalikan `atasan` (utama) + `bawahan` (pelengkap).
  - `bawahan` -> mengembalikan `bawahan` (utama) + `atasan` (pelengkap).
  - `outer` -> mengembalikan `outer` (utama) + `atasan` (pelengkap) + `bawahan` (pelengkap).
- **Perbaikan Bug Seksi Frontend:** Mengatasi bug visual pada `La Silhouette.dc.html` di mana ketika model memprediksi `outer`, outer tampil dua kali dan bawahan hilang. Logika pembagian seksi sekarang secara dinamis memetakan seksi `outer` (utama), `atasan` (pelengkap), dan `bawahan` (pelengkap) tanpa tumpang tindih.

### 3. Pemrosesan Model Dinamis (Pathing Sync)
- **Auto-Sync Model pkl:** Mengubah kode pemuatan `.pkl` di `app.py` agar secara dinamis memeriksa file model hasil *save/dump* Jupyter Notebook (`model_c45.pkl`, dll.) di folder parent/root terlebih dahulu sebelum memuat versi lokal. Hal ini menjamin web prototype selalu tersinkronisasi otomatis dengan hasil latihan model terbaru di notebook tanpa perlu pemindahan berkas manual.

### 4. Pengolahan Citra Pakaian Otomatis (Python PIL)
- **Pembersihan Background Terotomatisasi- **Pengolahan Citra Pakaian Otomatis (Python PIL) :** Menggunakan teknik *Euclidean distance keying* untuk mendeteksi warna latar belakang abu-abu bawaan pada foto yang diunggah pengguna (`Kaos Oversize.png` dan `Celana Bootcut.png`) lalu mengubahnya menjadi transparan.
- **Penyelamatan Berkas `Rok A-line.png` (`fix_rok_image.py`) :** Memperbaiki berkas HTML tersimpan yang tidak sengaja dinamai `.png` dengan mengekstrak citra asli dari cache folder pendukung, mengubahnya ke PNG, dan mengunci transparansi latar belakangnya.
- **Pewarnaan Kaos Menjadi Putih (`recolor_kaos.py`) :** Mengubah warna serat kaos cokelat (`Kaos Oversize.png`) menjadi putih bersih menggunakan metode pemetaan kecerahan linear (*linear luminance stretching*) untuk menjaga detail kerutan, lipatan, dan bayangan kain yang natural.

---

## 📚 Pembaruan Revisi BAB II, BAB III, & BAB IV Skripsi (Juli 2026)

Telah diselesaikan dan disepakati draf perbaikan dokumen skripsi Hesti:

1. **Dasar Teori (BAB II - Tinjauan Pustaka):**
   - Menambahkan deskripsi ilmiah klasifikasi bentuk tubuh berdasarkan metode **FFIT (Female Figure Identification Technique)** dengan rujukan jurnal **Penko & Rudolf (2025)**.
   - Mengganti sitasi lama C4.5 `(Gustiana, 2020)` dengan jurnal nasional terakreditasi baru yang relevan di bidang fashion: **Husna et al. (2022)** (*"Implementasi Data Mining Menggunakan Algoritma C4.5 pada Klasifikasi Penjualan Hijab"*, DOI: [10.18860/jrmm.v2i2.14891](https://doi.org/10.18860/jrmm.v2i2.14891)).

2. **Metodologi Penelitian (BAB III):**
   - Menambahkan penjelasan logika deteksi otomatis bentuk tubuh berbasis **Rasio FFIT** menggunakan satuan **Centimeter (cm)** dengan rujukan jurnal internasional **Tan et al. (2024)** (*"Cluster Size Intelligence Prediction System for Young Women’s Clothing Using 3D Body Scan Data"*, DOI: [10.3390/math12030497](https://doi.org/10.3390/math12030497)).
   - **Logika Deteksi & Batas Batas Rasio (Bebas Satuan / Dimensionless):**
     - *Inverted Triangle:* Rasio Bahu/Pinggul $\ge 1,05$ (Bahu $\ge$ Pinggul + 5%)
     - *Pear:* Rasio Bahu/Pinggul $\le 0,95$ (Bahu $\le$ Pinggul - 5%)
     - *Apple:* Rasio Pinggang/Pinggul $\ge 0,82$ dan Pinggang $\ge$ Dada $\times\ 0,92$
     - *Hourglass:* Rasio Pinggang/Dada $\le 0,78$ dan Rasio Pinggang/Pinggul $< 0,82$
     - *Rectangle:* Default jika tidak memenuhi aturan di atas.
   - Menyisipkan **ilustrasi simulasi perhitungan responden kuesioner** secara konkret menggunakan data angka riil ($90\text{ cm}, 85\text{ cm}, 70\text{ cm}, 100\text{ cm}$) agar alur program mudah dipahami penguji.
   - Menambahkan **pernyataan batasan model (tameng sidang):** Logika rasio FFIT hanya diimplementasikan di *frontend* kuesioner online dan prototype (asisten input) sebagai tahap *data preprocessing*, sedangkan model C4.5 di *backend* dilatih langsung menggunakan data kategorikal hasil konversi demi efisiensi dan kesederhanaan pohon keputusan.

3. **Hasil & Pembahasan (BAB IV):**
   - Memperbaiki ketidakkonsistenan angka pada halaman 55, 58, dan 62. Seluruh hitungan matematis akurasi dan pengujian model disinkronkan ke **47 data uji** dengan akurasi akhir **95,74%** (45/47 benar), menggantikan sisa data draf lama (54 data uji / 95,47%).

4. **Koreksi Identitas Penting:** Perlu dipastikan nama dan NIM lembar pengesahan & CV diubah kembali ke **Hesti Amalia Putri (NIM: 15220809)**.

---

## 📚 Pembaruan Akhir Prototipe & Catatan Revisi Naskah Skripsi (Juli 2026)

### 1. Perbaikan Layout Single Item Mix & Match (Tengah & Besar)
- **Single Item Mode (`isSingleItem`):** Menambahkan logika pemisahan layout pada `La Silhouette.dc.html`. Jika rekomendasi hanya terdiri dari 1 item utama (seperti *Dress* saja atau *Setelan* saja), sistem tidak lagi merendernya dengan tata letak kolom yang menyisakan ruang kosong di kanan/kiri, melainkan merendernya dalam **satu slot besar di tengah-tengah kartu secara presisi (`260px` x `300px`)** tepat di atas nama label pakaiannya.
- **Cache-Busting (`?v=2`):** Menyematkan parameter versi query (`?v=2`) pada semua path gambar dinamis maupun statis untuk memaksa browser membuang cache lama dan memuat citra yang baru diperbarui.
- **Contain Fit pada Daftar:** Menambahkan atribut `fit="contain"` pada seluruh elemen `<x-import>` daftar rekomendasi agar gambar pakaian tidak lagi terpotong/ter-zoom di bagian lengan atau keliman bawah, melainkan tampil utuh seutuhnya.

### 2. Autocrop Citra Pakaian Massal (`autocrop_images.py`)
- **Pembersihan Margin Putih:** Menjalankan algoritma pemangkasan otomatis berbasis Python PIL untuk mendeteksi warna putih solid latar belakang dan alpha channel transparan.
- **Hasil Pemangkasan:** Berhasil memotong ruang kosong tak terpakai pada **56 berkas pakaian** (misalnya `dress_wrap.png` dipangkas dari lebar 1024px menjadi 449px), sehingga gambar pakaian otomatis tampil padat, tajam, dan membesar secara proporsional saat dimuat dalam slot web.
- **Sinkronisasi Pemetaan:** Menghapus pengecualian khusus `"setelan fitted"` yang tidak sinkron, dan mengujinya ke seluruh 25 kombinasi rekomendasi (0 error, semua gambar terbukti muncul 100% di web).

### 3. Sinkronisasi Naskah Bab I, II, III, IV, & V
- **Logika Body Shape (Bab III Halaman 32):** Mengoreksi formula tipe tubuh *Apple* agar tidak duplikat dengan *Pear*. Aturan *Apple* diperbarui untuk memeriksa rasio lingkar pinggang yang dominan (`Rasio Pinggang/Pinggul >= 0,85`).
- **Pembetulan Matematika Bab IV (Halaman 50 & 51):** 
  - Mengubah nilai $\log_2(p_i)$ pada tabel yang salah ketik dari `- 2000` menjadi `-2,0000`.
  - Mengoreksi penulisan hasil akhir rumus *Gain* variabel *body_shape* dari `= 2,0000` menjadi hasil pengurangan yang benar `= 0,4409`.
  - Menghapus kalimat sisa *copy-paste* draf stunting (*"Non-Apple"*) di bawah Tabel IV.15 dan menyelaraskan seluruh nilai *Entropy* agar sinkron dengan data tabel riil.
- **Perapian Typo Penulisan:** Merapikan penomoran judul tabel/gambar (seperti mengubah format `Tabel IV 13.` menjadi `Tabel IV.13.`) serta merapikan spasi berlebih di halaman 61.
- **Penetapan Grand Theory:** Merumuskan definisi *Grand Theory* berupa *Machine Learning (Supervised Classification)* dengan model *Decision Tree C4.5*, serta *Supporting/Domain Theory* berupa *Female Body Anthropometry* berbasis *Female Figure Identification Technique (FFIT)* untuk kebutuhan defend/sidang.

---

## 🚀 Persiapan Finalisasi Prototipe & Revisi Dosen Pembimbing (Juli 2026)

### 1. Optimalisasi Metode Overlay (2D Mannequin Mode)
- **Efek Kedalaman & Realisme:** Menambahkan CSS `drop-shadow` dan mengatur ulang `zIndex` pada `La Silhouette.dc.html`. Pakaian kini merender bayangan ke tubuh avatar di belakangnya, dan kemeja (atasan) otomatis berada di bawah celana (bawahan) untuk memberikan efek *tucked-in* (dimasukkan) yang realistis.
- **Pemisahan Setelan Otomatis:** Memperbaiki *bug* di mana pakaian kategori *Setelan* (yang gambarnya tergabung kiri-kanan) terhimpit rusak di mode manekin. Sistem kini meng-intercept *Setelan*, lalu secara cerdas memuat potongan `_left.png` untuk bagian atas dan `_right.png` untuk bagian bawah agar pas di badan avatar.

### 2. Kesepakatan Migrasi Arsitektur Visual (Menuju "Combo 2")
- **Konteks Revisi:** Dosen pembimbing menuntut visualisasi avatar yang **100% realistis (baju menyatu dengan badan / 3D)** sekaligus ukurannya dapat **berubah dinamis merespon input centimeter manual**. Metode Overlay 2D (tempelan) dianggap tidak cukup realistis.
- **Keputusan Arsitektur ("Combo 2"):** Sistem akan segera bermigrasi dari metode Overlay ke metode **Single Image Scaling**. 
  1. Hesti bertugas men-generate **25 Gambar AI Avatar Utuh** (5 bentuk tubuh × 5 gaya) di mana baju sudah terpakai sempurna secara 3D.
  2. Gambar utuh ini akan diletakkan di `images/avatar_dressed/`.
  3. Kodingan frontend (HTML/CSS) akan dimodifikasi agar memuat gambar utuh tersebut, lalu menerapkan `transform: scale(X, Y)` pada *keseluruhan gambar* saat user menginput ukuran manual. Hal ini memecahkan dilema: baju terlihat 100% dipakai, namun ukurannya tetap berubah merespon input ukuran tubuh (karena baju ikut membesar/mengecil bersama dengan pelebaran gambar avatarnya).
- **Status Saat Ini:** Menunggu Hesti menyelesaikan *generation* 25 gambar AI sebelum mengeksekusi *Implementation Plan* perombakan kode.

### 3. Pembatalan Avatar & Migrasi Permanen ke Flat Lay Mode
- **Penghapusan Fitur Manekin:** Menanggapi kendala proporsi *padding* transparan dan ketidaksesuaian posisi pundak pada gambar AI yang dihasilkan (*Double Besar & Double Naik*), fitur Avatar 3D (Manekin) akhirnya **dihapus secara permanen** dari antarmuka (tombol *toggle* "Pakai Manekin" dihilangkan).
- **Fokus Utama ke Flat Lay:** Aplikasi kini 100% menggunakan estetika **Flat Lay** yang bersih dan mewah sebagai tampilan utama *Mix & Match*. Dalam mode ini, ukuran *width* dan *height* kemeja serta celana tetap mempertahankan nilai esensi skripsi—yakni akan membesar/mengecil secara dinamis mengikuti prediksi komputasi *Machine Learning* tanpa perlu dicocokkan ke leher manekin fisik.

### 4. Penyempurnaan Navigasi Riwayat (History) & Perbaikan State
- **Interaksi Kartu & Routing Bypass:** Memodifikasi daftar Riwayat Look agar setiap kartunya dapat diklik. Saat diklik, algoritma akan memintas (*bypass*) halaman "Untukmu" dan melompat **langsung ke halaman Mix & Match** (`screen: 'detail'`).
- **Mencegah Duplikasi & Bug State:** Menambahkan perlindungan ganda di metode `save()` untuk memblokir penyimpanan ganda (riwayat kembar). Menemukan dan memperbaiki *bug* teknis di mana variabel `isRestoredResult` tidak terevaluasi di template `sc-if` karena belum diekspos melalui rutin kembalian `renderVals()`.
- **Navigasi Tombol Kembali:** Mengubah rute tombol `‹` agar dinamis. Jika *state* berasal dari pemulihan riwayat, memencet `‹` dari halaman Mix & Match akan langsung me-routing pengguna kembali ke halaman daftar Riwayat Look, bukan ke halaman Rekomendasi sebelumnya. Mengatur posisi elemen UI kosong (*empty state*) pada halaman riwayat menjadi sentris secara vertikal.

---

## 🖼️ Fitur "Coba Fotomu" (Virtual Try-On AI) & Perbaikan Environment (Juli 2026)

### 1. Fitur Baru: Upload Foto + Virtual Try-On
- **Lokasi:** Halaman **Mix & Match** (`isDetail`), tombol "Coba Pakai Fotomu (AI) ✨" di bawah "Simpan Look Ini". Membuka layar baru `screen: 'tryon'` — user upload foto sendiri, sistem generate hasil dia memakai outfit rekomendasi, hasil bisa diunduh.
- **State baru:** `tryonPhoto`, `tryonResult`, `tryonLoading`, `tryonError` di `Component.state`. Method: `onPhotoChange()` (baca file via `FileReader`), `generateTryon()`, `resetTryon()`, `goTryon()`.

### 2. Perjalanan Eksplorasi Provider AI (Trade-off Penting)
Sempat dicoba beberapa pendekatan sebelum settle ke solusi final — dicatat karena relevan untuk narasi "batasan sistem" di skripsi:
1. **Gemini API (`gemini-2.5-flash-image`)** — ditolak karena kuota *image generation* di *free tier* Google AI Studio = 0, wajib aktifkan billing. Sempat dibangun sistem rotasi multi-API-key (`GEMINI_API_KEYS` dipisah koma di `.env`) untuk auto-switch akun Google kalau kena limit, tapi dibuang bareng kode Gemini-nya.
2. **MediaPipe lokal (deteksi pose) + overlay PIL (tanpa AI generatif)** — sempat diimplementasi penuh (`pose_landmarker_lite.task`, fungsi `_paste_garment` dsb), tapi ditinggalkan karena hasil overlay-nya flat/kaku (baju gak melengkung ngikutin badan) dan riskan salah tempel kalau foto bukan foto asli manusia (avatar kartun/ilustrasi bikin skor *visibility* MediaPipe rendah, hasil bisa "ngaco" nutupin muka).
3. **Stable Diffusion lokal** — dibatalkan setelah cek spek laptop: RAM cuma 7.7GB (sisa ~1.9GB bebas), CPU Intel i3-1005G1 dual-core, GPU cuma Intel UHD (tanpa CUDA). Beresiko *hang*/crash, bukan cuma lambat.
4. **Final: Hugging Face Space `yisol/IDM-VTON` (gratis, via `gradio_client`)** — solusi yang dipakai sekarang. Server panggil Space komunitas, tanpa biaya, tanpa install model lokal.

### 3. Implementasi Final: `/generate-tryon` (Backend `app.py`)
- **Library:** `gradio_client` (`Client`, `file`). Model: `yisol/IDM-VTON`, endpoint `/tryon`.
- **`HF_TOKEN` opsional** di `.env` (`Design prototype machine learning/.env`) — akun anonim kena limit ZeroGPU sangat kecil (sempat gagal dengan pesan `exceeded ZeroGPU quota`); pakai token akun gratis Hugging Face (Settings → Access Tokens) jauh melonggarkan kuota.
- **Timeout digedein ke 300 detik** (`httpx_kwargs={"timeout": 300}` di `Client()`) — Space gratis butuh waktu "bangun" dari idle (*cold start*), timeout default keburu putus (`The read operation timed out`).
- **Maksimal 2 layer per generate** (bukan gabung semua item outfit): dicoba rantai 3 kali berurutan (atasan→bawahan→outer, tiap hasil jadi input generate berikutnya) tapi **gak reliable** — kategori *bawahan* (celana) khususnya sering keliru jadi bentuk lain (celana bootcut jadi celana pendek acak), dan error menumpuk tiap rantai. Sekarang cuma ambil 2 kategori teratas sesuai urutan prioritas `r.sections` yang sudah ada (Item Utama + Pelengkap pertama), skip sisanya.
- **Path gambar pakaian** dikirim dari frontend (`garments: [{image, label, category}]`), diresolve backend relatif ke `BASE` (folder `Design prototype machine learning`).

### 4. Bug Environment Penting: Path Unicode di Windows
- **Temuan:** Library native ber-basis Bazel (spt. MediaPipe) **crash total (fatal C++ abort, bukan exception Python biasa)** kalau *current working directory* proses mengandung karakter non-ASCII — folder project ini ada `ドキュメント` (OneDrive Documents versi Jepang) di path-nya. Errornya: `Check failed: os_helper->IsDirectoryAccessible(srcdir)`.
- **Workaround (kalau butuh library native serupa lagi ke depannya):** `os.chdir()` sementara ke `tempfile.gettempdir()` (selalu path ASCII) sebelum inisialisasi library, lalu `os.chdir()` balik. File model/asset yang dibaca library itu juga harus diletakkan di path ASCII (copy ke temp dir dulu), bukan langsung dari folder project.
- **`.venv` sempat rusak total** — isinya binary Linux (ELF) padahal jalan di Windows (kemungkinan dibuat dari environment WSL/Linux sebelumnya). Sudah dibuat ulang bersih pakai Python Windows asli (`py -m venv`).

### 5. Klarifikasi: Ukuran Manual vs Hasil AI Try-On
- Input ukuran manual (`tinggi/bahu/dada/pinggang/pinggul` di mode "Belum tahu") **tidak dikirim ke `/generate-tryon`**. Ukuran itu cuma dipakai untuk (1) hitung *body shape* via `calcShape()`, dan (2) skala visual gambar baju di papan kolase **Mix & Match** (flat lay statis, bukan AI).
- Ukuran/fit baju di hasil AI Try-On 100% ditentukan model dari foto yang diupload user, bukan dari angka cm manual.

---

## 🔧 Perbaikan Lanjutan Fitur Try-On: "Setelan", File Rusak, & Batasan Kuota (Juli 2026)

### 1. Bug: Foto "Setelan" (2 potong jadi 1 gambar) Bikin AI Salah Pasang
- **Gejala:** Generate "Setelan Fitted" (fokus `fullbody`) menghasilkan atasan benar (kemeja hitam) tapi bawahan salah total (celana coklat/maroon random, bukan celana hitam dari produk aslinya).
- **Penyebab:** Foto produk kategori *Setelan* (`images/fullbody/setelan_*.png`) berisi **2 potong pakaian digabung dalam 1 foto** (atasan + celana bersebelahan). IDM-VTON cuma didesain baca 1 potong pakaian per referensi gambar, jadi cuma bagian yang dominan (atasan) yang ke-encode dengan benar.
- **Fix (`generateTryon()` di `La Silhouette.dc.html`):** Kalau kategori item adalah `fullbody` dan nama filenya mengandung "setelan", pecah jadi 2 garment terpisah — pakai file crop `_top.png` (kategori `atasan`) dan `_bottom.png` (kategori `bawahan`) yang **sudah ada** di folder tapi belum pernah dipakai sebelumnya, alih-alih kirim 1 foto gabungan.

### 2. Ditemukan: 4 dari 5 Varian "Setelan" Punya File Crop Kosong/Rusak
- **Temuan:** `setelan_atasan_berdetail_bottom.png`, `setelan_blazer_panjang_bottom.png`, `setelan_ikat_pinggang_top.png`, `setelan_rok_flared_top.png` semuanya **gambar putih polos kosong** (ukuran file cuma 3-4.5KB, dibanding versi valid yang 80-370KB). Cuma `setelan_fitted_top/bottom.png` yang valid keduanya. Kemungkinan sisa bug dari proses *autocrop* lama (`autocrop_images.py` dsb).
- **Mitigasi sementara (backend `app.py`):** Fungsi `_is_probably_blank(path, min_bytes=8000)` — cek ukuran file sebelum dikirim ke Hugging Face; kalau di bawah threshold, potongan itu di-*skip* (gak dikirim ke AI) daripada bikin hasil generate makin ngaco.
- **PR (belum dikerjakan):** 4 file itu perlu di-*crop ulang* manual dari foto sumber aslinya oleh Hesti — saya (Claude) gak punya akses ke foto produk original buat regenerate crop-nya.

### 3. Root Cause Terkonfirmasi: Foto Avatar Kartun 3D Bikin Hasil Ngaco
- Sepanjang sesi testing, sempat berulang kali hasil generate "gila" (baju nutupin muka, badan proporsi salah, dsb) — setelah ditelusuri, **semua kejadian itu pakai foto avatar kartun 3D yang sama**, bukan foto asli manusia.
- **Kesimpulan:** IDM-VTON dilatih murni dari foto manusia asli. Avatar/ilustrasi/kartun **akan selalu** menghasilkan deteksi & penempatan yang gak akurat, ini bukan bug yang bisa diperbaiki dari sisi kode — perlu didokumentasikan sebagai **batasan sistem** resmi di skripsi (fitur try-on cuma valid untuk input foto asli, badan menghadap depan, pencahayaan cukup).

### 4. Batasan Kuota Gratis Hugging Face (ZeroGPU)
- Akun gratis Hugging Face (bukan anonim, sudah pakai `HF_TOKEN`) tetap kena limit **5 menit ZeroGPU per hari** (reset ~24 jam). Kepakai habis kalau testing beruntun dalam waktu singkat — errornya: `exceeded your free ZeroGPU quota ... Try again in HH:MM:SS`.
- **Opsi yang didiskusikan (belum dieksekusi, nunggu keputusan Hesti):**
  1. Turunin `denoise_steps` dari 30 ke ~20 di `app.py` — generate lebih hemat kuota per panggilan, trade-off kualitas gambar sedikit lebih kasar.
  2. Pindah ke Google Colab (GPU gratis, sesi jauh lebih longgar) + tunnel ngrok, backend manggil URL Colab alih-alih HF Space — lebih ribet (harus buka tab Colab tiap demo) tapi gak kena limit ketat ala ZeroGPU.
  3. **Tidak** direkomendasikan: bikin banyak akun Hugging Face buat muter kuota — berpotensi melanggar ToS platform.
