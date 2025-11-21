
import csv, sys, pathlib
import matplotlib.pyplot as plt

def main(summary_path="results/summary.csv"):
    p = pathlib.Path(summary_path)
    if not p.exists():
        print("summary.csv não encontrado:", p)
        return
    rows = []
    with open(p, newline="") as f:
        r = csv.DictReader(f)
        rows = list(r)
    by_key = {}
    for row in rows:
        key = (int(row["n"]), row["density"])
        by_key.setdefault(key, []).append(row)
    outdir = p.parent / "figs"
    outdir.mkdir(exist_ok=True, parents=True)
    for (n,d), items in sorted(by_key.items()):
        cases = [r["case"] for r in items]
        ms    = [float(r["ms"]) for r in items]
        plt.figure()
        plt.bar(cases, ms)
        plt.title(f"n={n} density={d}")
        plt.xticks(rotation=45, ha="right")
        plt.ylabel("ms")
        plt.tight_layout()
        out = outdir / f"n{n}_d{str(d).replace('.','p')}.png"
        plt.savefig(out, dpi=160)
        plt.close()
        print("plot ->", out)

if __name__=="__main__":
    if len(sys.argv)>1:
        main(sys.argv[1])
    else:
        main()
