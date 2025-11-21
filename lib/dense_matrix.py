
from typing import Iterable, Tuple, List

class DenseMatrix:
    def __init__(self, rows:int, cols:int):
        if rows<=0 or cols<=0: raise ValueError("invalid shape")
        self.rows = rows
        self.cols = cols
        self._t = False
        self.a = [[0.0 for _ in range(cols)] for __ in range(rows)]

    @property
    def shape(self): return (self.cols, self.rows) if self._t else (self.rows, self.cols)

    def _norm(self, i:int,j:int) -> Tuple[int,int]:
        if self._t: i,j = j,i
        r,c = self.rows, self.cols
        if not (0<=i<r and 0<=j<c): raise IndexError("oob")
        return i,j

    def access(self, i:int, j:int) -> float:
        i,j = self._norm(i,j)
        return self.a[i][j]

    def insert(self, i:int, j:int, v:float) -> None:
        i,j = self._norm(i,j)
        self.a[i][j] = v

    def transpose(self):
        self._t = not self._t
        self.rows, self.cols = self.cols, self.rows

    def items(self) -> Iterable[Tuple[int,int,float]]:
        r,c = self.shape
        for i in range(r):
            for j in range(c):
                v = self.access(i,j)
                if v != 0.0:
                    yield i,j,v

    def add(self, other:"DenseMatrix")->"DenseMatrix":
        r,c = self.shape
        if other.shape != (r,c): raise ValueError("shape mismatch on add")
        R = DenseMatrix(r,c)
        for i in range(r):
            for j in range(c):
                R.insert(i,j, self.access(i,j)+other.access(i,j))
        return R

    def scale(self, a:float)->"DenseMatrix":
        r,c = self.shape
        R = DenseMatrix(r,c)
        for i in range(r):
            for j in range(c):
                R.insert(i,j, a*self.access(i,j))
        return R

    def matmul(self, other:"DenseMatrix")->"DenseMatrix":
        nA,mA = self.shape
        nB,mB = other.shape
        if mA != nB: raise ValueError("shape mismatch on matmul")
        R = DenseMatrix(nA, mB)
        # simple triple loop (ok for small sizes / verification)
        for i in range(nA):
            for t in range(mA):
                a = self.access(i,t)
                if a == 0.0: continue
                for j in range(mB):
                    R.insert(i,j, R.access(i,j) + a*other.access(t,j))
        return R
