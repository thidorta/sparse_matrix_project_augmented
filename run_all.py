
import argparse, subprocess, os, csv, sys
from pathlib import Path

def run_one(n:int, density:str, repeat:int, seed:int, out_root:Path):
    dtag = density.replace(".","p")
    out_dir = out_root / f"n{n}" / f"d{dtag}"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_csv = out_dir / "bench.csv"
    print(f"[bench] n={n} d={density} -> {out_csv}")
    cmd = [sys.executable, "bench.py", "--n", str(n), "--density", density, "--repeat", str(repeat), "--seed", str(seed), "--out", str(out_csv)]
    subprocess.run(cmd, check=True)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sizes", nargs="+", type=int, default=[200,500,1000])
    ap.add_argument("--densities", nargs="+", default=["0.01","0.05","0.10","0.20"])
    ap.add_argument("--repeat", type=int, default=3)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--out", default="results")
    args = ap.parse_args()

    out_root = Path(args.out)
    out_root.mkdir(parents=True, exist_ok=True)

    for n in args.sizes:
        for d in args.densities:
            run_one(n, d, args.repeat, args.seed, out_root)

    summary = out_root / "summary.csv"
    with open(summary, "w", newline="") as fsum:
        w = csv.writer(fsum)
        w.writerow(["n","density","case","ms"])
        for n_dir in sorted(out_root.glob("n*")):
            if not n_dir.is_dir(): continue
            n = int(n_dir.name[1:])
            for d_dir in sorted(n_dir.glob("d*")):
                if not d_dir.is_dir(): continue
                dens = d_dir.name[1:].replace("p",".")
                if dens[0] != "0": dens = "0."+dens
                bench_csv = d_dir / "bench.csv"
                if not bench_csv.exists(): continue
                with open(bench_csv, newline="") as fb:
                    r = csv.DictReader(fb)
                    for row in r:
                        w.writerow([n, dens, row["case"], row["ms"]])
    print(f"[done] summary -> {summary}")

if __name__ == "__main__":
    main()
