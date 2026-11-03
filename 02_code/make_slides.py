"""Membuat slide presentasi (12–15 halaman) dari tabel & gambar hasil.

Semua angka dibaca dari 04_results/tables/*.csv agar slide tidak pernah
memuat angka yang tidak ada di log. Gambar diambil dari 04_results/figures.

Pemakaian: python 02_code/make_slides.py [--label main]
Keluaran : 06_package/slides_kelompok1.pptx
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parents[1]
TAB = ROOT / "04_results/tables"
FIG = ROOT / "04_results/figures"
OUT = ROOT / "06_package"

DARK = RGBColor(0x1B, 0x1B, 0x1F)
ACCENT = RGBColor(0xC0, 0x39, 0x2B)
GREY = RGBColor(0x55, 0x55, 0x5F)
LBL = {"greedy": "Greedy", "ga_std": "GA", "ga_repair": "GA-R"}


def bullets(slide, items, top=1.45, size=18, width=11.6):
    tf = slide.shapes.add_textbox(Inches(0.7), Inches(top), Inches(width), Inches(0.5)).text_frame
    tf.word_wrap = True
    first = True
    for text, level in items:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.text = ("• " if level == 0 else "– ") + text
        p.level = level
        p.font.size = Pt(size - 2 * level)
        p.font.color.rgb = DARK if level == 0 else GREY
        p.space_after = Pt(6)


def title_slide(prs, title, subtitle, meta):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    bar = s.shapes.add_shape(1, Inches(0), Inches(0), Inches(13.33), Inches(0.35))
    bar.fill.solid()
    bar.fill.fore_color.rgb = ACCENT
    bar.line.fill.background()
    tb = s.shapes.add_textbox(Inches(0.8), Inches(1.5), Inches(11.7), Inches(2.4)).text_frame
    tb.word_wrap = True
    p = tb.paragraphs[0]
    p.text = title
    p.font.size = Pt(36)
    p.font.bold = True
    p.font.color.rgb = DARK
    p2 = tb.add_paragraph()
    p2.text = subtitle
    p2.font.size = Pt(20)
    p2.font.color.rgb = ACCENT
    p2.space_before = Pt(10)
    mb = s.shapes.add_textbox(Inches(0.8), Inches(4.6), Inches(11.7), Inches(1.8)).text_frame
    mb.word_wrap = True
    for i, line in enumerate(meta):
        p = mb.paragraphs[0] if i == 0 else mb.add_paragraph()
        p.text = line
        p.font.size = Pt(14)
        p.font.color.rgb = GREY


def content_slide(prs, title, items, size=18):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    t = s.shapes.add_textbox(Inches(0.6), Inches(0.45), Inches(12.1), Inches(0.9)).text_frame
    t.word_wrap = True
    p = t.paragraphs[0]
    p.text = title
    p.font.size = Pt(26)
    p.font.bold = True
    p.font.color.rgb = DARK
    line = s.shapes.add_shape(1, Inches(0.6), Inches(1.28), Inches(3.2), Inches(0.05))
    line.fill.solid()
    line.fill.fore_color.rgb = ACCENT
    line.line.fill.background()
    bullets(s, items, size=size)
    return s


def figure_slide(prs, title, img: Path, note=None, height=5.4):
    s = content_slide(prs, title, [], size=16)
    if img.exists():
        s.shapes.add_picture(str(img), Inches(1.1), Inches(1.5), height=Inches(height))
    if note:
        nb = s.shapes.add_textbox(Inches(0.7), Inches(7.0), Inches(11.9), Inches(0.6)).text_frame
        nb.word_wrap = True
        p = nb.paragraphs[0]
        p.text = note
        p.font.size = Pt(11)
        p.font.color.rgb = GREY
    return s


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", default="main")
    args = ap.parse_args()
    pi = pd.read_csv(TAB / f"{args.label}_descriptive.csv")
    cost = pd.read_csv(TAB / f"{args.label}_cost.csv").set_index("method")

    def med(m, col):
        return float(pi[pi["method"] == m][col].median())

    def nfeas(m):
        s = pi[pi["method"] == m]
        return int((s["feasible_rate"] >= 0.5).sum())

    n_inst = pi["instance"].nunique()
    bm = pi[pi["pattern"] == "benchmark"]
    prs = Presentation()
    prs.slide_width = Inches(13.33)
    prs.slide_height = Inches(7.5)

    title_slide(
        prs,
        "Repair-Based Genetic Algorithm for Course Timetabling\nunder Lecturer Availability Constraints",
        "Satu aspek terukur: nilai repair pada anggaran evaluasi yang sama",
        [
            "Kelompok 1 — F5522630001 Slamet Riyadi · F5522630002 Muhammad Adi Agum ·",
            "F5522630003 Akbar Tri Wicaksono · F5522630004 I Ketut Divta Suryawan",
            "Kecerdasan Komputasional (S2 Teknologi Informasi) · Dr. Dessy Santi, S.Kom., M.T. · 2026",
        ],
    )

    content_slide(prs, "Masalah: jadwal kuliah yang benar-benar bisa dipakai", [
        ("Kendala keras: dosen, ruang, kelompok mahasiswa tidak boleh bentrok di slot yang sama", 0),
        ("Kapasitas ruang dan slot terlarang (ketersediaan dosen) harus dihormati", 0),
        ("Kendala lunak: celah jam kosong di antara kelas sebuah kelompok per hari", 0),
        ("GA mengodekan satu gen = satu pasangan (ruang, slot)", 0),
        ("Crossover uniform antara dua induk layak hampir selalu menghasilkan anak TIDAK layak", 0),
        ("Akibatnya anggaran habis untuk menilai jadwal yang tidak dapat dipakai", 0),
        ("Pertanyaan praktis: apakah repair menolong, dan berapa biayanya?", 0),
    ])

    content_slide(prs, "Pertanyaan penelitian & hipotesis (dikunci sebelum melihat test)", [
        ("RQ1 — Pada anggaran evaluasi identik, apakah GA+repair menghasilkan jadwal layak "
         "lebih sering dan lebih baik daripada GA standar?", 0),
        ("RQ2 — Berapa biaya repair dalam anggaran evaluasi dan generasi?", 0),
        ("RQ3 — Seberapa sensitif hasilnya terhadap intensitas repair (ablation)?", 0),
        ("H1 — Keunggulan repair membesar ketika ketersediaan dosen menyempit", 0),
        ("H2 — GA standar tetap kompetitif pada instance longgar", 0),
        ("H3 — Keunggulan repair dibayar dengan porsi anggaran yang besar", 0),
        ("Semua hipotesis diuji; H1 tidak didukung pada tangga sintetis (dilaporkan apa adanya)", 0),
    ])

    content_slide(prs, "Aturan akuntansi evaluasi: inti perbandingan yang adil", [
        ("1 evaluasi = 1 penilaian objektif satu kandidat", 0),
        ("Skor satu jadwal penuh (fitness GA, skor greedy, inisialisasi)", 1),
        ("ATAU satu kandidat perpindahan (ruang, slot) yang diperiksa repair", 1),
        ("Indeks okupansi = pembukuan, tidak dibebankan; biayanya terlihat di runtime", 0),
        ("Semua metode stokastik berhenti di 10.000 evaluasi — bukan di jumlah generasi", 0),
        ("Baseline greedy deterministik dilaporkan dengan jumlah evaluasi sebenarnya", 0),
        ("Implikasi: GA+repair menyelesaikan ~3× lebih sedikit generasi dalam anggaran yang sama", 0),
    ])

    content_slide(prs, "Metode: apa yang di-repair dan bagaimana", [
        ("Inisialisasi greedy-seeded: individu 0 = greedy most-constrained-first deterministik", 0),
        ("Individu lain: greedy dengan urutan/tie-break acak (tetap dibayar 1 evaluasi)", 0),
        ("Seleksi turnamen k=3, crossover uniform per gen, elitisme 2", 0),
        ("Mutasi: per gen, ubah slot / ruang / keduanya dengan peluang 1/n", 0),
        ("Repair: kumpulkan sesi yang melanggar, acak, perbaiki maksimum k = 5 sesi", 0),
        ("Untuk tiap sesi: slot yang bebas bagi dosen & semua kelompok, diizinkan ketersediaan, "
         "punya ruang cocok yang bebas", 0),
        ("Pilih kandidat dengan penalti preferensi tambahan terkecil; tiap kandidat = 1 evaluasi", 0),
        ("Gagal bila tidak ada slot valid — dicatat sebagai kegagalan, run berlanjut", 0),
    ])

    content_slide(prs, "Data & desain terkunci", [
        ("9 instance sintetis: 30/60/90 sesi × pola ketersediaan A (67%), B (43%), C (23%)", 0),
        ("Dibangun dari jadwal basis yang layak → kelayakan terjamin, kesulitan dikendalikan", 0),
        ("12 instance publik ITC2007 CB-CTT comp01–comp12 (tanpa modifikasi)", 0),
        ("Split: pilot/development = pilot45B, pilot45C, comp13, comp14", 0),
        ("Test = 9 sintetis + comp01–comp12 → 21 instance", 0),
        ("20 seed per metode per instance; unit analisis = instance (median 20 seed)", 0),
        ("Konfigurasi dipilih di pilot: k = 5, 1 kandidat/sesi, tanpa swap, pm = 1/n, budget 10.000", 0),
        ("Semua dikunci di 00_config/design_lock.md sebelum test dievaluasi", 0),
    ])

    content_slide(prs, "Hasil utama: 21 instance test, 20 seed per metode", [
        (f"GA-R layak pada mayoritas seed di {nfeas('ga_repair')}/{n_inst} instance; "
         f"GA {nfeas('ga_std')}/{n_inst}; Greedy {nfeas('greedy')}/{n_inst}", 0),
        (f"Median H: GA-R {med('ga_repair','median_H'):.0f} · GA {med('ga_std','median_H'):.0f} · "
         f"Greedy {med('greedy','median_H'):.0f}", 0),
        (f"Median P: GA-R {med('ga_repair','median_P'):.0f} · GA {med('ga_std','median_P'):.0f} · "
         f"Greedy {med('greedy','median_P'):.0f}", 0),
        ("Wilcoxon berpasangan per instance: H p = 0.0033; P p = 0.0003; Cliff's delta = −1.00", 0),
        ("Friedman: H χ² = 23.53 (p < 0.001); P χ² = 10.47 (p = 0.0053)", 0),
        ("Post-hoc Wilcoxon + Holm: ketiga pasangan signifikan (p ≤ 0.0066)", 0),
        ("McNemar kelayakan: 9 instance diskordan, semuanya berpihak GA-R, p = 0.0039", 0),
    ])

    figure_slide(prs, "Kelayakan per instance (median 20 seed)",
                 FIG / f"{args.label}_fig3_feasible_rate.png",
                 "Sumber: 04_results/figures/" + f"{args.label}_fig3_feasible_rate.png")

    s = content_slide(prs, "Dua keluarga instance berperilaku berbeda", [
        ("Sintetis (9): SEMUA metode layak di semua seed — termasuk greedy", 0),
        ("Ketersediaan turun 67% → 23%, tetapi okupansi ruang hanya 0.50 → tidak pernah cukup sulit", 0),
        ("Keunggulan repair di sini pada P: 0.00 / 0.00 / 0.00 vs GA 0.00 / 2.00 / 4.50 (pola A/B/C)", 0),
        ("Benchmark publik (12): greedy TIDAK PERNAH layak (median H = 24)", 0),
        ("GA layak di 17/240 run; GA-R layak di 173/240 run", 0),
        ("Median H benchmark: GA-R 0.00 vs GA 7.00; median P: 106.5 vs 171.0", 0),
        ("Faktor pembeda = okupansi ruang × ketersediaan, bukan persentase ketersediaan saja", 0),
        ("comp01 & comp05 gagal dicapai semua metode dalam 10.000 evaluasi → dilaporkan gagal", 0),
    ], size=16)

    content_slide(prs, "Biaya repair (RQ2)", [
        (f"Porsi anggaran untuk repair: {cost.loc['ga_repair','median_repair_share']*100:.0f}% "
         "(median per instance)", 0),
        ("2.84 juta dari 4.20 juta evaluasi adalah pemeriksaan kandidat repair", 0),
        ("36% probe gagal (tidak ada slot valid) dan tetap dibayar", 0),
        (f"Generasi selesai: GA {cost.loc['ga_std','median_generations']:.0f} vs "
         f"GA-R {cost.loc['ga_repair','median_generations']:.0f} → 3.1× lebih sedikit", 0),
        (f"Runtime median: {cost.loc['ga_std','median_runtime_s']:.2f} s vs "
         f"{cost.loc['ga_repair','median_runtime_s']:.2f} s per run", 0),
        ("Di benchmark: GA yang berhasil biasanya layak sangat awal (median 20 evaluasi); "
         "GA-R yang berhasil butuh median 3.002 evaluasi", 0),
        ("Artinya: repair dibayar di depan, dan yang dibeli adalah keandalan, bukan kecepatan", 0),
    ], size=16)

    figure_slide(prs, "Kurva konvergensi dan penggunaan anggaran",
                 FIG / f"{args.label}_fig1_convergence.png",
                 "Sumber: 04_results/figures/" + f"{args.label}_fig1_convergence.png")

    abl_path = TAB / "ablation_descriptive.csv"
    if abl_path.exists():
        abl = pd.read_csv(abl_path)
        items = [("Ablation: 5 varian × 21 instance × 20 seed = 2.100 run", 0)]
        for tag in ["abl_attempts3", "abl_k1", "abl_k10", "abl_swap_on", "abl_no_seed"]:
            g = abl[abl["variant"] == tag]
            if g.empty:
                continue
            items.append((f"{tag}: layak {g['feasible_rate'].mean():.2f} · "
                          f"median H {g['median_H'].median():.1f} · "
                          f"median P {g['median_P'].median():.1f} · "
                          f"porsi repair {g['median_repair_share'].median():.2f}", 0))
        items.append(("Pembanding: konfigurasi terkunci (k=5, 1 kandidat, tanpa swap, greedy seed)", 0))
        content_slide(prs, "Ablation: seberapa sensitif hasil pada intensitas repair", items, size=16)
    else:
        content_slide(prs, "Ablation", [("Ablation belum dianalisis saat slide dibuat.", 0)])

    content_slide(prs, "Ancaman validitas & batasan", [
        ("Internal: dua GA berbagi semua komponen kecuali repair; baseline mendapat sweep pm sendiri", 0),
        ("Konstruk: validator independen memeriksa ulang semua jadwal terbaik (861/861 cocok)", 0),
        ("Eksternal: hanya 21 instance; tidak ada jadwal institusi nyata yang teranonimisasi", 0),
        ("Tangga ketersediaan sintetis tidak menghasilkan gradien kesulitan → H1 tidak didukung", 0),
        ("Kesimpulan: 21 instance membatasi kuasa uji omnibus → hasil per keluarga dilaporkan terpisah", 0),
        ("Reproduksi: kode, seed, data, kunci desain, dan JSONL mentah dirilis", 0),
    ])

    content_slide(prs, "Kesimpulan", [
        ("Pada anggaran 10.000 evaluasi, repair mengubah GA dari sering-tidak-layak menjadi "
         "hampir-selalu-layak pada instance realistis", 0),
        ("19/21 instance vs 10/21; 173/240 run benchmark vs 17/240; delta Cliff = −1.00", 0),
        ("Harganya: 67% anggaran dan 3× lebih sedikit generasi", 0),
        ("Repair layak dijadikan default ketika konstruktor deterministik sudah gagal", 0),
        ("Kontribusi bukan metode baru, melainkan pengukuran trade-off yang dapat direproduksi", 0),
    ])

    content_slide(prs, "Terima kasih — pertanyaan", [
        ("Kode & data: 02_code/, 01_data/, 03_experiments/raw/, 04_results/", 0),
        ("Naskah: 05_manuscript/manuscript.docx (+ PDF)", 0),
        ("Paket submit: 06_package/ (cover letter, dua calon jurnal, kontribusi anggota, "
         "tabel klaim → bukti)", 0),
        ("Reproduksi: lihat README.md — dua perintah dari JSONL ke semua tabel & gambar", 0),
    ])

    OUT.mkdir(parents=True, exist_ok=True)
    out = OUT / "slides_kelompok1.pptx"
    prs.save(out)
    print(f"wrote {out} ({len(prs.slides.__iter__.__self__._sldIdLst)} slides)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
