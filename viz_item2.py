# viz_item2.py
import argparse, csv
from pathlib import Path
import matplotlib.pyplot as plt

def density_tag(d):
    s = "{:.5f}".format(d).rstrip('0').rstrip('.')
    if s.startswith('.'): s = '0'+s
    return s.replace('.','p')

def read_summary(path):
    rows = []
    with open(path, newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            n = int(row["n"])
            d = float(row["density"])
            case = row["case"]
            if ":" not in case:  # ignora linhas ruins
                continue
            op, impl = case.split(":", 1)
            ms = float(row["ms"])
            rows.append({"n":n,"density":d,"op":op,"impl":impl,"ms":ms})
    return rows

def uniq(vals): return sorted(set(vals))
def ensure_dir(p: Path): p.mkdir(parents=True, exist_ok=True)

def pivot_vs_n(rows, op, density, impls, ns):
    out = {impl: [] for impl in impls}
    for n in ns:
        for impl in impls:
            ms = None
            for r in rows:
                if r["op"]==op and r["impl"]==impl and r["n"]==n and abs(r["density"]-density)<1e-12:
                    ms = r["ms"]; break
            out[impl].append(ms)
    return out

def pivot_vs_density(rows, op, n, impls, dens):
    out = {impl: [] for impl in impls}
    for d in dens:
        for impl in impls:
            ms = None
            for r in rows:
                if r["op"]==op and r["impl"]==impl and r["n"]==n and abs(r["density"]-d)<1e-12:
                    ms = r["ms"]; break
            out[impl].append(ms)
    return out

def save_csv(path: Path, header, rows):
    with open(path, "w", newline="") as f:
        import csv; w = csv.writer(f); w.writerow(header); w.writerows(rows)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--summary", default="results/summary.csv")
    ap.add_argument("--out_figs", default="results/figs_item2")
    ap.add_argument("--out_tables", default="results/tables_item2")
    args = ap.parse_args()

    rows = read_summary(args.summary)
    if not rows: print("summary.csv vazio?"); return

    impls = uniq(r["impl"] for r in rows)     # ['dense','dict','tree'] etc.
    ops   = uniq(r["op"]   for r in rows)     # ['add','matmul','scale']
    ns    = sorted(uniq(r["n"] for r in rows))
    dens  = sorted(uniq(r["density"] for r in rows))

    out_figs   = Path(args.out_figs);   ensure_dir(out_figs)
    out_tables = Path(args.out_tables); ensure_dir(out_tables)

    # tabela "explodida"
    save_csv(out_tables/"summary_split.csv",
             ["n","density","op","impl","ms"],
             [[r["n"], r["density"], r["op"], r["impl"], r["ms"]] for r in rows])

    # 1) tempo vs n (fixando densidade) — uma figura por (op, densidade)
    for op in ops:
        for d in dens:
            piv = pivot_vs_n(rows, op, d, impls, ns)
            # tabela
            tpath = out_tables / f"pivot_{op}_d{density_tag(d)}_vs_n.csv"
            tbl = [["n"] + list(impls)]
            for k, n in enumerate(ns):
                tbl.append([n] + [piv[impl][k] for impl in impls])
            save_csv(tpath, tbl[0], tbl[1:])

            # gráfico
            import matplotlib.pyplot as plt
            plt.figure()
            for impl in impls:
                plt.plot(ns, piv[impl], marker="o", label=impl)
            plt.title(f"{op} — tempo vs n (densidade={d})")
            plt.xlabel("n"); plt.ylabel("ms"); plt.legend(); plt.tight_layout()
            fpath = out_figs / f"time_vs_n_{op}_d{density_tag(d)}.png"
            plt.savefig(fpath, dpi=160); plt.close()

    # 2) tempo vs densidade (fixando n) — uma figura por (op, n)
    for op in ops:
        for n in ns:
            piv = pivot_vs_density(rows, op, n, impls, dens)
            # tabela
            tpath = out_tables / f"pivot_{op}_n{n}_vs_density.csv"
            tbl = [["density"] + list(impls)]
            for k, d in enumerate(dens):
                tbl.append([d] + [piv[impl][k] for impl in impls])
            save_csv(tpath, tbl[0], tbl[1:])

            # gráfico
            plt.figure()
            for impl in impls:
                plt.plot(dens, piv[impl], marker="o", label=impl)
            plt.title(f"{op} — tempo vs densidade (n={n})")
            plt.xlabel("densidade"); plt.ylabel("ms"); plt.legend(); plt.tight_layout()
            fpath = out_figs / f"time_vs_density_{op}_n{n}.png"
            plt.savefig(fpath, dpi=160); plt.close()

if __name__ == "__main__":
    main()
