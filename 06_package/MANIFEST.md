# MANIFEST paket submit — Kelompok 1

Diperbarui: 29 Oktober 2026. Semua berkas berada di
`/home/aec/_AO/PATHs/S2/AO_PAPERs/COURSE_EXAM/KK/`.

## 1. Naskah

| Berkas | Ukuran | Keterangan |
|---|---|---|
| `05_manuscript/manuscript.docx` | 648 KB | **berkas utama** untuk submit (format yang diminta Springer) |
| `05_manuscript/manuscript.pdf` | 884 KB | PDF untuk dosen/pembaca (16 halaman, 5 gambar tertanam; teks rata kiri-kanan) |
| `05_manuscript/manuscript.md` | 52 KB | sumber Markdown yang dihasilkan `build_manuscript.py` |
| `05_manuscript/manuscript_source.md` | 36 KB | sumber tunggal seluruh teks (satu baris per paragraf); `build_manuscript.py` mengisi tabel, referensi, dan placeholder angka |
| `05_manuscript/idn/manuscript_source_id.md` | 46 KB | terjemahan Indonesia dari sumber di atas (nomor, sitasi, tabel, dan placeholder identik) |
| `05_manuscript/idn/manuscript_id.docx` / `.pdf` | 672 KB / 884 KB | versi bahasa Indonesia (16 halaman, tabel + gambar berlabel Indonesia) — **pendamping, bukan naskah submit** |
| `05_manuscript/numbers_main.md` | 8 KB | lembar angka: semua tabel hasil dalam satu berkas |

Naskah: judul, abstrak, 8 bagian, 5 gambar, 7 tabel + tabel lampiran, 26
referensi (19 terbit 2022–2026), bagian Declarations (kontribusi penulis, data,
kode, competing interests, penggunaan AI generatif).

## 2. Slide presentasi

| Berkas | Ukuran | Keterangan |
|---|---|---|
| `06_package/slides_kelompok1.pptx` | 340 KB | 15 slide (batas brief 10–15), dua gambar hasil, angka dari CSV |

## 3. Kode dan lingkungan

| Berkas | Keterangan |
|---|---|
| `02_code/*.py` | 15 skrip: parser, model+validator, generator, metode (GA/GA+repair), pembuat job, runner, pemilih konfigurasi pilot, analisis, perbandingan ablation, lembar angka, penyusun naskah, konverter DOCX/PDF, slide, ekspor mentah |
| `02_code/requirements.txt` | numpy 2.5.4, scipy 1.18.1, pandas 3.1.0, matplotlib 3.11.2, openpyxl 3.1.5, python-docx, python-pptx |
| `README.md` | struktur, lingkungan (i7-13650HX, 14 vCPU, 8 GB, WSL2), perintah reproduksi, format catatan per run |

## 4. Data

| Berkas | Ukuran | Keterangan |
|---|---|---|
| `01_data/synthetic/*.json` | 9 berkas | instance sintetis 30/60/90 sesi × pola A/B/C, `base_solution` tersimpan, seed generator tercatat |
| `01_data/pilot/*.json` | 2 berkas | instance pilot (`pilot45B`, `pilot45C`) |
| `01_data/benchmark/raw/*.ctt` | 21 berkas | ITC2007 Track 2 asli, tanpa modifikasi |
| `01_data/benchmark/*.json` | 21 berkas | hasil konversi `ctt_parser.py` |
| `02_code/generate_instances.py` | — | generator + seed; lisensi data: lihat `README.md` §Data |

## 5. Hasil mentah

| Berkas | Baris | Keterangan |
|---|---|---|
| `03_experiments/raw/pilot.jsonl` | 472 | pilot grid + baseline |
| `03_experiments/raw/main.jsonl` | 861 | suite utama (21 instance × 3 metode; 20 seed untuk metode stokastik) |
| `03_experiments/raw/ablation.jsonl` | 2100 | 5 varian × 21 instance × 20 seed |
| `06_package/raw_results/{pilot,main,ablation}_runs.csv` | 472 / 861 / 2100 | ekspor tabel dari JSONL di atas |
| `06_package/raw_results/all_runs.xlsx` | 3 sheet | sama, dalam satu buku kerja |
| `03_experiments/logs/run_*.log` | — | stdout tiap eksekusi + identitas host/versi |

## 6. Tabel dan gambar

| Berkas | Keterangan |
|---|---|
| `04_results/tables/main_*.csv` | deskriptif, statistik, biaya, per keluarga |
| `04_results/tables/ablation_*.csv` | deskriptif + perbandingan varian vs konfigurasi terkunci |
| `04_results/tables/main_tables.xlsx`, `ablation_tables.xlsx` | versi buku kerja |
| `04_results/tables/pilot_selection.csv` | grid pilot + konfigurasi terpilih |
| `04_results/figures/main_fig1..5.png` | 5 gambar 300 dpi yang dipakai naskah |
| `04_results/figures/ablation_fig1..5.png` | gambar pendukung ablation |
| `04_results/figures/idn/main_fig1..5.png` | lima gambar yang sama dengan label bahasa Indonesia (dipakai naskah versi Indonesia) |

## 7. Kunci desain dan administrasi

| Berkas | Keterangan |
|---|---|
| `00_config/design_lock.md` | RQ, hipotesis, split, seed, budget, aturan berhenti, parameter final, **amendment log** (perubahan daftar varian ablation sebelum hasil test dibaca) |
| `00_config/config_final.json` | konfigurasi final hasil pilot |
| `00_config/jobs_{pilot,main,ablation}.json` | spesifikasi run yang dieksekusi |
| `06_package/claims_evidence.md` | 20 klaim → berkas bukti → perintah pemeriksa |
| `06_package/member_contributions.md` | peran + artefak per anggota (wajib diverifikasi anggota) |
| `06_package/cover_letter.md` | draft surat pengantar |
| `06_package/journal_candidates.md` | dua calon jurnal + kutipan lingkup resmi + catatan yang harus dicek ulang |
| `07_literature/matrix.md` | matriks 12 studi terdekat |
| `07_literature/references.md`, `.bib`, `refs_verified.json` | 26 referensi, metadata dari Crossref/OpenAlex/S2 |

## 8. Status terhadap syarat brief

| Syarat | Status |
|---|---|
| Satu aspek terukur (bukan arsitektur baru) | ✅ repair vs tanpa repair pada anggaran evaluasi identik |
| Disiplin anggaran (semua evaluasi dihitung) | ✅ `design_lock.md` §5, terlihat di `repair_share` tiap run |
| Anti-kebocoran (kunci sebelum test) | ✅ `design_lock.md` bertanggal 2026-10-29, split dev/test terpisah, amendment log |
| 20 seed untuk metode stokastik | ✅ `range(1,21)`, terlihat di JSONL |
| Run gagal dicatat sebagai gagal | ✅ comp01 & comp05 dilaporkan gagal mencapai feasible |
| Statistik berpasangan per instance + effect size | ✅ Wilcoxon, Friedman, Holm, Cliff's delta, McNemar |
| ≥20 referensi, ≥12 dari 2022–2026, matriks 10–15 studi | ✅ 26 referensi (19 dari 2022–2026), matriks 12 studi |
| Naskah Inggris siap submit + Word + PDF | ✅ `manuscript.docx` + `manuscript.pdf` |
| Kode + README + environment + data + hasil mentah + gambar | ✅ bagian 3–6 di atas |
| Slide 10–15 halaman | ✅ 15 slide |
| Catatan kontribusi anggota | ✅ `member_contributions.md` (wajib dikonfirmasi anggota) |
| Draft cover letter + dua calon jurnal terverifikasi | ✅ `cover_letter.md`, `journal_candidates.md` |
| Tabel klaim → hasil eksperimen | ✅ `claims_evidence.md` |
| Submit satu jurnal setelah persetujuan dosen | ⏳ menunggu persetujuan dosen dan pemeriksaan akhir anggota |

## 9. Cara memeriksa ulang seluruh angka

```bash
cd /home/aec/_AO/PATHs/S2/AO_PAPERs/COURSE_EXAM/KK
.venv/bin/python 02_code/analyze.py --raw 03_experiments/raw/main.jsonl --label main
.venv/bin/python 02_code/analyze.py --raw 03_experiments/raw/ablation.jsonl --label ablation
.venv/bin/python 02_code/ablation_compare.py
.venv/bin/python 02_code/report_numbers.py --label main
.venv/bin/python 02_code/build_manuscript.py --label main
.venv/bin/python 02_code/md2docx.py 05_manuscript/manuscript.md 05_manuscript/manuscript.docx --pdf

# versi bahasa Indonesia (angka dari CSV yang sama)
.venv/bin/python 02_code/analyze.py --raw 03_experiments/raw/main.jsonl --label main \
        --lang id --figdir 04_results/figures/idn
.venv/bin/python 02_code/build_manuscript.py --label main --lang id
.venv/bin/python 02_code/md2docx.py 05_manuscript/idn/manuscript_id.md \
        05_manuscript/idn/manuscript_id.docx --pdf
```

Keluaran yang diharapkan identik dengan berkas di paket ini; bila berbeda,
berkas mentah di `03_experiments/raw/` adalah sumber kebenaran.
