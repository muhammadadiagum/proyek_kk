# Dua calon jurnal (terverifikasi di situs resmi)

Diperiksa: 29 Oktober 2026. Semua pernyataan di bawah dikutip/diringkas dari
halaman resmi Springer Nature Link yang URL-nya dicantumkan. Tidak ada nomor
APC, kuartil, atau faktor dampak yang dicantumkan karena angka tersebut tidak
kami baca dari halaman resmi pada tanggal ini — periksa kembali saat submit.

---

## Kandidat 1 — *Journal of Scheduling* (J Sched)

- Penerbit: Springer (Springer-Verlag). ISSN 1094-6136 (cetak), 1099-1425 (elektronik) — dikonfirmasi lewat Crossref `api.crossref.org/journals/1094-6136`.
- Halaman resmi: https://link.springer.com/journal/10951 dan https://link.springer.com/journal/10951/aims-and-scope
- Lingkup (kutipan ringkas dari halaman *Aims and scope*): "a recognized global forum for the publication of all forms of scheduling research … covers advances in scheduling research, such as the latest techniques, applications, theoretical issues and novel approaches to problems", relevan bagi Computer Science, Operational Research, Engineering, Artificial Intelligence, dan lain-lain.
- Kesesuaian dengan artikel kita: penjadwalan (timetabling) adalah inti lingkup jurnal; artikel kita mengukur trade-off kualitas–biaya pada algoritma penjadwalan, bukan metode baru untuk masalah lain.
- Jalur submit: tombol "Submit manuscript" pada halaman jurnal; sistem naskah baru adalah Snapp (Springer Nature Article Processing Platform).
- Format berkas: panduan penulis meminta "all relevant editable source files" dan menyatakan naskah teks harus dalam format pengolah kata umum seperti **.docx** atau LaTeX.
- Deklarasi wajib saat submit: *Author Contribution* dan *Competing Interests* lewat antarmuka submisi; *Data Availability Statement* sesuai kebijakan riset data Springer Nature.
- Model akses: hybrid — artikel dapat terbit lewat langganan atau *Open Choice* (open access berbayar). Biaya open access tidak dicantumkan di halaman yang kami periksa; cek halaman APC jurnal sebelum memilih.
- Catatan penting untuk kita: jurnal ini menyatakan bahwa artikel yang tidak menyertakan berkas sumber lengkap "will result in your article not being considered for review".

## Kandidat 2 — *Journal of Heuristics* (J Heuristics)

- Penerbit: Springer. ISSN 1381-1231 (cetak), 1572-9397 (elektronik) — dikonfirmasi lewat Crossref `api.crossref.org/journals/1381-1231`.
- Halaman resmi: https://link.springer.com/journal/10732 dan https://link.springer.com/journal/10732/aims-and-scope
- Lingkup: halaman *Aims and scope* membagi jurnal menjadi area terkelola, antara lain **Adaptive Memory Programming**, **Artificial Intelligence and Constraint Programming**, **Combinatorial Optimization**, **Evolutionary Computation**, dan **Real-World Applications**.
- Persyaratan eksplisit yang menguntungkan artikel kita (kutipan dari halaman *Aims and scope*): "If the work is empirical, it is important that sound scientific methods be employed. In particular, it is important the test data sets used in the work be made available to the research community. Additionally, concise statements of hypothesis must be provided along with the evidence that supports them. Both statistical and qualitative significance should be demonstrated."
  → Artikel kita sudah memenuhi tiga hal ini: dataset + generator + indeks split dirilis, hipotesis dinyatakan di bagian 1 dan diuji di bagian 5, dan signifikansi statistik dilaporkan dengan effect size serta koreksi Holm.
- Jalur submit: "Submit manuscript" pada halaman jurnal, melalui Snapp.
- Format berkas: sama seperti jurnal Springer lain — .docx atau LaTeX sebagai berkas sumber yang dapat diedit.
- Model akses: hybrid (langganan atau *Open Choice*).
- Catatan: ada *call for papers* terbuka untuk **Special Issue: Parallel Metaheuristics** di https://link.springer.com/collections/faheabejbj (status: open for submissions, tenggat "ongoing"). Artikel kita **bukan** metaheuristik paralel, jadi kami tidak mengarahkan submisi ke special issue itu; disebutkan di sini hanya agar tidak salah pilih jalur saat submit.

---

## Rekomendasi urutan

1. **Journal of Heuristics** — kesesuaian paling dekat dengan kontribusi (studi empiris komparatif algoritma evolusioner dengan analisis biaya evaluasi), dan persyaratan mereka (data tersedia, hipotesis jelas, signifikansi statistik) persis yang sudah dipenuhi paket ini.
2. **Journal of Scheduling** — alternatif bila editor menilai kontribusinya lebih tepat sebagai studi penjadwalan terapan.

Submisi dilakukan ke **satu** jurnal pada satu waktu, setelah dosen menyetujui. Berkas yang dibutuhkan untuk keduanya sudah tersedia dalam paket ini:
`05_manuscript/*.docx`, `03_experiments/raw/*.jsonl`, `04_results/`, `02_code/`, `01_data/`, `README.md`, dan `06_package/cover_letter.md`.

## Hal yang harus dicek ulang oleh user sebelum submit

- APC/*Open Choice* terkini pada halaman jurnal (angka tidak kami cantumkan karena tidak diverifikasi).
- Apakah jurnal memakai *double-anonymous peer review* pada saat submit; bila ya, anonimkan nama penulis di berkas dan metadata (panduan Springer menyarankan anonimisasi data juga).
- Format referensi akhir: panduan Springer menerima gaya yang konsisten; kami memakai APA 7, yang perlu diseragamkan bila editor meminta gaya lain.
