# Paper sources

LaTeX sources, bibliography files, and the figures needed to build them live here. Compiled PDFs remain in `paper/`.

The published paper source is `lqg-amplituhedron.tex`; its frozen PDF is `../../paper/lqg-amplituhedron.pdf`. The thermal-intertwiners proposal source and its figures are in `thermal-intertwiners/`; compiled copies are under `../../paper/thermal-intertwiners/`.

Build from each source directory so the relative figure and bibliography paths resolve. For example, from this directory:

```sh
latexmk -pdf -outdir=../../paper lqg-amplituhedron.tex
```

For the thermal-intertwiners proposal, run `latexmk -pdf -outdir=../../../paper/thermal-intertwiners thermal-intertwiners.tex` from `code/papers/thermal-intertwiners/`.
