# Lista 01 — Algoritmos de Ordenação

Esta atividade implementa e compara algoritmos de ordenação em Python e C++. A proposta original está em [lista_01-gc.pdf](lista_01-gc.pdf).

## Entregável

- [slides/lista.html](slides/lista.html): apresentação final interativa.
- [slides/lista.md](slides/lista.md): fonte Marp da apresentação.
- [artifacts/sorting_comparison.html](artifacts/sorting_comparison.html): visualização comparativa.
- [artifacts/sorting_results.html](artifacts/sorting_results.html): gráficos interativos da campanha.
- Tabela de apoio exportada pelo notebook: `family_winners.html`.
- Fontes relevantes: implementações `*.cpp` e `*.py` dos algoritmos de ordenação.

O [solucao.ipynb](solucao.ipynb) é apenas referência: ele **não é executável isoladamente**, pois depende da infraestrutura do projeto criada para visualização, log e métricas de análise. Essa infraestrutura é densa para este entregável; por isso, foram incorporados somente os fontes de sorting exibidos nos slides.

O código completo do projeto está disponível publicamente em [github.com/ineryo/tca-lab](https://github.com/ineryo/tca-lab).

### Estrutura do ZIP

```text
entregavel-lista-01/
├── README.md
├── assignments/01-sorting/
│   ├── README.md
│   ├── slides/{lista.md,lista.html,tca.css}
│   └── artifacts/{sorting_comparison,sorting_results,family_winners}.html
├── cpp/src/algorithms/sorting/{selection,insertion,merge,quick,radix}_sort.cpp
└── src/tca/reference/sorting/{selection,insertion,merge,quick,radix}_sort.py
```

### Criar o ZIP

Execute na raiz do repositório:

```powershell
$root = (Resolve-Path .).Path
$stage = Join-Path ([System.IO.Path]::GetTempPath()) ("entregavel-lista-01-" + [guid]::NewGuid())
$package = Join-Path $stage "entregavel-lista-01"
$zip = Join-Path $root "assignments/01-sorting/entregavel-lista-01.zip"
$files = @(
  Get-Item -LiteralPath @(
    "assignments/01-sorting/README.md",
    "assignments/01-sorting/slides/lista.md",
    "assignments/01-sorting/slides/lista.html",
    "assignments/01-sorting/slides/tca.css",
    "assignments/01-sorting/artifacts/sorting_comparison.html",
    "assignments/01-sorting/artifacts/sorting_results.html",
    "assignments/01-sorting/artifacts/family_winners.html"
  )
  Get-ChildItem "cpp/src/algorithms/sorting" -File -Filter "*_sort.cpp" |
    Where-Object Name -ne "radix_binary_sort.cpp"
  Get-ChildItem "src/tca/reference/sorting" -File -Filter "*_sort.py"
)
New-Item $package -ItemType Directory -Force | Out-Null

@'
# Entregável — Lista 01: Algoritmos de Ordenação

Apresentação final: [slides/lista.html](assignments/01-sorting/slides/lista.html).

A documentação completa, incluindo instruções e fontes incorporados, está em
[assignments/01-sorting/README.md](assignments/01-sorting/README.md).
'@ | Set-Content -LiteralPath (Join-Path $package "README.md") -Encoding utf8

foreach ($file in $files) {
  $target = Join-Path $package $file.FullName.Substring($root.Length).TrimStart('\')
  New-Item (Split-Path $target) -ItemType Directory -Force | Out-Null
  Copy-Item -LiteralPath $file.FullName -Destination $target
}
Compress-Archive -Path $package -DestinationPath $zip -Force
Remove-Item $stage -Recurse -Force
```

## Gerar o HTML

```powershell
npx marp assignments/01-sorting/slides/lista.md --theme assignments/01-sorting/slides/tca.css --html --allow-local-files --output assignments/01-sorting/slides/lista.html
```
