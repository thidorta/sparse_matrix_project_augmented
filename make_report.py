
import argparse, csv, statistics, os, platform, datetime
from pathlib import Path

def load_summary(path):
    rows = []
    with open(path, newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            try:
                n = int(row["n"]); d = float(row["density"]); case=row["case"]; ms=float(row["ms"])
                op, impl = case.split(":",1)
                rows.append({"n":n,"d":d,"op":op,"impl":impl,"ms":ms})
            except Exception:
                continue
    return rows

def uniq(xs): return sorted(set(xs))

def pivot(rows, keys):
    from collections import defaultdict
    g = defaultdict(list)
    for r in rows:
        g[tuple(r[k] for k in keys)].append(r)
    return g

def summarize(rows):
    Ns = uniq(r["n"] for r in rows)
    Ds = uniq(r["d"] for r in rows)
    Ops = uniq(r["op"] for r in rows)
    Impls = uniq(r["impl"] for r in rows)
    return Ns, Ds, Ops, Impls

def choose_figs(Ns, Ds, Ops):
    figs = []
    pick_ops = Ops if len(Ops)<=2 else [Ops[0], Ops[-1]]
    smallN, largeN = (Ns[0], Ns[-1]) if Ns else (None,None)
    smallD, largeD = (Ds[0], Ds[-1]) if Ds else (None,None)
    for op in pick_ops:
        if smallD is not None:
            figs.append(("time_vs_n", op, f"d{str(smallD).replace('.','p')}"))
        if largeD is not None and largeD!=smallD:
            figs.append(("time_vs_n", op, f"d{str(largeD).replace('.','p')}"))
        if smallN is not None:
            figs.append(("time_vs_density", op, f"n{smallN}"))
        if largeN is not None and largeN!=smallN:
            figs.append(("time_vs_density", op, f"n{largeN}"))
    out, seen = [], set()
    for t in figs:
        if t in seen: continue
        seen.add(t); out.append(t)
    return out[:6]

def compute_speedups(rows):
    out = {}
    by = pivot(rows, ["op","n","d"])
    for key, group in by.items():
        times = {}
        for r in group: times[r["impl"]] = r["ms"]
        if "dict" in times:
            dtime = times["dict"]
            if "tree" in times and dtime>0:
                out.setdefault("dict_vs_tree", []).append(times["tree"]/dtime)
            if "dense" in times and dtime>0:
                out.setdefault("dict_vs_dense", []).append(times["dense"]/dtime)
    med = {k: statistics.median(v) for k,v in out.items() if v}
    return med

def mk_md(rows, title, authors, course):
    Ns, Ds, Ops, Impls = summarize(rows)
    today = datetime.date.today().isoformat()
    speed = compute_speedups(rows)

    lines = []
    lines += [f"# {title}", "", f"**Autores:** {authors}", f"**Disciplina:** {course}", f"**Data:** {today}", ""]
    resume = ("Implementamos duas estruturas para matrizes esparsas: (i) *dict-of-dicts* (hash, O(1) médio) "
              "e (ii) árvore AVL por chave (i,j) (O(log k) garantido), além de baseline denso. "
              "Comparamos `add`, `scale`, `matmul` e `transpose` nos tamanhos e densidades do enunciado.")
    if speed:
        frag = []
        if "dict_vs_tree" in speed: frag.append(f"mediana(tree/dict) ≈ **{speed['dict_vs_tree']:.1f}×**")
        if "dict_vs_dense" in speed: frag.append(f"mediana(dense/dict) ≈ **{speed['dict_vs_dense']:.1f}×**")
        if frag: resume += " Razões de tempo típicas: " + ", ".join(frag) + "."
    lines += ["## Resumo", "", resume, ""]

    lines += ["## Introdução", "", 
              "Dizemos que uma matriz é **esparsa** quando o número de elementos não nulos `k` satisfaz `k ≪ n·m`. "
              "Nesses cenários, estruturas esparsas evitam varrer zeros, reduzindo custo temporal e espacial.", ""]

    lines += ["## Estruturas de Dados", "",
              "### Hash (dict-of-dicts)",
              "- Layout: linha → {coluna → valor}; zeros removem a entrada.",
              "- Complexidades: `get/set` O(1) médio; `transpose` O(1); `add` O(kA+kB); `scale` O(k); `matmul` ≈ O(kA·dB).",
              "",
              "### AVL (árvore por (i,j))",
              "- Chave `(i,j)` em ordem lexicográfica; `iter_row(i)` por faixa.",
              "- Complexidades: `get/set` O(log k); `transpose` O(1); `add` O((kA+kB)·log k); `scale` O(k); `matmul` ≈ O(kA·dB·log kC).",
              ""]

    lines += ["## Metodologia Experimental", "",
              f"Tamanhos testados: {', '.join(map(str,Ns))}.",
              f"Densidades testadas: {', '.join(map(str,Ds))}.",
              f"Operações: {', '.join(Ops)}.",
              "Tempo reportado: melhor de N repetições por caso.", ""]

    lines += ["## Resultados", ""]
    figs = choose_figs(Ns, Ds, Ops)
    for kind, op, tag in figs:
        if kind=="time_vs_n":
            img = f"results/figs_item2/time_vs_n_{op}_{tag}.png"
            lines += [f"**{op} — tempo vs n** (densidade {tag[1:].replace('p','.')}):",
                      f"![{op} vs n]({img})", ""]
        else:
            img = f"results/figs_item2/time_vs_density_{op}_{tag}.png"
            lines += [f"**{op} — tempo vs densidade** ({tag}):",
                      f"![{op} vs densidade]({img})", ""]

    lines += ["## Discussão", "",
              "- Hash domina em baixa densidade (constante menor + O(1) médio).",
              "- AVL oferece garantias e boa varredura ordenada, porém paga o fator log.",
              "- Denso só se aproxima em densidades altas ou tamanhos pequenos.",
              "- `transpose` é lógico (O(1)) e não depende de `nnz`.", ""]

    lines += ["## Conclusão", "",
              "Em instâncias esparsas, **dict-of-dicts** tende a ser a melhor escolha prática; a **AVL** é indicada quando a "
              "ordenação e limites assintóticos garantidos são requisitos. Para densidades altas, representações densas tendem a vencer.", ""]

    return "\n".join(lines)

def md_to_html(md_text):
    import html, re
    out = ['<!doctype html><meta charset="utf-8"><style>body{font:16px/1.6 sans-serif;max-width:900px;margin:40px auto;padding:0 16px}img{max-width:100%}h1,h2,h3{margin-top:1.2em}</style><body>']
    for line in md_text.splitlines():
        if line.startswith("# "): out.append(f"<h1>{html.escape(line[2:])}</h1>"); continue
        if line.startswith("## "): out.append(f"<h2>{html.escape(line[3:])}</h2>"); continue
        if line.startswith("### "): out.append(f"<h3>{html.escape(line[4:])}</h3>"); continue
        m = re.match(r'!\[(.*?)\]\((.*?)\)', line.strip())
        if m:
            alt, src = m.group(1), m.group(2)
            out.append(f'<figure><img src="{html.escape(src)}" alt="{html.escape(alt)}"><figcaption>{html.escape(alt)}</figcaption></figure>')
            continue
        line = line.replace("**","<b>")  # básica
        out.append(f"<p>{line}</p>")
    out.append("</body>")
    return "\n".join(out)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--summary", default="results/summary.csv")
    ap.add_argument("--title", default="Relatório — Matrizes Esparsas")
    ap.add_argument("--authors", default="Seu Nome")
    ap.add_argument("--course", default="MC458")
    ap.add_argument("--out_md", default="RELATORIO_MC458.md")
    ap.add_argument("--out_html", default="RELATORIO_MC458.html")
    args = ap.parse_args()

    rows = load_summary(args.summary)
    md = mk_md(rows, args.title, args.authors, args.course)
    with open(args.out_md, "w", encoding="utf-8") as f: f.write(md)
    html = md_to_html(md)
    with open(args.out_html, "w", encoding="utf-8") as f: f.write(html)
    print("OK:", args.out_md)
    print("OK:", args.out_html)

if __name__ == "__main__":
    main()
