# Numbers sheet — main

Sumber: `04_results/tables/main_*.csv` (dari `03_experiments/raw/main.jsonl`).

## 1. Karakteristik instance

| Instance | Sessions | Rooms | Slots | Room fill | Pattern |
|---|---|---|---|---|---|
| comp01 | 160 | 6 | 30 | 0.889 | benchmark |
| comp02 | 283 | 16 | 25 | 0.708 | benchmark |
| comp03 | 251 | 16 | 25 | 0.627 | benchmark |
| comp04 | 286 | 18 | 25 | 0.636 | benchmark |
| comp05 | 152 | 9 | 36 | 0.469 | benchmark |
| comp06 | 361 | 18 | 25 | 0.802 | benchmark |
| comp07 | 434 | 20 | 25 | 0.868 | benchmark |
| comp08 | 324 | 18 | 25 | 0.720 | benchmark |
| comp09 | 279 | 18 | 25 | 0.620 | benchmark |
| comp10 | 370 | 18 | 25 | 0.822 | benchmark |
| comp11 | 162 | 5 | 45 | 0.720 | benchmark |
| comp12 | 218 | 11 | 36 | 0.550 | benchmark |
| syn30A | 30 | 2 | 30 | 0.500 | A |
| syn30B | 30 | 2 | 30 | 0.500 | B |
| syn30C | 30 | 2 | 30 | 0.500 | C |
| syn60A | 60 | 4 | 30 | 0.500 | A |
| syn60B | 60 | 4 | 30 | 0.500 | B |
| syn60C | 60 | 4 | 30 | 0.500 | C |
| syn90A | 90 | 6 | 30 | 0.500 | A |
| syn90B | 90 | 6 | 30 | 0.500 | B |
| syn90C | 90 | 6 | 30 | 0.500 | C |

## 2. Kinerja per metode (21 instance test)

| Method | Feasible instances | Median H | Mean H | Median P | Median gens | Median runtime (s) | Repair share |
|---|---|---|---|---|---|---|---|
| GA-R | 19/21 | 0.00 | 0.42 | 63.00 | 68.00 | 8.60 | 0.669 |
| GA | 10/21 | 1.00 | 4.42 | 95.00 | 208.00 | 4.35 | 0.000 |
| Greedy | 9/21 | 11.00 | 13.62 | 38.00 | 0.00 | 0.05 | 0.000 |

## 3. Median hard violations per pola ketersediaan

| Pattern | Greedy | GA | GA-R |
|---|---|---|---|
| A | 0.00 | 0.00 | 0.00 |
| B | 0.00 | 0.00 | 0.00 |
| C | 0.00 | 0.00 | 0.00 |
| benchmark | 24.00 | 7.00 | 0.00 |

## 4. Median penalti preferensi (P) per pola

| Pattern | Greedy | GA | GA-R |
|---|---|---|---|
| A | 23.00 | 0.00 | 0.00 |
| B | 24.00 | 2.00 | 0.00 |
| C | 17.00 | 4.50 | 0.00 |
| benchmark | 86.50 | 171.00 | 106.50 |

## 5. Uji statistik

| Test | Metric | Comparison | n | statistic | p | p (Holm) | Cliff's delta | Effect |
|---|---|---|---|---|---|---|---|---|
| wilcoxon_paired | H | ga_repair_vs_ga_std | 21 | 0.000 | 0.0033 | 0.0033 | -1.000 | large |
| wilcoxon_paired | P | ga_repair_vs_ga_std | 21 | 0.000 | 0.0003 | 0.0003 | -1.000 | large |
| friedman | H | greedy+ga_std+ga_repair | 21 | 23.532 | 0.0000 | 0.0000 | – | nan |
| friedman | P | greedy+ga_std+ga_repair | 21 | 10.468 | 0.0053 | 0.0053 | – | nan |
| posthoc_wilcoxon_holm | H | ga_std_vs_greedy | 21 | – | 0.0022 | 0.0066 | -1.000 | large |
| posthoc_wilcoxon_holm | H | ga_repair_vs_greedy | 21 | – | 0.0022 | 0.0066 | -1.000 | large |
| posthoc_wilcoxon_holm | H | ga_repair_vs_ga_std | 21 | – | 0.0033 | 0.0066 | -1.000 | large |
| mcnemar_exact | feasible | ga_repair_vs_ga_std | 9 | 9.000 | 0.0039 | 0.0039 | – | nan |

## 6. Rincian per instance

| Instance | Pattern | n | GA med H | GA feasible | GA-R med H | GA-R feasible | GA med P | GA-R med P | GA gens | GA-R gens | GA-R repair share |
|---|---|---|---|---|---|---|---|---|---|---|---|
| comp01 | benchmark | 160 | 9.00 | 0.00 | 4.00 | 0.00 | 36.50 | 25.00 | 208.00 | 80.00 | 0.615 |
| comp02 | benchmark | 283 | 9.00 | 0.00 | 0.00 | 0.70 | 180.50 | 121.50 | 208.00 | 57.00 | 0.724 |
| comp03 | benchmark | 251 | 3.00 | 0.00 | 0.00 | 0.85 | 161.50 | 91.50 | 208.00 | 54.00 | 0.740 |
| comp04 | benchmark | 286 | 1.00 | 0.10 | 0.00 | 1.00 | 108.50 | 63.00 | 208.00 | 50.00 | 0.757 |
| comp05 | benchmark | 152 | 10.00 | 0.00 | 3.00 | 0.00 | 480.50 | 361.00 | 208.00 | 84.00 | 0.595 |
| comp06 | benchmark | 361 | 15.00 | 0.00 | 0.00 | 0.90 | 196.50 | 166.00 | 208.00 | 54.00 | 0.737 |
| comp07 | benchmark | 434 | 24.00 | 0.00 | 0.00 | 0.70 | 213.50 | 200.50 | 208.00 | 61.00 | 0.703 |
| comp08 | benchmark | 324 | 4.00 | 0.00 | 0.00 | 1.00 | 122.00 | 70.50 | 208.00 | 49.50 | 0.760 |
| comp09 | benchmark | 279 | 0.00 | 0.75 | 0.00 | 1.00 | 138.50 | 70.00 | 208.00 | 54.00 | 0.739 |
| comp10 | benchmark | 370 | 9.00 | 0.00 | 0.00 | 1.00 | 181.00 | 135.00 | 208.00 | 51.00 | 0.753 |
| comp11 | benchmark | 162 | 5.00 | 0.00 | 0.00 | 1.00 | 95.00 | 77.00 | 208.00 | 51.00 | 0.754 |
| comp12 | benchmark | 218 | 5.00 | 0.00 | 0.50 | 0.50 | 463.00 | 272.50 | 208.00 | 62.50 | 0.696 |
| syn30A | A | 30 | 0.00 | 1.00 | 0.00 | 1.00 | 0.00 | 0.00 | 208.00 | 84.00 | 0.595 |
| syn30B | B | 30 | 0.00 | 1.00 | 0.00 | 1.00 | 0.00 | 0.00 | 208.00 | 78.50 | 0.620 |
| syn30C | C | 30 | 0.00 | 1.00 | 0.00 | 1.00 | 0.00 | 0.00 | 208.00 | 91.00 | 0.559 |
| syn60A | A | 60 | 0.00 | 1.00 | 0.00 | 1.00 | 0.00 | 0.00 | 208.00 | 78.00 | 0.625 |
| syn60B | B | 60 | 0.00 | 1.00 | 0.00 | 1.00 | 2.00 | 0.00 | 208.00 | 76.00 | 0.631 |
| syn60C | C | 60 | 0.00 | 1.00 | 0.00 | 1.00 | 4.50 | 0.00 | 208.00 | 79.00 | 0.620 |
| syn90A | A | 90 | 0.00 | 1.00 | 0.00 | 1.00 | 2.00 | 0.00 | 208.00 | 68.00 | 0.669 |
| syn90B | B | 90 | 0.00 | 1.00 | 0.00 | 1.00 | 3.50 | 0.00 | 208.00 | 74.00 | 0.641 |
| syn90C | C | 90 | 0.00 | 1.00 | 0.00 | 1.00 | 15.00 | 1.00 | 208.00 | 72.00 | 0.651 |
