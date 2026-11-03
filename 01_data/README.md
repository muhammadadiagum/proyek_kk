# 01_data — Data dan Instance

Folder ini berisi seluruh instance yang dipakai dalam eksperimen, baik benchmark publik, sintetis, maupun pilot.

## Struktur

| Path | Isi |
|---|---|
| `benchmark/*.json` | 21 instance benchmark hasil parsing; `comp01`–`comp12` untuk hasil utama, `comp13`–`comp14` untuk pilot, `comp15`–`comp21` cadangan. |
| `benchmark/raw/*.ctt` | Berkas asli ITC2007 CB-CTT sebelum diubah ke model internal. |
| `synthetic/*.json` | 9 instance sintetis (`syn30/60/90` × pola A/B/C). |
| `pilot/*.json` | 2 instance pilot (`pilot45B`, `pilot45C`). |
| `instance_characteristics.csv` | Ringkasan karakteristik instance sintetis dan pilot. |

## 1. Benchmark publik

Instance standar dari kompetisi **ITC2007 Curriculum-Based Course Timetabling (CB-CTT)**. Data tersedia publik dan diturunkan dari kasus penjadwalan nyata, sehingga struktur dan tingkat kesulitannya diakui komunitas.

- Berkas: `benchmark/comp01.json` sampai `benchmark/comp21.json`
- Hasil utama: `comp01`–`comp12` (12 instance)
- Pilot: `comp13`–`comp14`
- Cadangan: `comp15`–`comp21`, tidak dipakai di hasil utama

Fungsi: uji eksternal/realistis. Data tidak dibuat sendiri; proyek memakai salinan publiknya.

## 2. Sintetis

Instance yang dibuat sendiri oleh generator proyek.

- Berkas: `synthetic/syn30A.json` sampai `synthetic/syn90C.json`
- Jumlah: 9 instance
- Kombinasi: 30, 60, dan 90 sesi × pola ketersediaan dosen A/B/C
- Pola A = paling longgar, pola B = sedang, pola C = paling ketat

Setiap instance sintetis dibangun dari jadwal basis yang sudah pasti layak, lalu ketersediaan dosen dipersempit. Karena solusi layaknya dijamin ada, instance ini dipakai untuk mengontrol tingkat kesulitan dan menguji pengaruh ketersediaan dosen secara sistematis.

## 3. Pilot

Pilot bukan jenis sumber data, melainkan **tahap pemakaian**. Pilot dipakai sebelum eksperimen utama untuk memilih konfigurasi (misalnya peluang mutasi dan intensitas repair).

- Instance pilot: `pilot/pilot45B.json` dan `pilot/pilot45C.json`
- Pilot juga memakai `benchmark/comp13.json` dan `benchmark/comp14.json`
- Jumlah run pilot: 472 run

Setelah konfigurasi dikunci, konfigurasi tersebut diuji pada 21 instance utama. Tujuannya agar pemilihan parameter tidak menggunakan data uji.

## Ringkasan

| Kategori | Sumber | Jumlah instance | Peran |
|---|---|---:|---|
| Benchmark publik | ITC2007 CB-CTT | 12 dipakai (`comp01`–`comp12`) | Uji eksternal/realistis |
| Sintetis | Generator proyek | 9 (`syn30/60/90` × A/B/C) | Uji terkontrol |
| Pilot | 2 pilot + `comp13`–`comp14` | 4 | Kalibrasi konfigurasi awal |

## Data yang diolah untuk hasil utama

- 21 instance uji: 12 benchmark + 9 sintetis
- Total isi instance: 3.820 sesi, 209 ruang, 897 dosen, 951 kelompok mahasiswa
- 861 run main: 21 instance × 41 run (20 seed GA + 20 seed GA-R + 1 greedy)
- 2.100 run ablation: 21 instance × 5 varian × 20 seed
- 472 run pilot

Total rekaman run final yang diolah: **3.433 run** (pilot 472 + main 861 + ablation 2.100).

## Catatan

- `comp15`–`comp21` adalah cadangan; jangan dianggap bagian hasil utama.
- Pilot adalah tahap kalibrasi, bukan data uji final.
- File `*.json` adalah model internal hasil parsing/generasi; berkas asli benchmark ada di `benchmark/raw/*.ctt`.
- Jangan mengedit instance secara manual; gunakan `02_code/ctt_parser.py` atau `02_code/generate_instances.py` bila perlu meregenerasi.
