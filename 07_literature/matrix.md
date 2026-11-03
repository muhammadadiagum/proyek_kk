# Matriks studi terdekat (12 studi)

Kolom **Relation to this study** menyatakan *perbedaan cakupan*, bukan klaim
bahwa studi lain tidak membahas hal tersebut. Metadata setiap entri diverifikasi
lewat Crossref/OpenAlex (`refs_verified.json`); ringkasan isi diambil dari
abstrak resmi yang tersedia publik.

| # | Studi | Masalah / setting | Metode | Anggaran komputasi dilaporkan | Fokus evaluasi | Relation to this study |
|---|---|---|---|---|---|---|
| 1 | Ceschia, Da Ros, Di Gaspero & Schaerf (2026), *Computers & Operations Research* 195:107621 | CB-CTT (dataset ITC2007 dan sintetis) | *Local search* yang direvisi/ dikonfigurasi ulang untuk beragam dataset | Batas waktu (*time limit*) sebagai setting eksperimen | Efektivitas local search lintas dataset di bawah batas waktu | Fokus pada neighbourhood local search; studi ini menyoroti bahwa desain yang bekerja lintas dataset di bawah batas waktu masih sulit. Penelitian kami memisahkan **biaya repair** dari biaya evaluasi dalam GA. |
| 2 | Nguyen (2026), ICAART 2026 | ITC-2007 Track 3 (CB-CTT) | VND dengan penalti adaptif, inisialisasi CP-SAT, gerak *Kempe-chain* + min-cost max-flow untuk penempatan ruang | Tidak berhenti pada anggaran evaluasi tetap; solusi awal feasible dijamin CP | Kualitas solusi akhir (penalti) | Inisialisasi feasible dijamin oleh model CP; dalam penelitian kami anggaran evaluasi sama untuk semua metode dan kelayakan awal tidak dijamin. |
| 3 | Steiner, Pferschy & Schaerf (2024), *CEJOR* 33:277–314 | Penjadwalan kurikulum empat tahun dengan kombinasi mata pelajaran bebas | *Decomposition* + optimasi (heuristik/eksak) | Tidak dilaporkan sebagai anggaran evaluasi | Kelayakan untuk setiap kombinasi pilihan mahasiswa | Menangani kendala kurikulum jauh lebih kaya; kami memakai CB-CTT standar untuk mengisolasi efek ketersediaan dosen. |
| 4 | Abdipoor, Yaakob, Goh & Abdullah (2023), *Intelligent Systems with Applications* 19:200253 | University Course Timetabling | Tinjauan pendekatan metaheuristik | Tinjauan (tidak mengeksekusi anggaran seragam) | Klasifikasi metode dan isu terbuka | Menunjukkan metaheuristik adalah arus utama; penelitian kami menjawab isu *perbandingan adil biaya kendala*. |
| 5 | Badoni, Sahoo, Srivastava, Mann, Gupta & Verma (2023), *Axioms* 12(8):720 | University Course Timetabling | Kombinasi strategi eksplorasi–eksploitasi | Tidak dibandingkan pada anggaran evaluasi tetap | Kualitas solusi pada instance uji | Menekankan keseimbangan eksplorasi–eksploitasi; kami mengukur bagaimana repair menggeser keseimbangan itu pada anggaran tetap. |
| 6 | Dunke & Nickel (2023), *Annals of Operations Research* 328:1313–1348 | Penjadwalan universitas multi-level multi-kriteria | Matheuristik (dekomposisi + model eksak) | Biaya komputasi tidak dinormalisasi ke jumlah evaluasi | Kualitas multi-kriteria dan preferensi | Optimasi parsial eksak per blok; kami memakai GA dengan anggaran evaluasi tertutup agar perbandingan setara. |
| 7 | Erdoğan Akbulut, Özçelik & Saraç (2024), *Pamukkale Univ. J. Eng. Sci.* 30(1):17–30 | Penjadwalan tingkat fakultas dengan kendala *double major/minor* | Simulated annealing + model *goal programming* | Dilaporkan sebagai parameter algoritma, bukan anggaran evaluasi | Kelayakan kendala dan deviasi tujuan | Menangani kendala administratif tambahan; kami menstandarkan kendala CB-CTT dan membandingkan dua varian GA pada anggaran sama. |
| 8 | Romaguera, Plender-Nabas, Matias & Austero (2024), *Procedia Computer Science* 234:1714–1721 | Penjadwalan mata kuliah berbasis web | GA dengan mutasi heuristik yang memfokuskan gen tak-feasible | Tidak dilaporkan sebagai anggaran evaluasi | Efektivitas mutasi heuristik | Mutasi terarah mirip repair kami; perbedaannya, kami **membebankan** setiap kandidat repair ke anggaran dan mengukur biayanya. |
| 9 | Li & Gonsalves (2022), *The Chinese Journal of Artificial Intelligence* 1(1) | Penjadwalan ujian di universitas Jepang | Varian GA (encoding + operator khusus) | Tidak dilaporkan sebagai anggaran evaluasi | Kualitas jadwal ujian | Studi kasus tunggal tanpa perbandingan anggaran; kami memakai 21 instance dengan split dev/test dan 10 seed. |
| 10 | Zhang, Ku & Zhao (2026), *Symmetry* 18(4):641 | Optimasi multiobjektif berkendala dengan daerah feasible sempit | *Seeding* sadar-struktur, operator repair berbasis proyeksi, dua populasi | Anggaran evaluasi disebut sebagai kendala desain | Kelayakan dan keragaman | Konfirmasi bahwa repair penting saat daerah feasible sempit; kami mengukur **harga** repair dalam satuan evaluasi pada satu objektif leksikografis. |
| 11 | Zhao, Sun, Wang & Sang (2026), *IEEE Transactions on Evolutionary Computation* (early access) | Penjadwalan *hybrid flow shop* sadar-energi | EA *surrogate-assisted* yang sadar-anggaran dan dipandu kelayakan | Anggaran evaluasi eksplisit (mahal, surrogate) | Kualitas vs jumlah evaluasi | Sejalan pada premis anggaran-sadar; domain berbeda dan tidak mengisolasi biaya repair relatif terhadap variasi ketersediaan. |
| 12 | López-Ibáñez, Dubois-Lacoste, Pérez Cáceres, Birattari & Stützle (2016), *Operations Research Perspectives* 3:43–58 | Konfigurasi otomatis algoritma | *Iterated racing* (irace) | Anggaran evaluasi konfigurasi dilaporkan | Kualitas konfigurasi | Kami tidak memakai irace; pemilihan parameter dilakukan lewat grid pilot terbatas yang dikunci sebelum data test, untuk menghindari penyetelan pada data test. |

## Catatan sintesis

- Metaheuristik untuk penjadwalan pendidikan umumnya dilaporkan dengan batas
  waktu atau iterasi; **perbandingan yang menormalkan biaya kendala** (repair,
  inisialisasi) ke dalam anggaran evaluasi masih jarang dinyatakan eksplisit.
- Studi terbaru (2022–2026) menunjukkan dua arah: (i) neighbourhood/local search
  yang makin canggih untuk CB-CTT, dan (ii) *constraint handling* berbasis
  repair/proyeksi pada EA. Penelitian ini menghubungkan keduanya dengan
  mengukur *ongkos* repair di dalam GA pada anggaran tetap.
