
# Relatório — Matrizes Esparsas (versão Python)

## 1. Introdução
Defina matriz esparsa (k ≪ n·m), motivação e aplicações.

## 2. Estruturas
- **Dict-of-dicts (hash)**: O(1) médio, transposta O(1), índice por linhas.
- **AVL por (i,j)**: O(log k) garantido, transposta O(1), `iter_row` por faixa.

## 3. Complexidade teórica
Tabela com `get/set`, `transpose`, `add`, `scale`, `matmul` para ambas. Explique por que `matmul` ~ O(k_A·d_B).

## 4. Metodologia
Gerador (n, densidade, seeds), ambiente (CPU, RAM, Python), métricas.

## 5. Resultados
Gráficos/tabelas de tempos (csv do `bench.py`), discussão por regime.

## 6. Conclusão
Quando usar cada estrutura; limitações e ideias futuras (CSR/CSC, Numpy/SciPy).

