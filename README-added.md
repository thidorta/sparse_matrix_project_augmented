
# Sparse Matrices — Dict-of-Dicts + AVL Tree

Este projeto implementa **duas** estruturas de matrizes esparsas em Python:

1. `SparseMatrix` (dict de dicts) — **O(1)** médio (hash) para `get/set`, transposta lógica O(1).
2. `TreeMatrix` (AVL por chave `(i,j)`) — **O(log k)** garantido para `get/set`, transposta lógica O(1).

Também inclui uma `DenseMatrix` (baseline) para verificação e benchmarks.

## Como usar (exemplos rápidos)

```bash
# criar venv (opcional)
python -m venv .venv && .venv\Scripts\activate  # no Windows
# pip install -r requirements.txt   # nada obrigatório

python - << "PY"
from lib.sparse_matrix import SparseMatrix
from lib.tree_matrix import TreeMatrix
from lib.dense_matrix import DenseMatrix

A = SparseMatrix.random(8,8,0.2,(1,9))
B = SparseMatrix.random(8,8,0.2,(1,9))

print("A (coords):"); A.show(dense=False)
print("A (denso):"); A.show(dense=True)

T = TreeMatrix.from_coords(A.rows,A.cols, [(i,j,v) for i,row in A.data.items() for j,v in row.items()])
S = A + B
M = A * B
print("A+B (denso):"); S.show(dense=True)
print("A*B (denso):"); M.show(dense=True)
PY
```

### Verificar correção (comparar com denso)
```
python verify.py --A A.txt --B B.txt --op add
python verify.py --A A.txt --B B.txt --op matmul
```

### Benchmark (gera CSV simples)
```
python bench.py --n 500 --density 0.01 --repeat 3 --out results.csv
```

## Arquitetura resumida
- `lib/sparse_matrix.py` — dict de dicts + `is_transposed` → transposta O(1).
- `lib/tree_matrix.py` — **AVL** (chave `(i,j)`), `iter_row(i)` via busca por faixa.
- `lib/dense_matrix.py` — baseline denso, útil para checar resultados.
- `verify.py` — compara `add` e `matmul` nas três representações e mostra erro máximo.
- `bench.py` — gera instâncias e mede tempo de `add/scale/matmul`.

## Notas importantes
- **Zeros**: inserir `0` remove a entrada, preservando esparsidade.
- **Transposta**: é **lógica** (flag); índices são trocados no acesso/iteração.
- **Multiplicação**: `A * B` percorre `A` por não-nulos e usa `iter_row(t)` de `B` (eficiente no AVL).

## Próximos passos para o relatório
- Rodar `bench.py` com (n, densidade) do PDF; salvar CSVs.
- Plotar tempo vs. n e tempo vs. densidade; discutir onde cada estrutura vence.
- Comparar memória por elemento (dict vs AVL) e ponto de transição para denso.
