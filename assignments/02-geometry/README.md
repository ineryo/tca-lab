# Lista 02 — Geometria Computacional

Esta atividade implementa e aplica primitivas e algoritmos de geometria computacional em C++, com demonstrações e visualizações interativas. A proposta original está em [lista_02-gc.pdf](lista_02-gc.pdf).

## Entregável

- [resposta.html](resposta.html): relatório final interativo.
- [resposta.md](resposta.md): fonte Markdown do relatório.
- [report.css](report.css): estilo utilizado na geração do HTML.
- [solucao.ipynb](solucao.ipynb): notebook completo de desenvolvimento, validação e geração das visualizações.
- [artifacts/q01_pseudo_angle.html](artifacts/q01_pseudo_angle.html): visualização do pseudo-ângulo.
- [artifacts/q02_entre.html](artifacts/q02_entre.html): visualização do critério `entre`.
- [artifacts/q03_barycentric_location.html](artifacts/q03_barycentric_location.html): coordenadas baricêntricas e localização em triângulo.
- [artifacts/q04_clipping.html](artifacts/q04_clipping.html): visualização do recorte/interseção de segmento com triângulo.
- [artifacts/q05_triangle_disjointness.html](artifacts/q05_triangle_disjointness.html): casos de interseção e disjunção entre triângulos.
- [artifacts/q06_convexity.html](artifacts/q06_convexity.html): verificação de convexidade de polígonos.
- [artifacts/q07_first_intersection.html](artifacts/q07_first_intersection.html): classificação ponto-polígono pela primeira interseção do raio.
- Fontes relevantes: `cpp/include/tca/geometry/*.hpp` e `cpp/src/geometry/*.cpp`.

O [solucao.ipynb](solucao.ipynb) é incluído como registro completo da solução e do processo de validação. Sua execução integral depende da extensão C++ e da infraestrutura do projeto; por isso, o [resposta.html](resposta.html) constitui o documento principal de leitura, enquanto o notebook preserva os experimentos e a geração dos artefatos.

O código completo do projeto está disponível publicamente em [github.com/ineryo/tca-lab](https://github.com/ineryo/tca-lab).

### Estrutura do ZIP

```text
entregavel-lista-02/
├── README.md
├── assignments/02-geometry/
│   ├── README.md
│   ├── lista_02-gc.pdf
│   ├── solucao.ipynb
│   ├── resposta.md
│   ├── resposta.html
│   ├── report.css
│   └── artifacts/
│       ├── q01_pseudo_angle.html
│       ├── q02_entre.html
│       ├── q03_barycentric_location.html
│       ├── q04_clipping.html
│       ├── q05_triangle_disjointness.html
│       ├── q06_convexity.html
│       └── q07_first_intersection.html
└── cpp/
    ├── include/tca/geometry/
    │   ├── types.hpp
    │   ├── numeric.hpp
    │   ├── primitives.hpp
    │   └── algorithms.hpp
    └── src/geometry/
        ├── primitives.cpp
        └── algorithms.cpp
```

## Atualizar o relatório

Os trechos de código e as figuras inseridos em `resposta.md` são sincronizados pelo Markdown Artifact Updater:

```powershell
uv run markdown-artifact-updater update assignments/02-geometry/resposta.md --repo-root . --apply
```

## Gerar o HTML

Após atualizar o Markdown, gere o relatório HTML com Pandoc:

```powershell
pandoc assignments/02-geometry/resposta.md `
    --standalone `
    --mathjax `
    --css=report.css `
    -o assignments/02-geometry/resposta.html
```

O `resposta.html`, o `report.css` e a pasta `artifacts/` devem permanecer juntos na estrutura indicada acima para preservar o estilo e as visualizações interativas.

## Repositório do projeto

Este entregável contém os arquivos necessários para leitura, avaliação e
reprodução dos principais resultados da Lista 02.

A implementação completa faz parte do projeto **TCA Lab**, disponível em:

[github.com/ineryo/tca-lab](https://github.com/ineryo/tca-lab)

O repositório é mantido como projeto em desenvolvimento e pode receber
atualizações posteriores à geração deste entregável, incluindo melhorias de
implementação, documentação, testes, visualizações e novas funcionalidades.

Por esse motivo, o conteúdo deste ZIP representa uma versão autocontida da
solução no momento da entrega, enquanto o repositório Git deve ser considerado
a referência para a versão mais recente do código.

### Criar o ZIP

Execute na raiz do repositório:

```powershell
# ============================================================
# Entregável — Lista 02: Geometria Computacional
# Execute de qualquer diretório dentro do repositório Git.
# ============================================================

$root = (git rev-parse --show-toplevel).Trim()

if (-not $root -or -not (Test-Path -LiteralPath $root)) {
    throw "Não foi possível localizar a raiz do repositório Git."
}

$stage = Join-Path ([System.IO.Path]::GetTempPath()) (
    "entregavel-lista-02-" + [guid]::NewGuid()
)

$package = Join-Path $stage "entregavel-lista-02"

$zip = Join-Path `
    $root `
    "assignments/02-geometry/entregavel-lista-02.zip"


# ------------------------------------------------------------
# Arquivos incluídos no entregável
# ------------------------------------------------------------

$files = @(

    # Documentação e solução
    "assignments/02-geometry/README.md",
    "assignments/02-geometry/lista_02-gc.pdf",
    "assignments/02-geometry/solucao.ipynb",
    "assignments/02-geometry/resposta.md",
    "assignments/02-geometry/resposta.html",
    "assignments/02-geometry/report.css",

    # Artefatos interativos
    "assignments/02-geometry/artifacts/q01_pseudo_angle.html",
    "assignments/02-geometry/artifacts/q02_entre.html",
    "assignments/02-geometry/artifacts/q03_barycentric_location.html",
    "assignments/02-geometry/artifacts/q04_clipping.html",
    "assignments/02-geometry/artifacts/q05_triangle_disjointness.html",
    "assignments/02-geometry/artifacts/q06_convexity.html",
    "assignments/02-geometry/artifacts/q07_first_intersection.html",

    # Interfaces C++
    "cpp/include/tca/geometry/types.hpp",
    "cpp/include/tca/geometry/numeric.hpp",
    "cpp/include/tca/geometry/primitives.hpp",
    "cpp/include/tca/geometry/algorithms.hpp",

    # Implementações C++
    "cpp/src/geometry/primitives.cpp",
    "cpp/src/geometry/algorithms.cpp"
)


# ------------------------------------------------------------
# Validação
# ------------------------------------------------------------

foreach ($relative in $files) {
    $source = Join-Path $root $relative

    if (-not (Test-Path -LiteralPath $source)) {
        throw "Arquivo ausente no pacote: $relative"
    }
}


# ------------------------------------------------------------
# Diretório temporário
# ------------------------------------------------------------

New-Item `
    -Path $package `
    -ItemType Directory `
    -Force |
    Out-Null


# ------------------------------------------------------------
# README curto da raiz do ZIP
# ------------------------------------------------------------

@'
# Entregável — Lista 02: Geometria Computacional

Este pacote reúne a entrega da **Lista 02 — Geometria Computacional** da
disciplina **Técnicas Computacionais Avançadas**.

## Conteúdo principal

- Relatório final interativo:  
  [assignments/02-geometry/resposta.html](assignments/02-geometry/resposta.html)

- Notebook completo da solução:  
  [assignments/02-geometry/solucao.ipynb](assignments/02-geometry/solucao.ipynb)

- Documentação detalhada do entregável:  
  [assignments/02-geometry/README.md](assignments/02-geometry/README.md)

- Enunciado original:  
  [assignments/02-geometry/lista_02-gc.pdf](assignments/02-geometry/lista_02-gc.pdf)

## Organização

O arquivo `resposta.html` é o documento principal de leitura e reúne as
explicações, resultados e visualizações interativas.

O notebook `solucao.ipynb` preserva o desenvolvimento completo da solução,
incluindo experimentos, validações e geração das figuras.

Os fontes C++ relevantes utilizados nas soluções também estão incluídos neste
pacote.

## Repositório

A implementação faz parte do projeto **TCA Lab**, mantido e atualizado em:

https://github.com/ineryo/tca-lab

Este ZIP representa uma versão autocontida da solução no momento da entrega.
O repositório Git pode conter atualizações posteriores, melhorias de
implementação, documentação, testes e novas funcionalidades.
'@ | Set-Content `
    -LiteralPath (Join-Path $package "README.md") `
    -Encoding utf8


# ------------------------------------------------------------
# Copiar arquivos preservando a estrutura do repositório
# ------------------------------------------------------------

foreach ($relative in $files) {

    $source = Join-Path $root $relative
    $target = Join-Path $package $relative

    $targetDirectory = Split-Path $target

    New-Item `
        -Path $targetDirectory `
        -ItemType Directory `
        -Force |
        Out-Null

    Copy-Item `
        -LiteralPath $source `
        -Destination $target
}


# ------------------------------------------------------------
# Gerar ZIP
# ------------------------------------------------------------

Compress-Archive `
    -Path $package `
    -DestinationPath $zip `
    -Force


# ------------------------------------------------------------
# Limpeza
# ------------------------------------------------------------

Remove-Item `
    -LiteralPath $stage `
    -Recurse `
    -Force


# ------------------------------------------------------------
# Resultado
# ------------------------------------------------------------

Write-Host ""
Write-Host "Entregável criado com sucesso:"
Write-Host $zip
```