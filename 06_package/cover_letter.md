# Draft cover letter

**To:** Editor-in-Chief, *Journal of Heuristics* (Springer)
**Subject:** Submission of "Repair-Based Genetic Algorithm for Course Timetabling under Lecturer Availability Constraints"

Dear Editor-in-Chief,

We submit the manuscript "Repair-Based Genetic Algorithm for Course Timetabling
under Lecturer Availability Constraints" for consideration as an original
research article in *Journal of Heuristics*.

**What the paper reports.** The paper asks a narrow, measurable question: at an
identical budget of 10,000 objective evaluations, does repairing hard-constraint
violations after crossover and mutation help a genetic algorithm find feasible
course timetables, and what does that repair cost? We compare deterministic
greedy construction, a standard GA, and the same GA augmented with a repair
operator that relocates violating sessions to valid room–slot pairs with the
smallest added preference penalty. Every candidate examined by repair is charged
to the evaluation budget, so the comparison is budget-matched rather than
generation-matched.

**Main findings.** Repair increased the number of test instances on which a
feasible timetable was found in a majority of seeds from 10 to 19 out of 21, and
the number of feasible runs on twelve public ITC2007 benchmark instances from 17
to 173 out of 240, at the price of about two thirds of the evaluation budget and
a threefold reduction in completed generations. On a controlled synthetic ladder
where feasibility was easy, repair did not change feasibility but improved the
preference penalty. The contrast between the two families is itself a result:
the discriminating factor is room occupancy combined with availability, not the
availability percentage alone. We report the ladder as a negative result for our
own hypothesis rather than omitting it.

**Why it fits *Journal of Heuristics*.** The work is an empirical study of
heuristic search with a stated hypothesis, statistical testing with effect sizes
and Holm correction, and a released test suite — the three things the journal's
aims and scope ask of empirical submissions. The contribution is deliberately
not a new evolutionary framework; it is a measurement of a widely used device
(constraint repair) under a cost model that is usually left implicit.

**Data and code availability.** The released package contains the generator and
its seeds, all instance files (including the public benchmark copies with
attribution and licence notes), the design-lock document written before the test
instances were evaluated, the per-run JSONL records of every experiment (pilot,
main, ablation), the analysis scripts that regenerate every table and figure, and
the manuscript sources. Two commands reproduce all reported numbers from the raw
records.

**Declarations.** The manuscript is original, is not under consideration
elsewhere, and has not been published previously. All four authors have approved
the submitted version. Author contributions and competing interests are declared
in the submission system and in `06_package/member_contributions.md`. The study
did not involve human participants or personal data; the timetable instances are
either synthetic or public benchmark data.

We would be glad to provide any further material the editorial office requires.

Yours sincerely,

Slamet Riyadi (corresponding author), on behalf of Muhammad Adi Agum, Akbar Tri
Wicaksono, and I Ketut Divta Suryawan
Study Program of Information Technology (S2), Postgraduate Program
Kecerdasan Komputasional — 2026

---

## Catatan untuk user (bukan bagian surat)

- Nama jurnal, sapaan, dan isi paragraf kesesuaian sudah disesuaikan dengan
  halaman resmi *Journal of Heuristics* yang diperiksa 2026-10-29
  (`06_package/journal_candidates.md`).
- Ganti "Editor-in-Chief" dengan nama editor yang tercantum pada halaman jurnal
  saat submit; kami tidak mencantumkan nama karena tidak diverifikasi pada hari
  yang sama.
- Bila dosen memilih *Journal of Scheduling* sebagai target, tukar paragraf
  "Why it fits" dengan paragraf kesesuaian penjadwalan dan ganti baris "To:".
- Submisi hanya ke satu jurnal pada satu waktu, setelah persetujuan dosen.
