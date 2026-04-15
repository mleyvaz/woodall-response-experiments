# Woodall Response — Experiments

Code, data, and figures accompanying the two-part response to:

> Woodall, W. H., King, C., Driscoll, A. R., & Montgomery, D. C. (2025). *A critical assessment of neutrosophic statistics.*

**Authors:** Maikel Y. Leyva-Vázquez¹ and Florentin Smarandache²
¹ Universidad de Guayaquil, Ecuador · ² University of New Mexico, USA

## Companion papers

- **Part I — Theory:** *Clarifying the Layers of Neutrosophic Statistics — A Taxonomy and Publication Protocol*
- **Part II — Empirical:** *A Corrected Simulation and Extended Empirical Evidence*

## Repository layout

```
experiments/
  exp1_indeterminacy_reduction.py   # NS vs IS under 1,000 operations
  exp1_results.csv
  exp2_tif_independence.py          # T/I/F statistical independence vs interval counter-factual
  exp2_results.csv
  exp3_head_to_head.py              # Classical vs Interval vs Neutrosophic decisions
  exp3_results.csv
  exp4_uci_ns_benchmark.py          # 5 UCI datasets, NS zone-classification benchmark
  exp4_results.csv
  exp5_corrected_simulation.py      # Elasticity + zone classification (Part II, Section 2)
  exp5_results.json
figures/                            # All figures referenced in the two papers
```

## How to reproduce

```bash
python -m venv .venv
# Windows:   .venv\Scripts\activate
# macOS/Lin: source .venv/bin/activate
pip install -r requirements.txt

# Run each experiment individually
python experiments/exp1_indeterminacy_reduction.py
python experiments/exp2_tif_independence.py
python experiments/exp3_head_to_head.py
python experiments/exp4_uci_ns_benchmark.py
python experiments/exp5_corrected_simulation.py
```

Each script is self-contained, seeded (`random.seed(42)` / `np.random.seed(42)`), and writes its CSV/JSON output next to the script.

## Experiments summary

| # | File | Claim validated |
|---|------|-----------------|
| 1 | exp1_indeterminacy_reduction.py | NS intervals are 1.37–1.54× narrower than IS; IS never wins in 2,000 ops |
| 2 | exp2_tif_independence.py | Real T/I/F data has r ≈ 0; interval-disguised counter-factual forces r ≤ −0.6 |
| 3 | exp3_head_to_head.py | Zone classification produces different (and better-calibrated) decisions |
| 4 | exp4_uci_ns_benchmark.py | NS consensus accuracy + coverage across 5 UCI datasets |
| 5 | exp5_corrected_simulation.py | Elasticity (NS ≡ classical ANOVA at I=0) + zone shifts as I grows |

## License

MIT — see `LICENSE`.

## Citation

If you use this code, please cite both Part I and Part II.
