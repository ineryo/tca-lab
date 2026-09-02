# Fluxo de documentação e apresentação da lista de TCA

## Jupyter Notebook + Marp + Marp Artifact Updater

## 1. Objetivo

Esta documentação define um fluxo para elaboração e entrega das atividades de **Técnicas Computacionais Avançadas (TCA)** combinando:

- Jupyter Notebook para execução, análise e documentação detalhada;
- C++ e Python para implementações dos algoritmos;
- `marp-artifact-updater` para sincronizar automaticamente trechos de código e artefatos com a apresentação;
- Marp para apresentação visual;
- HTML como formato final interativo;
- HTML do notebook como registro frozen da execução.

A ideia central é evitar cópias manuais de código.

A implementação real permanece nos arquivos-fonte ou nas células do notebook, enquanto a apresentação apenas referencia essas fontes.

O fluxo geral é:

```text
                    ┌──────────────────────┐
                    │ Arquivos-fonte       │
                    │ .cpp / .py           │
                    └──────────┬───────────┘
                               │
                               │
                    ┌──────────▼───────────┐
                    │ Notebook .ipynb      │
                    │                      │
                    │ execução             │
                    │ experimentos         │
                    │ benchmarks           │
                    │ Plotly               │
                    └──────┬────────┬──────┘
                           │        │
                  export   │        │ artefatos
                           │        │
               ┌───────────▼──┐  ┌──▼──────────────┐
               │ notebook.html│  │ plots / tabelas │
               │ frozen       │  │ .html/.png/.csv │
               └──────────────┘  └───────┬─────────┘
                                         │
 Arquivos-fonte ─────────────────────────┤
                                         │
                              ┌──────────▼──────────┐
                              │ marp-artifact-      │
                              │ updater             │
                              └──────────┬──────────┘
                                         │
                                         ▼
                              ┌─────────────────────┐
                              │ slides/lista.md     │
                              │                     │
                              │ C++ │ Python        │
                              │ plots               │
                              │ resultados          │
                              └──────────┬──────────┘
                                         │
                                      Marp
                                         │
                                         ▼
                              ┌─────────────────────┐
                              │ lista.html          │
                              │ apresentação        │
                              └─────────────────────┘
```

---

# 2. Produtos finais

O trabalho passa a possuir dois produtos principais.

## 2.1. Notebook frozen

Exemplo:

```text
analysis.html
```

Ele contém:

- explicações;
- células executadas;
- outputs;
- tabelas;
- resultados;
- gráficos;
- experimentos;
- documentação detalhada.

É o registro completo da execução.

---

## 2.2. Apresentação Marp

Exemplo:

```text
lista.html
```

Ela contém apenas os elementos importantes para apresentação:

- formulação do problema;
- ideia do algoritmo;
- trechos relevantes;
- comparação C++ × Python;
- complexidade;
- benchmarks;
- plots;
- conclusões.

Portanto:

```text
analysis.html
    =
relatório computacional frozen

lista.html
    =
apresentação
```

Eles são complementares, não concorrentes.

---

# 3. Estrutura recomendada do projeto

Para a atividade de Sorting, por exemplo:

```text
assignments/
└── 01-sorting/
    │
    ├── notebooks/
    │   └── analysis.ipynb
    │
    ├── src/
    │   ├── cpp/
    │   │   ├── selection_sort.cpp
    │   │   ├── merge_sort.cpp
    │   │   ├── quick_sort.cpp
    │   │   └── radix_sort.cpp
    │   │
    │   └── python/
    │       ├── selection_sort.py
    │       ├── merge_sort.py
    │       ├── quick_sort.py
    │       └── radix_sort.py
    │
    ├── artifacts/
    │   ├── benchmark_results.jsonl
    │   ├── complexity.csv
    │   ├── complexity_plot.html
    │   ├── complexity_plot.png
    │   └── sorting_animation.html
    │
    ├── slides/
    │   ├── lista.md
    │   └── tca.css
    │
    └── dist/
        ├── lista.html
        ├── lista.pdf
        └── analysis.html
```

A divisão de responsabilidades fica:

```text
src/
    código real

notebooks/
    execução e análise

artifacts/
    resultados produzidos

slides/
    apresentação

dist/
    arquivos finais para entrega
```

---

# 4. Instalação das ferramentas

## 4.1. Marp CLI

A forma recomendada para um projeto é instalar o Marp localmente como dependência de desenvolvimento:

```bash
npm install --save-dev @marp-team/marp-cli
```

Depois:

```bash
npx marp --version
```

O Marp CLI suporta geração de HTML diretamente e também possui modos `watch`, `server` e `preview`.

---

## 4.2. Marp Artifact Updater

Considerando o projeto configurado com `uv`, o updater deverá estar disponível no ambiente.

Teste:

```bash
uv run marp-artifact-updater --help
```

Os comandos principais são:

```bash
uv run marp-artifact-updater check slides/lista.md --repo-root .
```

e:

```bash
uv run marp-artifact-updater update slides/lista.md --repo-root . --apply
```

O comportamento é deliberadamente conservador:

```text
check
    apenas verifica

update
    dry-run por padrão

update --apply
    modifica o arquivo
```

O updater altera somente regiões delimitadas e preserva o restante do Markdown.

---

# 5. Criando snippets nos arquivos Python

Considere:

```text
assignments/01-sorting/src/python/merge_sort.py
```

Marque apenas a parte que interessa à apresentação:

```python
def merge(left, right):
    result = []

    while left and right:
        if left[0] <= right[0]:
            result.append(left.pop(0))
        else:
            result.append(right.pop(0))

    return result + left + right


# snippet:start merge-sort

def merge_sort(values):
    if len(values) <= 1:
        return values

    middle = len(values) // 2

    left = merge_sort(values[:middle])
    right = merge_sort(values[middle:])

    return merge(left, right)

# snippet:end merge-sort
```

O identificador:

```text
merge-sort
```

poderá então ser usado pela apresentação.

O updater reconhece o formato:

```text
# snippet:start NAME

...

# snippet:end NAME
```



---

# 6. Criando o snippet correspondente em C++

Arquivo:

```text
assignments/01-sorting/src/cpp/merge_sort.cpp
```

Por exemplo:

```cpp
#include <vector>

// snippet:start merge-sort

void merge_sort(std::vector<int>& values) {
    if (values.size() <= 1) {
        return;
    }

    const std::size_t middle = values.size() / 2;

    std::vector<int> left(
        values.begin(),
        values.begin() + middle
    );

    std::vector<int> right(
        values.begin() + middle,
        values.end()
    );

    merge_sort(left);
    merge_sort(right);

    merge(values, left, right);
}

// snippet:end merge-sort
```

Dessa forma existe o mesmo identificador lógico:

```text
merge-sort
```

nas duas implementações:

```text
merge_sort.cpp#merge-sort

merge_sort.py#merge-sort
```

Isso facilita muito a comparação.

---

# 7. Utilizando snippets vindos diretamente do notebook

Também é possível armazenar o snippet dentro de uma célula de código do `.ipynb`.

Por exemplo, uma célula Python pode conter:

```python
# snippet:start complexity-estimation

estimate = estimate_complexity_from_results(
    results,
    algorithm="merge",
    backend="python",
    family="uniform_random",
    metric="comparisons",
)

estimate.best_model, estimate.power_exponent

# snippet:end complexity-estimation
```

Salve o notebook.

O updater poderá então ler essa célula.

Importante:

> O `marp-artifact-updater` não executa o notebook.

Ele lê somente o código que está salvo no `.ipynb`.

Portanto:

```text
alterar célula
      ↓
salvar notebook
      ↓
executar updater
      ↓
slide atualizado
```

Não é necessário executar a célula para atualizar o código exibido no slide.

---

# 8. Criando a apresentação Marp

Arquivo:

```text
assignments/01-sorting/slides/lista.md
```

Comece com:

```markdown
---
marp: true
theme: tca
paginate: true
---

# Técnicas Computacionais Avançadas

## Algoritmos de Ordenação

Igor Nery
```

Depois:

```markdown
---

## Merge Sort

O Merge Sort utiliza a estratégia de divisão e conquista:

1. divide o vetor;
2. ordena recursivamente cada metade;
3. combina as partes ordenadas.

Complexidade assintótica:

\[
T(n) = 2T(n/2) + O(n)
\]

portanto:

\[
T(n) = O(n\log n)
\]
```

---

# 9. Criando o slide de comparação C++ × Python

Queremos obter:

```text
               Trecho do código merge_sort

      merge_sort.cpp        │       merge_sort.py
                             │
      void merge_sort(...)  │       def merge_sort(...):
      {                      │           ...
          ...                │
      }                      │
```

No Markdown:

```markdown
---

<!-- _class: code-compare -->

### Trecho do código `merge_sort`

##### `merge_sort.cpp`

##### `merge_sort.py`

<!-- snippet-include: assignments/01-sorting/src/cpp/merge_sort.cpp#merge-sort -->
```cpp
// conteúdo atualizado automaticamente
```
<!-- snippet-include-end -->

<!-- snippet-include: assignments/01-sorting/src/python/merge_sort.py#merge-sort -->
```python
# conteúdo atualizado automaticamente
```
<!-- snippet-include-end -->
```

A diretiva:

```markdown
<!-- _class: code-compare -->
```

aplica a classe apenas ao slide atual.

No Marpit/Marp, `class` é uma diretiva local e o prefixo `_` transforma a diretiva em uma diretiva aplicada somente à página atual.

---

# 10. Criando o tema CSS

Arquivo:

```text
assignments/01-sorting/slides/tca.css
```

Conteúdo inicial:

```css
/* @theme tca */

@import 'default';

section {
    font-size: 30px;
}

/* ==========================================================
   Slide com comparação de código C++ | Python
   ========================================================== */

section.code-compare {
    display: grid;

    grid-template-columns:
        minmax(0, 1fr)
        1px
        minmax(0, 1fr);

    grid-template-rows:
        auto
        auto
        minmax(0, 1fr);

    column-gap: 24px;
    align-items: start;
}

/* Título principal */
section.code-compare > h3 {
    grid-column: 1 / -1;
    grid-row: 1;

    margin-bottom: 18px;
}

/* Título da coluna C++ */
section.code-compare > h5:nth-of-type(1) {
    grid-column: 1;
    grid-row: 2;

    margin-top: 0;
    margin-bottom: 10px;
    text-align: center;
}

/* Título da coluna Python */
section.code-compare > h5:nth-of-type(2) {
    grid-column: 3;
    grid-row: 2;

    margin-top: 0;
    margin-bottom: 10px;
    text-align: center;
}

/* Primeiro bloco de código */
section.code-compare > pre:nth-of-type(1) {
    grid-column: 1;
    grid-row: 3;
}

/* Segundo bloco de código */
section.code-compare > pre:nth-of-type(2) {
    grid-column: 3;
    grid-row: 3;
}

/* Linha divisora */
section.code-compare::after {
    content: "";

    grid-column: 2;
    grid-row: 2 / 4;

    width: 1px;
    height: 100%;

    background: currentColor;
    opacity: 0.25;
}

/* Código */
section.code-compare pre {
    margin: 0;
    width: 100%;
    overflow: hidden;
}

/* Fonte ligeiramente menor */
section.code-compare pre code {
    font-size: 0.72em;
    line-height: 1.35;
}
```

Esse CSS não depende do updater.

A responsabilidade fica separada:

```text
marp-artifact-updater
        ↓
conteúdo

CSS Marp
        ↓
layout
```

O Marp permite temas CSS próprios, inclusive passando diretamente o arquivo CSS ao CLI.

---

# 11. Atualizando os snippets

A partir da raiz do repositório:

```bash
uv run marp-artifact-updater check \
    assignments/01-sorting/slides/lista.md \
    --repo-root .
```

Se algum trecho estiver desatualizado, o comando retorna indicando mudança necessária.

Depois:

```bash
uv run marp-artifact-updater update \
    assignments/01-sorting/slides/lista.md \
    --repo-root . \
    --apply
```

Execute novamente:

```bash
uv run marp-artifact-updater check \
    assignments/01-sorting/slides/lista.md \
    --repo-root .
```

O resultado esperado é que nenhum trecho esteja stale.

O fluxo passa a ser:

```text
editar merge_sort.cpp
        ↓
salvar
        ↓
marp-artifact-updater check
        ↓
detecta diferença
        ↓
marp-artifact-updater update --apply
        ↓
lista.md atualizado
```

---

# 12. Por que usar `check` antes da entrega

O comando:

```bash
marp-artifact-updater check
```

é especialmente interessante porque permite detectar:

```text
slide
   ≠
código atual
```

sem alterar nada.

Assim é possível incluir no fluxo de entrega:

```text
1. testes
2. benchmarks
3. notebook
4. updater check
5. Marp build
```

O updater define códigos de saída diferentes para conteúdo stale e entradas inválidas, permitindo também futura integração com scripts e CI.

---

# 13. Visualizando a apresentação durante o desenvolvimento

Uma forma simples é:

```bash
npx marp \
    assignments/01-sorting/slides/lista.md \
    --theme assignments/01-sorting/slides/tca.css \
    --preview
```

O modo preview abre uma janela própria de apresentação e ativa automaticamente o acompanhamento de alterações.

Outra possibilidade:

```bash
npx marp \
    assignments/01-sorting/slides/lista.md \
    --theme assignments/01-sorting/slides/tca.css \
    --watch
```

O `--watch` observa alterações no Markdown e no CSS usado como tema e regenera a saída quando necessário.

---

# 14. Gerando o HTML da apresentação

Execute:

```bash
npx marp \
    assignments/01-sorting/slides/lista.md \
    --theme assignments/01-sorting/slides/tca.css \
    --html \
    -o assignments/01-sorting/dist/lista.html
```

O Marp CLI gera HTML diretamente. A opção `--html` habilita tags HTML no conteúdo quando necessárias.

O arquivo:

```text
assignments/01-sorting/dist/lista.html
```

é a apresentação final.

---

# 15. Gerando também PDF

Como fallback:

```bash
npx marp \
    assignments/01-sorting/slides/lista.md \
    --theme assignments/01-sorting/slides/tca.css \
    --html \
    -o assignments/01-sorting/dist/lista.pdf
```

O PDF é útil para:

- arquivamento;
- impressão;
- visualização rápida;
- contingência.

Entretanto, componentes interativos obviamente tornam-se estáticos no PDF.

Por isso:

```text
HTML = apresentação principal

PDF = fallback
```

---

# 16. Gerando gráficos interativos no notebook

Para Plotly:

```python
fig.show()
```

continua sendo usado normalmente durante o desenvolvimento.

Quando o gráfico estiver pronto para ser usado na apresentação:

```python
from pathlib import Path

artifact_path = (
    ROOT
    / "assignments"
    / "01-sorting"
    / "artifacts"
    / "complexity_plot.html"
)

fig.write_html(
    artifact_path,
    include_plotlyjs=True,
    full_html=True,
)
```

Com:

```python
include_plotlyjs=True
```

o JavaScript necessário fica incorporado ao arquivo do gráfico.

Isso facilita a preservação da interatividade.

---

# 17. Inserindo o gráfico no Marp

O `marp-artifact-updater` aceita figuras em formatos como:

```text
PNG
JPEG
GIF
SVG
WebP
AVIF
HTML
HTM
```

Para HTML, o comportamento padrão é produzir um `iframe`.

No slide:

```markdown
---

## Complexidade experimental

<!-- figure-include: assignments/01-sorting/artifacts/complexity_plot.html -->
<!-- figure-include-end -->
```

Depois:

```bash
uv run marp-artifact-updater update \
    assignments/01-sorting/slides/lista.md \
    --repo-root . \
    --apply
```

O updater gera o conteúdo necessário dentro da região.

---

# 18. Plot interativo versus plot estático

É recomendável gerar os dois:

```text
complexity_plot.html
complexity_plot.png
```

Por exemplo:

```python
fig.write_html(
    "complexity_plot.html",
    include_plotlyjs=True,
)

fig.write_image(
    "complexity_plot.png",
    width=1600,
    height=900,
    scale=2,
)
```

A versão HTML serve para:

```text
zoom
hover
botões
seletores
sliders
animações
```

A versão PNG serve para:

```text
PDF
README
GitHub
fallback
```

---

# 19. Dependência entre código e artefato

O updater também possui suporte a `depends_on`.

Por exemplo:

```markdown
<!-- figure-include: assignments/01-sorting/artifacts/complexity_plot.html?depends_on=assignments/01-sorting/notebooks/analysis.ipynb -->
<!-- figure-include-end -->
```

A ideia é permitir detectar:

```text
analysis.ipynb
    foi modificado depois
        ↓
complexity_plot.html
    pode estar antigo
```

O updater não recria o gráfico automaticamente; ele apenas reporta que o artefato pode estar stale.

Isso é interessante para manter consistência da entrega.

---

# 20. Gerando o notebook frozen

O notebook de desenvolvimento permanece:

```text
assignments/01-sorting/notebooks/analysis.ipynb
```

Ao finalizar, gere:

```bash
jupyter nbconvert \
    --to html \
    assignments/01-sorting/notebooks/analysis.ipynb \
    --output analysis
```

O `nbconvert` suporta diretamente conversão de `.ipynb` para HTML.

Se o notebook já foi executado e salvo, o HTML preservará os outputs armazenados.

---

# 21. Gerando o frozen HTML com execução nova

Para garantir que todo o notebook seja executado novamente antes da criação do HTML:

```bash
jupyter nbconvert \
    --to html \
    --execute \
    assignments/01-sorting/notebooks/analysis.ipynb \
    --output analysis
```

O `nbconvert` suporta `--execute`, executando o notebook antes da exportação.

Para benchmarks demorados, pode ser necessário ajustar o timeout:

```bash
jupyter nbconvert \
    --to html \
    --execute \
    --ExecutePreprocessor.timeout=-1 \
    assignments/01-sorting/notebooks/analysis.ipynb \
    --output analysis
```

Nesse caso o HTML representa uma execução completa e reproduzível daquele estado do código.

---

# 22. Cuidado importante com o notebook original

Não é necessário sobrescrever o notebook para gerar o HTML.

Prefira:

```text
analysis.ipynb
       ↓
nbconvert --execute
       ↓
analysis.html
```

em vez de executar algum processo que modifique automaticamente o notebook fonte.

Isso mantém separados:

```text
fonte editável

e

artefato frozen
```

---

# 23. Estrutura recomendada de cada algoritmo na apresentação

Para cada algoritmo:

## Slide 1 — conceito

```text
Merge Sort

• divisão e conquista
• divisão recursiva
• merge
• O(n log n)
```

---

## Slide 2 — pseudocódigo

```text
merge_sort(A):

    se |A| <= 1:
        retorna A

    divide A em L e R

    merge_sort(L)
    merge_sort(R)

    merge(L, R)
```

---

## Slide 3 — implementação

```text
                Implementação

     merge_sort.cpp │ merge_sort.py
                    │
       C++          │      Python
                    │
```

---

## Slide 4 — complexidade

```text
Teórico

comparações:
O(n log n)

memória:
O(n)
```

---

## Slide 5 — benchmark

Tabela resumida:

```text
          random   sorted   reverse   repeated

Merge      ...      ...       ...        ...
Quick      ...      ...       ...        ...
Radix      ...      ...       ...        ...
```

---

## Slide 6 — gráfico

Plot interativo:

```text
metric
[comparisons ▼]

algorithm
[merge ▼]

family
[uniform_random ▼]
```

---

## Slide 7 — conclusão

```text
Modelo teórico:
O(n log n)

Resultado experimental:
compatível com n log n

Diferenças Python/C++:
tempo absoluto diferente,
crescimento assintótico semelhante.
```

---

# 24. Classes Marp recomendadas

Além de:

```markdown
<!-- _class: code-compare -->
```

vale criar algumas classes reutilizáveis.

## Código único

```markdown
<!-- _class: code-full -->
```

Visual:

```text
┌──────────────────────────────────────────┐
│                                          │
│              código grande               │
│                                          │
└──────────────────────────────────────────┘
```

---

## Código e resultado

```markdown
<!-- _class: code-result -->
```

Visual:

```text
┌──────────────────────────────┐
│ código                       │
└──────────────────────────────┘

               ↓

┌──────────────────────────────┐
│ resultado                    │
└──────────────────────────────┘
```

---

## Comparação

```markdown
<!-- _class: code-compare -->
```

Visual:

```text
C++                     Python
────────────── │ ──────────────
               │
 código        │ código
               │
```

---

## Resultado central

```markdown
<!-- _class: result -->
```

Visual:

```text
          Resultado experimental

               [GRÁFICO]
```

Isso transforma o tema em uma pequena linguagem visual própria para trabalhos computacionais.

---

# 25. Workflow diário recomendado

Durante o desenvolvimento:

```text
1. editar código
      ↓
2. rodar testes
      ↓
3. executar notebook quando necessário
      ↓
4. salvar notebook
      ↓
5. gerar artifacts
      ↓
6. atualizar Marp
      ↓
7. visualizar slides
```

Na prática:

```bash
uv run pytest
```

depois:

```bash
uv run marp-artifact-updater update \
    assignments/01-sorting/slides/lista.md \
    --repo-root . \
    --apply
```

e:

```bash
npx marp \
    assignments/01-sorting/slides/lista.md \
    --theme assignments/01-sorting/slides/tca.css \
    --preview
```

---

# 26. Workflow final de entrega

Ao terminar uma lista:

```text
                    CÓDIGO FINAL
                         │
                         ▼
                     pytest
                         │
                         ▼
                executar notebook
                         │
                         ▼
                gerar artifacts
                         │
                         ▼
           marp-artifact-updater
                         │
                         ▼
                       check
                         │
                         ▼
             gerar presentation HTML
                         │
                         ▼
                gerar notebook HTML
                         │
                         ▼
                      entrega
```

Checklist:

```text
[ ] testes passam

[ ] notebook executa do início ao fim

[ ] outputs do notebook estão corretos

[ ] gráficos foram regenerados

[ ] marp-artifact-updater check passa

[ ] snippets C++ estão atualizados

[ ] snippets Python estão atualizados

[ ] HTML da apresentação abre

[ ] gráficos interativos funcionam

[ ] HTML frozen do notebook abre

[ ] PDF fallback foi gerado
```

---

# 27. Arquivos que devem ser entregues

Uma entrega completa poderia conter:

```text
01-sorting/
│
├── lista.html
├── lista.pdf
├── analysis.html
│
└── source/
    ├── analysis.ipynb
    ├── merge_sort.cpp
    ├── merge_sort.py
    ├── quick_sort.cpp
    ├── quick_sort.py
    └── ...
```

Ou, se o código já estiver disponível no GitHub:

```text
lista.html
analysis.html
lista.pdf
```

mais o link para o repositório.

---

# 28. Qual arquivo usar em cada situação

| Situação | Arquivo |
|---|---|
| Apresentar em sala | `lista.html` |
| Professor navegar pelos resultados | `analysis.html` |
| Inspecionar código e experimentos | `analysis.ipynb` |
| Conferir rapidamente | `lista.pdf` |
| Desenvolver apresentação | `lista.md` |
| Alterar design | `tca.css` |
| Reproduzir resultados | código + notebook |
| Ver Plotly interativo | HTML |

---

# 29. Relação entre os componentes

É importante manter esta divisão conceitual:

```text
.cpp / .py
     =
implementação

.ipynb
     =
execução + análise

artifacts/
     =
resultados produzidos

lista.md
     =
narrativa da apresentação

tca.css
     =
layout visual

marp-artifact-updater
     =
sincronização

lista.html
     =
apresentação final

analysis.html
     =
registro frozen
```

---

# 30. Regra fundamental: nunca copiar código manualmente

Evitar:

```markdown
```python
def merge_sort(...):
    ...
```
```

quando esse código já existe em:

```text
merge_sort.py
```

Prefira:

```markdown
<!-- snippet-include: assignments/01-sorting/src/python/merge_sort.py#merge-sort -->
...
<!-- snippet-include-end -->
```

Porque uma cópia manual cria duas fontes:

```text
merge_sort.py

e

slide.md
```

que podem divergir.

Com o updater:

```text
merge_sort.py
      │
      └──────► slide.md
```

existe uma única fonte de verdade.

---

# 31. O mesmo vale para o notebook

Se um exemplo está armazenado no notebook:

```text
analysis.ipynb
```

a apresentação deve referenciá-lo:

```markdown
<!-- snippet-include: assignments/01-sorting/notebooks/analysis.ipynb#complexity-estimation -->
...
<!-- snippet-include-end -->
```

Assim:

```text
Notebook
   │
   ├── código executado
   │
   └────► Marp
```

O notebook continua responsável pela execução.

O Marp apenas apresenta um subconjunto do conteúdo.

---

# 32. Filosofia da solução

O sistema passa a ter três níveis.

## Nível 1 — fonte

```text
C++
Python
Notebook
```

É onde o trabalho acontece.

---

## Nível 2 — evidência

```text
CSV
JSONL
PNG
HTML
Plotly
tabelas
```

É o resultado computacional.

---

## Nível 3 — comunicação

```text
Marp
```

É onde os resultados são apresentados.

Portanto:

```text
SOURCE
   ↓
COMPUTATION
   ↓
ARTIFACT
   ↓
PRESENTATION
```

O Marp não precisa executar o trabalho.

Ele apresenta evidências produzidas pelo trabalho.

---

# 33. Resultado final esperado

Ao abrir:

```text
lista.html
```

o professor vê uma apresentação organizada:

```text
────────────────────────────────────────────

             MERGE SORT

────────────────────────────────────────────


           Ideia do algoritmo


────────────────────────────────────────────


       IMPLEMENTAÇÃO

 merge_sort.cpp      │     merge_sort.py
                     │
 void merge_sort()   │     def merge_sort():
 {                   │         ...
     ...             │
 }                   │

────────────────────────────────────────────


       COMPLEXIDADE

           O(n log n)


────────────────────────────────────────────


       BENCHMARK EXPERIMENTAL

            [Plotly]

      zoom / hover / filtros


────────────────────────────────────────────


       CONCLUSÃO

Teoria e experimento apresentam
comportamento compatível com n log n.

────────────────────────────────────────────
```

Enquanto:

```text
analysis.html
```

permanece disponível para quem quiser verificar:

- código completo;
- execução;
- tabelas;
- métodos;
- experimentos;
- parâmetros;
- outputs intermediários;
- análises detalhadas.

---

# 34. Resumo operacional

Durante o desenvolvimento:

```bash
uv run pytest
```

```bash
uv run marp-artifact-updater update \
    assignments/01-sorting/slides/lista.md \
    --repo-root . \
    --apply
```

```bash
npx marp \
    assignments/01-sorting/slides/lista.md \
    --theme assignments/01-sorting/slides/tca.css \
    --preview
```

Antes da entrega:

```bash
uv run marp-artifact-updater check \
    assignments/01-sorting/slides/lista.md \
    --repo-root .
```

Gerar apresentação:

```bash
npx marp \
    assignments/01-sorting/slides/lista.md \
    --theme assignments/01-sorting/slides/tca.css \
    --html \
    -o assignments/01-sorting/dist/lista.html
```

Gerar notebook frozen:

```bash
jupyter nbconvert \
    --to html \
    --execute \
    assignments/01-sorting/notebooks/analysis.ipynb \
    --output analysis
```

O resultado é uma solução em que o código permanece executável, o notebook permanece reproduzível e a apresentação permanece concisa, visual e sincronizada com os artefatos reais do projeto.