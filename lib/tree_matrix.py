
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Tuple, Iterable, List

Key = Tuple[int,int]

@dataclass
class _Node:
    key: Key
    val: float
    lh: Optional["_Node"]=None
    rh: Optional["_Node"]=None
    h: int=1

def _h(x: Optional[_Node]) -> int:
    return x.h if x is not None else 0

def _upd(x: _Node) -> None:
    x.h = 1 + max(_h(x.lh), _h(x.rh))

def _bf(x: _Node) -> int:
    return _h(x.lh) - _h(x.rh)

def _rotR(y: _Node) -> _Node:
    x = y.lh;  assert x is not None
    T2 = x.rh
    x.rh = y
    y.lh = T2
    _upd(y); _upd(x)
    return x

def _rotL(x: _Node) -> _Node:
    y = x.rh;  assert y is not None
    T2 = y.lh
    y.lh = x
    x.rh = T2
    _upd(x); _upd(y)
    return y

def _min_node(x: _Node) -> _Node:
    while x.lh is not None:
        x = x.lh
    return x

def _cmp(a: Key, b: Key) -> int:
    # lexicographic compare
    if a[0] != b[0]:
        return -1 if a[0] < b[0] else 1
    if a[1] != b[1]:
        return -1 if a[1] < b[1] else 1
    return 0

def _insert(x: Optional[_Node], key: Key, val: float) -> _Node:
    if x is None:
        return _Node(key, val)
    c = _cmp(key, x.key)
    if c == 0:
        x.val = val
        return x
    elif c < 0:
        x.lh = _insert(x.lh, key, val)
    else:
        x.rh = _insert(x.rh, key, val)
    _upd(x)
    bf = _bf(x)
    if bf > 1:
        # LL ou LR
        if _cmp(key, x.lh.key) < 0:
            return _rotR(x)            # LL
        else:
            x.lh = _rotL(x.lh)         # LR
            return _rotR(x)
    if bf < -1:
        # RR ou RL
        if _cmp(key, x.rh.key) > 0:
            return _rotL(x)            # RR
        else:
            x.rh = _rotR(x.rh)         # RL  (<<< AQUI era o erro)
            return _rotL(x)
    return x

def _delete(x: Optional[_Node], key: Key) -> Optional[_Node]:
    if x is None: return None
    c = _cmp(key, x.key)
    if c < 0:
        x.lh = _delete(x.lh, key)
    elif c > 0:
        x.rh = _delete(x.rh, key)
    else:
        # delete this
        if x.lh is None or x.rh is None:
            x = x.lh if x.lh is not None else x.rh
        else:
            succ = _min_node(x.rh)
            x.key, x.val = succ.key, succ.val
            x.rh = _delete(x.rh, succ.key)
    if x is None: return None
    _upd(x)
    bf = _bf(x)
    # LL
    if bf > 1 and _bf(x.lh) >= 0: return _rotR(x)
    # LR
    if bf > 1 and _bf(x.lh) < 0:  x.lh = _rotL(x.lh); return _rotR(x)
    # RR
    if bf < -1 and _bf(x.rh) <= 0: return _rotL(x)
    # RL
    if bf < -1 and _bf(x.rh) > 0:  x.rh = _rotR(x.rh); return _rotL(x)
    return x

def _find(x: Optional[_Node], key: Key) -> Optional[_Node]:
    while x is not None:
        c = _cmp(key, x.key)
        if c == 0: return x
        x = x.lh if c < 0 else x.rh
    return None

def _lower_bound(x: Optional[_Node], key: Key) -> Optional[_Node]:
    # smallest node >= key
    res = None
    while x is not None:
        c = _cmp(key, x.key)
        if c <= 0:
            res = x
            x = x.lh
        else:
            x = x.rh
    return res

def _inorder(x: Optional[_Node]) -> Iterable[_Node]:
    if x is None: return
    stack: List[_Node] = []
    cur = x
    while stack or cur:
        while cur: stack.append(cur); cur = cur.lh
        cur = stack.pop()
        yield cur
        cur = cur.rh

def _iter_range(x: Optional[_Node], lo: Key, hi: Key) -> Iterable[_Node]:
    # inclusive range [lo, hi]
    if x is None: return
    stack: List[_Node] = []
    cur = x
    while stack or cur:
        while cur:
            stack.append(cur)
            # if cur.key >= lo, go left; else skip left
            if _cmp(cur.key, lo) >= 0:
                cur = cur.lh
            else:
                break
        if not stack: break
        node = stack.pop()
        if _cmp(node.key, lo) >= 0 and _cmp(node.key, hi) <= 0:
            yield node
        # move right if node.key <= hi
        if _cmp(node.key, hi) <= 0:
            cur = node.rh
        else:
            cur = None

class TreeMatrix:
    """AVL-based sparse matrix with guaranteed O(log k) get/set.
       Keys are (i,j) in base orientation. Transpose is logical (flag).
    """
    def __init__(self, rows:int, cols:int):
        if rows<=0 or cols<=0: raise ValueError("invalid shape")
        self.rows = rows
        self.cols = cols
        self._root: Optional[_Node] = None
        self._nnz = 0
        self._transposed = False

    @property
    def shape(self): return (self.cols, self.rows) if self._transposed else (self.rows, self.cols)
    @property
    def nnz(self): return self._nnz

    def _norm(self, i:int, j:int) -> Key:
        if self._transposed: i,j = j,i
        r,c = self.rows, self.cols
        if not (0 <= i < r and 0 <= j < c):
            raise IndexError("index out of bounds")
        return (i,j)

    def access(self, i:int, j:int) -> float:
        key = self._norm(i,j)
        node = _find(self._root, key)
        return 0.0 if node is None else node.val

    def insert(self, i:int, j:int, val: float) -> None:
        key = self._norm(i,j)
        node = _find(self._root, key)
        existed = node is not None
        if val == 0.0:
            if existed:
                self._root = _delete(self._root, key)
                self._nnz -= 1
            return
        self._root = _insert(self._root, key, val)
        if not existed: self._nnz += 1

    def transpose(self) -> None:
        self._transposed = not self._transposed
        self.rows, self.cols = self.cols, self.rows

    def items(self) -> Iterable[Tuple[int,int,float]]:
        if not self._transposed:
            for nd in _inorder(self._root):
                i,j = nd.key
                yield (i,j,nd.val)
        else:
            for nd in _inorder(self._root):
                i,j = nd.key
                yield (j,i,nd.val)

    def iter_row(self, i:int) -> Iterable[Tuple[int,float]]:
        """Iterate (j,val) for a logical row i efficiently via range search."""
        # map logical i to base orientation
        if self._transposed:
            # logical row i corresponds to base column i -> we cannot range by column in base;
            # But multiplication code will call iter_row(t) on non-transposed matrices by construction.
            # For completeness, we can brute-force iterate; acceptable for verification/small sizes.
            for (ri,rj,v) in self.items():
                if ri == i: yield (rj, v)
            return
        lo = (i, -10**18)
        hi = (i,  10**18)
        for nd in _iter_range(self._root, lo, hi):
            # ensure row match
            if nd.key[0] == i:
                yield (nd.key[1], nd.val)

    # algebra
    def add(self, other: "TreeMatrix") -> "TreeMatrix":
        r,c = self.shape
        if other.shape != (r,c): raise ValueError("shape mismatch on add")
        R = TreeMatrix(r,c)
        for i,j,v in self.items(): R.insert(i,j,v)
        for i,j,v in other.items():
            cur = R.access(i,j)
            nv = cur + v
            R.insert(i,j,nv)
        return R

    def scale(self, a: float) -> "TreeMatrix":
        r,c = self.shape
        R = TreeMatrix(r,c)
        if a == 0.0: return R
        for i,j,v in self.items():
            R.insert(i,j, a*v)
        return R

    def matmul(self, other: "TreeMatrix") -> "TreeMatrix":
        nA,mA = self.shape
        nB,mB = other.shape
        if mA != nB: raise ValueError("shape mismatch on matmul")
        R = TreeMatrix(nA, mB)
        # For each nonzero (i,t) in A, multiply by row t of B
        for (i,t,a_it) in self.items():
            for (j, b_tj) in other.iter_row(t):
                cur = R.access(i,j)
                nv = cur + a_it*b_tj
                R.insert(i,j,nv)
        return R

    # convenience
    @staticmethod
    def from_coords(rows:int, cols:int, triplets: Iterable[Tuple[int,int,float]]) -> "TreeMatrix":
        M = TreeMatrix(rows, cols)
        for i,j,v in triplets:
            M.insert(i,j,v)
        return M
