"""
Experiment 4: UCI Benchmark — Classical vs Interval vs Neutrosophic Statistics
For the Woodall response paper. Tests neutrosophic zone classification
(thirdanswer-style) on 5 UCI datasets.
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import numpy as np
from sklearn.datasets import load_iris, load_wine, load_breast_cancer, load_digits
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score
from scipy.stats import wilcoxon
import warnings
warnings.filterwarnings('ignore')

np.random.seed(42)

def classical_classify(y_prob):
    """Classical: single probability, binary decision at 0.5."""
    return (y_prob >= 0.5).astype(int)

def interval_classify(y_probs_bootstrap):
    """Interval: use bootstrap CI, classify based on whether CI contains 0.5."""
    lower = np.percentile(y_probs_bootstrap, 2.5, axis=0)
    upper = np.percentile(y_probs_bootstrap, 97.5, axis=0)
    # If CI contains 0.5, abstain (assign majority class)
    preds = np.where(lower > 0.5, 1, np.where(upper < 0.5, 0, -1))  # -1 = uncertain
    return preds, lower, upper

def neutrosophic_classify(y_prob, y_probs_bootstrap):
    """Neutrosophic: compute T, I, F and classify by zone."""
    n = len(y_prob)
    T = np.abs(2 * y_prob - 1)  # distance from 0.5, normalized

    # I from bootstrap spread
    std_boot = np.std(y_probs_bootstrap, axis=0)
    I = np.minimum(1.0, std_boot / 0.25)  # normalized by typical spread

    # F from contradiction: how much bootstrap samples disagree with point estimate
    boot_class = (y_probs_bootstrap >= 0.5).astype(float)
    point_class = (y_prob >= 0.5).astype(float)
    disagree_rate = np.mean(np.abs(boot_class - point_class[np.newaxis, :]), axis=0)
    F = disagree_rate

    # Zone classification
    zones = []
    preds = []
    for j in range(n):
        t, i, f = T[j], I[j], F[j]
        C = max(0, t - i - f)

        if t > 0.5 and i < 0.35 and f < 0.3:
            zone = "Consensus"
            pred = 1 if y_prob[j] >= 0.5 else 0
        elif i >= 0.35:
            zone = "Ambiguity"
            pred = 1 if y_prob[j] >= 0.5 else 0  # predict but flag
        elif t > 0.3 and f > 0.3:
            zone = "Contradiction"
            pred = 1 if y_prob[j] >= 0.5 else 0
        else:
            zone = "Ignorance"
            pred = 1 if y_prob[j] >= 0.5 else 0

        zones.append(zone)
        preds.append(pred)

    return np.array(preds), T, I, F, zones

def run_dataset(name, X, y, n_splits=5, n_bootstrap=20):
    """Run 5-fold CV comparing 3 methods on a binary dataset."""
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
    scaler = StandardScaler()

    classical_accs = []
    interval_accs = []
    ns_accs = []
    ns_consensus_accs = []
    paraconsistent_counts = []
    zone_counts = {"Consensus": 0, "Ambiguity": 0, "Contradiction": 0, "Ignorance": 0}
    total_n = 0

    for train_idx, test_idx in skf.split(X, y):
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]

        X_train_s = scaler.fit_transform(X_train)
        X_test_s = scaler.transform(X_test)

        # Train base classifier
        clf = LogisticRegression(max_iter=1000, random_state=42)
        clf.fit(X_train_s, y_train)
        y_prob = clf.predict_proba(X_test_s)[:, 1]

        # Bootstrap
        boot_probs = []
        for b in range(n_bootstrap):
            idx = np.random.choice(len(X_train_s), len(X_train_s), replace=True)
            clf_b = LogisticRegression(max_iter=1000, random_state=42+b)
            clf_b.fit(X_train_s[idx], y_train[idx])
            boot_probs.append(clf_b.predict_proba(X_test_s)[:, 1])
        boot_probs = np.array(boot_probs)

        # Classical
        y_classical = classical_classify(y_prob)
        classical_accs.append(accuracy_score(y_test, y_classical))

        # Interval
        y_interval, lower, upper = interval_classify(boot_probs)
        # Replace uncertain (-1) with majority class
        majority = int(y_train.mean() >= 0.5)
        y_interval_filled = np.where(y_interval == -1, majority, y_interval)
        interval_accs.append(accuracy_score(y_test, y_interval_filled))

        # Neutrosophic
        y_ns, T, I, F, zones = neutrosophic_classify(y_prob, boot_probs)
        ns_accs.append(accuracy_score(y_test, y_ns))

        # Consensus-only accuracy (predict only on Consensus zone)
        consensus_mask = np.array([z == "Consensus" for z in zones])
        if consensus_mask.sum() > 0:
            ns_consensus_accs.append(accuracy_score(y_test[consensus_mask], y_ns[consensus_mask]))

        # Paraconsistent cases (T + F > 1)
        paraconsistent = np.sum((T + F) > 1.0)
        paraconsistent_counts.append(paraconsistent)

        # Zone distribution
        for z in zones:
            zone_counts[z] += 1
        total_n += len(y_test)

    # Wilcoxon: NS vs Classical
    try:
        stat, p_val = wilcoxon(ns_accs, classical_accs)
    except:
        p_val = 1.0

    consensus_acc = np.mean(ns_consensus_accs) if ns_consensus_accs else 0
    coverage = zone_counts["Consensus"] / total_n if total_n > 0 else 0

    return {
        "name": name,
        "n": len(y),
        "classical_acc": np.mean(classical_accs),
        "interval_acc": np.mean(interval_accs),
        "ns_acc": np.mean(ns_accs),
        "ns_consensus_acc": consensus_acc,
        "coverage": coverage,
        "wilcoxon_p": p_val,
        "paraconsistent": sum(paraconsistent_counts),
        "total_points": total_n,
        "zones": zone_counts,
    }

# ============================================================
# RUN ALL 5 DATASETS
# ============================================================

print("Experiment 4: UCI Benchmark — Classical vs Interval vs Neutrosophic")
print("=" * 90)

results = []

# 1. Iris (binary: setosa vs rest)
print("Running Iris (setosa vs rest)...")
iris = load_iris()
y_iris = (iris.target == 0).astype(int)
results.append(run_dataset("Iris (setosa vs rest)", iris.data, y_iris))

# 2. Wine (class 1 vs rest)
print("Running Wine (class 1 vs rest)...")
wine = load_wine()
y_wine = (wine.target == 1).astype(int)
results.append(run_dataset("Wine (cl.1 vs rest)", wine.data, y_wine))

# 3. Breast Cancer
print("Running Breast Cancer...")
bc = load_breast_cancer()
results.append(run_dataset("Breast Cancer", bc.data, bc.target))

# 4. Digits (even vs odd)
print("Running Digits (even vs odd)...")
digits = load_digits()
y_digits = (digits.target % 2 == 0).astype(int)
results.append(run_dataset("Digits (even/odd)", digits.data, y_digits))

# 5. Wine (class 0 vs rest — easy, negative control)
print("Running Wine (class 0 vs rest — negative control)...")
y_wine0 = (wine.target == 0).astype(int)
results.append(run_dataset("Wine (cl.0, neg ctrl)", wine.data, y_wine0))

# ============================================================
# PRINT RESULTS TABLE
# ============================================================

print(f"\n{'='*90}")
print(f"Table 4. UCI Benchmark: Classical vs Interval vs Neutrosophic (5-fold CV, seed=42)")
print(f"{'='*90}")
print(f"{'Dataset':<22} {'n':>5} {'Classical':>10} {'Interval':>10} {'NS All':>8} {'NS Cons.':>9} {'Cover%':>7} {'Wilcox p':>9} {'T+F>1':>6}")
print("-"*90)
for r in results:
    print(f"{r['name']:<22} {r['n']:>5} {r['classical_acc']:>10.4f} {r['interval_acc']:>10.4f} {r['ns_acc']:>8.4f} {r['ns_consensus_acc']:>9.4f} {r['coverage']*100:>6.1f}% {r['wilcoxon_p']:>9.4f} {r['paraconsistent']:>6}")
print("-"*90)

# Zone distribution summary
print(f"\nZone Distribution (all datasets combined):")
total_zones = {"Consensus": 0, "Ambiguity": 0, "Contradiction": 0, "Ignorance": 0}
total_pts = 0
for r in results:
    for z, c in r["zones"].items():
        total_zones[z] += c
    total_pts += r["total_points"]
for z, c in total_zones.items():
    print(f"  {z}: {c} ({100*c/total_pts:.1f}%)")

# Save CSV
import csv
with open('exp4_results.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=["name","n","classical_acc","interval_acc","ns_acc","ns_consensus_acc","coverage","wilcoxon_p","paraconsistent"])
    w.writeheader()
    for r in results:
        w.writerow({k: r[k] for k in w.fieldnames})

print(f"\nSaved: exp4_results.csv")
