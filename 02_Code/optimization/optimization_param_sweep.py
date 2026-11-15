"""
Parameter-sweep experiments for the project's feature-weight optimization.

Mirrors 02_Code/optimization/optimization.py (same pseudo-anomaly rule, same
objective = -AUROC on abs-normalised weights, same SLSQP / CG / L-BFGS-B setup,
same start w0 = 1/7) but exposes the parameters so each can be varied ONE AT A
TIME. Selection metric = synthetic AUROC (train only). Test AUROC is recorded
for reporting only.

Experiments (IDs are new, choose your own naming if you prefer):
  OPT-P1  finite-difference step  eps      (default scipy 1.49e-8)
  OPT-P2  pseudo-anomaly strength noise_scale (default 3.0)
  OPT-P3  starting point x0                (default equal weights)
  OPT-P4  max iterations maxiter           (default 500)
  OPT-P5  lower bound on each weight       (default 0.01)

Run:  python optimization_param_sweep.py --results-dir <03_Results> --out sweep.csv
"""
import argparse, os, sys
import numpy as np, pandas as pd
from scipy.optimize import minimize
from scipy.stats import rankdata

FEATURES = ["pixel_difference", "ssim", "color_difference", "edge_difference",
            "texture_difference", "frequency_difference", "defect_area"]
CATS = ["bottle", "cable", "capsule", "carpet", "grid", "hazelnut", "leather",
        "metal_nut", "screw", "tile", "toothbrush", "transistor"]
D = len(FEATURES)
DEFAULTS = dict(method="SLSQP", eps=None, noise_scale=3.0, x0="equal", maxiter=500, lb=0.01)


def fast_auc(neg, pos):
    r = rankdata(np.concatenate([neg, pos]))
    n0, n1 = len(neg), len(pos)
    return (r[n0:].sum() - n1 * (n1 + 1) / 2) / (n0 * n1)


def load(results_dir, cat):
    d = os.path.join(results_dir, cat, "features")
    tr = pd.read_csv(os.path.join(d, "improved_train_features_mean.csv"))
    te = pd.read_csv(os.path.join(d, "improved_test_features_mean.csv"))
    return tr, te


def pseudo_anomalies(tr, noise_scale, seed=42):
    """Same rule as generate_pseudo_anomalies(): base row + |N(0, noise_scale*std)|;
    SSIM is lowered instead of raised."""
    rng = np.random.RandomState(seed)
    rows = []
    for _ in range(len(tr)):
        base = tr.iloc[rng.randint(len(tr))]
        row = {}
        for f in FEATURES:
            shift = abs(rng.normal(0, noise_scale * tr[f].std()))
            row[f] = max(0.0, base[f] - shift) if f == "ssim" else base[f] + shift
        rows.append(row)
    return pd.DataFrame(rows)


def to_z(df, tr):
    def m(x):
        a = x[FEATURES].copy(); a["ssim"] = 1.0 - a["ssim"]; return a.values.astype(float)
    t = m(tr); mu, sd = t.mean(0), t.std(0) + 1e-8      # np.std (ddof=0) as in baseline_detector
    return (m(df) - mu) / sd


def norm_w(w):
    w = np.abs(w); return w / (w.sum() + 1e-12)


def run_one(zn, za, zte, y, method, eps, x0, maxiter, lb):
    obj = lambda w: -fast_auc(zn @ norm_w(w), za @ norm_w(w))
    opts = {"maxiter": maxiter}
    if eps is not None:
        opts["eps"] = eps
    kw = dict(fun=obj, x0=x0.copy(), method=method, options=opts)
    if method == "SLSQP":
        kw["bounds"] = [(lb, 1.0)] * D
        kw["constraints"] = [{"type": "eq", "fun": lambda w: np.sum(np.abs(w)) - 1.0}]
    elif method == "L-BFGS-B":
        kw["bounds"] = [(lb, 1.0)] * D
    res = minimize(**kw)
    w = norm_w(res.x)
    w_eq = np.full(D, 1 / D)
    return dict(synth_auroc=-res.fun, test_auroc=fast_auc(zte[y == 0] @ w, zte[y == 1] @ w),
                moved_L1=float(np.abs(w - w_eq).sum()), n_iter=getattr(res, "nit", np.nan),
                n_fev=getattr(res, "nfev", np.nan), success=bool(res.success),
                max_w=float(w.max()), min_w=float(w.min()))


def experiments():
    """Yield (exp_id, param_name, param_value, config dict)."""
    for m in ["SLSQP", "CG", "L-BFGS-B"]:
        for e in [None, 1e-4, 1e-3, 1e-2, 5e-2, 1e-1]:
            yield "OPT-P1", "eps", "default" if e is None else e, {**DEFAULTS, "method": m, "eps": e}
    # remaining experiments use a finite-difference step that can see AUROC changes
    base = {**DEFAULTS, "eps": 1e-2}
    for ns in [0.5, 1.0, 2.0, 3.0, 5.0]:
        yield "OPT-P2", "noise_scale", ns, {**base, "noise_scale": ns}
    yield "OPT-P3", "x0", "equal", {**base, "x0": "equal"}
    for s in range(5):
        yield "OPT-P3", "x0", f"random_{s}", {**base, "x0": f"random_{s}"}
    for it in [1, 5, 20, 500]:
        yield "OPT-P4", "maxiter", it, {**base, "maxiter": it}
    for lb in [0.0, 0.01, 0.05, 0.10]:
        yield "OPT-P5", "lower_bound", lb, {**base, "lb": lb}


def main(results_dir, out):
    rows = []
    cache = {c: load(results_dir, c) for c in CATS}
    for cat in CATS:
        tr, te = cache[cat]
        y = (te["category"] != "good").astype(int).values
        zte = to_z(te, tr)
        for exp_id, pname, pval, cfg in experiments():
            za = to_z(pseudo_anomalies(tr, cfg["noise_scale"]), tr)
            zn = to_z(tr, tr)
            if cfg["x0"] == "equal":
                x0 = np.full(D, 1 / D)
            else:
                x0 = np.random.RandomState(int(cfg["x0"].split("_")[1])).dirichlet(np.ones(D))
            r = run_one(zn, za, zte, y, cfg["method"], cfg["eps"], x0, cfg["maxiter"], cfg["lb"])
            rows.append(dict(experiment_id=exp_id, category=cat, method=cfg["method"],
                             param=pname, value=pval, **r))
        print("done", cat, file=sys.stderr, flush=True)
    df = pd.DataFrame(rows); df.to_csv(out, index=False); return df


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--results-dir", required=True)
    ap.add_argument("--out", default="optimization_sweep_results.csv")
    a = ap.parse_args()
    df = main(a.results_dir, a.out)
    g = (df.groupby(["experiment_id", "method", "param", "value"], sort=False)
           [["synth_auroc", "test_auroc", "moved_L1", "n_iter"]].mean().round(4))
    print(g.to_string())
