
import argparse, sys
from lib.sparse_matrix import SparseMatrix
from lib.tree_matrix import TreeMatrix
from lib.dense_matrix import DenseMatrix

def load_sparse_from_file(path:str)->SparseMatrix:
    return SparseMatrix.load_from_file(path)

def to_dense_from_sparse(S: SparseMatrix)->DenseMatrix:
    r,c = S.rows, S.cols
    D = DenseMatrix(r,c)
    for i, row in S.data.items():
        for j, v in row.items():
            D.insert(i,j,v)
    return D

def to_tree_from_sparse(S: SparseMatrix)->TreeMatrix:
    T = TreeMatrix(S.rows, S.cols)
    for i, row in S.data.items():
        for j, v in row.items():
            T.insert(i,j,v)
    return T

def max_abs_diff(A,B)->float:
    rA,cA = A.shape; rB,cB = B.shape
    assert (rA,cA)==(rB,cB)
    n,m = rA,cA
    mx = 0.0
    for i in range(n):
        for j in range(m):
            da = A.access(i,j)
            db = B.access(i,j)
            d = abs(da-db)
            if d > mx: mx = d
    return mx

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--A", required=True)
    ap.add_argument("--B", required=True)
    ap.add_argument("--op", choices=["add","matmul"], required=True)
    ap.add_argument("--eps", type=float, default=1e-9)
    args = ap.parse_args()

    S = load_sparse_from_file(args.A)
    Q = load_sparse_from_file(args.B)
    D_A = to_dense_from_sparse(S)
    D_B = to_dense_from_sparse(Q)
    T_A = to_tree_from_sparse(S)
    T_B = to_tree_from_sparse(Q)

    if args.op=="add":
        Sd = D_A.add(D_B)
        St = T_A.add(T_B)
        Ss = S + Q
    else:
        Sd = D_A.matmul(D_B)
        St = T_A.matmul(T_B)
        Ss = S * Q

    # Compare
    md_st = max_abs_diff(Sd, St)
    md_ss = max_abs_diff(Sd, to_dense_from_sparse(Ss))
    print(f"max|dense - tree| = {md_st:.3e}")
    print(f"max|dense - dict| = {md_ss:.3e}")
    if md_st<=args.eps and md_ss<=args.eps:
        print("OK within tolerance.")
        return 0
    print("Mismatch above tolerance.")
    return 2

if __name__=="__main__":
    sys.exit(main())
