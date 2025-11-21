
import argparse, time, csv, random
from lib.sparse_matrix import SparseMatrix
from lib.tree_matrix import TreeMatrix
from lib.dense_matrix import DenseMatrix

def gen_sparse(rows, cols, density, seed=42):
    random.seed(seed)
    k = int(rows*cols*density)
    S = SparseMatrix(rows, cols)
    seen = set()
    while len(seen) < k:
        i = random.randrange(rows); j = random.randrange(cols)
        if (i,j) in seen: continue
        seen.add((i,j))
        v = random.uniform(-1,1)
        if v==0.0: v = 0.5
        S.insert(i,j,v)
    return S

def timeit(fn, repeat=1):
    best = float("inf")
    for _ in range(repeat):
        t0 = time.perf_counter()
        fn()
        t1 = time.perf_counter()
        best = min(best, (t1-t0)*1000.0)
    return best

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=1000)
    ap.add_argument("--density", type=float, default=0.01)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--repeat", type=int, default=3)
    ap.add_argument("--out", default="results.csv")
    args = ap.parse_args()

    A = gen_sparse(args.n, args.n, args.density, args.seed)
    B = gen_sparse(args.n, args.n, args.density, args.seed+1)

    # Materialize others
    D_A = DenseMatrix(args.n, args.n);  [D_A.insert(i,j,v) for i,row in A.data.items() for j,v in row.items()]
    D_B = DenseMatrix(args.n, args.n);  [D_B.insert(i,j,v) for i,row in B.data.items() for j,v in row.items()]
    T_A = TreeMatrix(args.n, args.n);   [T_A.insert(i,j,v) for i,row in A.data.items() for j,v in row.items()]
    T_B = TreeMatrix(args.n, args.n);   [T_B.insert(i,j,v) for i,row in B.data.items() for j,v in row.items()]

    rows = []
    # add
    rows.append(("add:dict",   timeit(lambda: A + B, args.repeat)))
    rows.append(("add:tree",   timeit(lambda: T_A.add(T_B), args.repeat)))
    rows.append(("add:dense",  timeit(lambda: D_A.add(D_B), args.repeat)))
    # scale
    rows.append(("scale:dict",  timeit(lambda: A*2.0, args.repeat)))
    rows.append(("scale:tree",  timeit(lambda: T_A.scale(2.0), args.repeat)))
    rows.append(("scale:dense", timeit(lambda: D_A.scale(2.0), args.repeat)))
    # matmul
    rows.append(("matmul:dict",  timeit(lambda: A*B, args.repeat)))
    rows.append(("matmul:tree",  timeit(lambda: T_A.matmul(T_B), args.repeat)))
    rows.append(("matmul:dense", timeit(lambda: D_A.matmul(D_B), 1)))  # denso custa caro; 1 repetição

    with open(args.out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["case","ms"])
        for r in rows:
            w.writerow(r)
    print(f"Saved {args.out}")

if __name__=="__main__":
    main()
