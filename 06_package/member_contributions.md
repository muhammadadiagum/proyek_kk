# Catatan kontribusi anggota — Kelompok 1

Mata kuliah: Kecerdasan Komputasional (S2 Teknologi Informasi)
Dosen: Dr. Dessy Santi, S.Kom., M.T.
Topik: GA dengan repair — penjadwalan kuliah dengan kendala ketersediaan dosen
Tanggal: 29 Oktober 2026

> **Catatan kejujuran.** Pembagian di bawah adalah pembagian kerja yang
> direkomendasikan berdasarkan artefak yang benar-benar ada di paket ini, supaya
> setiap anggota dapat ditunjuk pada berkas yang dapat diperiksa. Setiap anggota
> **wajib memverifikasi dan, bila perlu, mengoreksi** bagiannya sebelum
> dikumpulkan; tidak ada kontribusi yang diklaim tanpa artefak yang dapat
> ditelusuri.

| Anggota | NIM | Peran | Artefak yang dapat diperiksa | Butir kontribusi pada naskah |
|---|---|---|---|---|
| Slamet Riyadi | F5522630001 | Ketua, perumusan masalah & protokol | `00_config/design_lock.md`, `07_literature/matrix.md`, `07_literature/references.bib` | §1 Introduction, §3 Problem formulation, §7 Threats to validity |
| Muhammad Adi Agum | F5522630002 | Implementasi inti & akuntansi evaluasi | `02_code/model.py`, `02_code/methods.py`, `02_code/ctt_parser.py` | §4.1 Encoding and operators, §4.2 Repair operator, §3.3 Evaluation accounting |
| Akbar Tri Wicaksono | F5522630003 | Data, generator, dan desain eksperimen | `02_code/generate_instances.py`, `02_code/make_jobs.py`, `02_code/run_experiment.py`, `01_data/` | §4.3 Instances, §4.4 Locked design and pilot |
| I Ketut Divta Suryawan | F5522630004 | Analisis, statistik, dan penyusunan naskah | `02_code/analyze.py`, `02_code/report_numbers.py`, `02_code/build_manuscript.py`, `04_results/`, `05_manuscript/` | §5 Results, §6 Discussion, §8 Conclusion |

Seluruh anggota: verifikasi angka pada `05_manuscript/numbers_main.md` terhadap
`03_experiments/raw/main.jsonl`, penyuntingan bahasa Inggris, dan persetujuan
naskah akhir sebelum submit.

## Berkas bukti eksekusi (untuk pemeriksaan dosen)

| Berkas | Isi | Baris/ukuran |
|---|---|---|
| `03_experiments/raw/pilot.jsonl` | 472 run pilot (grid parameter + baseline) | 472 baris |
| `03_experiments/raw/main.jsonl` | 861 run suite utama (21 instance × 3 metode × 20 seed + baseline) | 861 baris |
| `03_experiments/raw/ablation.jsonl` | 2100 run ablation (5 varian × 21 instance × 20 seed) | 2100 baris |
| `03_experiments/logs/` | log stdout/stderr setiap eksekusi | per-run |
| `04_results/tables/main_tables.xlsx` | tabel deskriptif, statistik, biaya (satu berkas) | 5 sheet |
| `04_results/figures/*.png` | 5 gambar 300 dpi | 5 berkas |
| `00_config/design_lock.md` | kunci desain + amendment log | 191+ baris |

## Pernyataan orisinalitas

Naskah disusun dari hasil eksekusi yang tercatat di `03_experiments/raw/`. Tidak
ada angka pada naskah yang tidak dapat diregenerasi dari berkas mentah tersebut
dengan dua perintah yang tercantum di `README.md`. Referensi diambil dari
Crossref/OpenAlex/Semantic Scholar dan tersimpan lengkap di
`07_literature/refs_verified.json`.
