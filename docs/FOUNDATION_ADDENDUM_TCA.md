# Projeto TCA — Adendo de Consolidação Arquitetural e Roadmap Operacional

**Complemento ao `docs/FOUNDATION.md`**  
**Versão de consolidação — agosto de 2026**

> Este adendo registra as decisões tomadas após a implementação efetiva da infraestrutura de sorting. O documento fundador permanece como registro da concepção original; quando houver divergência entre uma proposta exploratória anterior e uma decisão consolidada neste adendo, prevalece a decisão mais recente.

---

# Parte XVIII — Consolidação Arquitetural e Roadmap Operacional

## 86. Natureza deste adendo

Este adendo registra decisões tomadas após a implementação efetiva da primeira infraestrutura de sorting.

O documento de fundação permanece como registro da concepção original do projeto. Entretanto, a implementação revelou quais abstrações são realmente necessárias, quais propostas podem ser adiadas e quais devem ser simplificadas.

O objetivo desta consolidação é preservar duas propriedades simultaneamente:

1. manter uma infraestrutura reutilizável para Geometria Computacional e experimentação;
2. impedir que a infraestrutura cresça a ponto de se tornar mais complexa que os próprios problemas acadêmicos estudados.

> **Nova regra de contenção:** nenhuma abstração, dependência ou camada será introduzida apenas porque poderá ser útil no futuro. Ela deverá resolver uma necessidade concreta já observada ou imediatamente necessária no roadmap.

## 87. Princípio de proporcionalidade

O TCA continua sendo uma biblioteca acadêmica incremental, mas não deve se transformar em um framework genérico de experimentação algorítmica.

A infraestrutura deve permanecer subordinada aos algoritmos.

Uma pergunta conceitualmente simples, como “quais algoritmos de sorting estão implementados?”, deve continuar tendo uma resposta simples, mesmo que esses algoritmos também possam ser instrumentados, comparados e visualizados.

A evolução desejada é:

```text
algoritmo
   ↓
infraestrutura mínima necessária
   ↓
experimento / visualização
```

Como regra prática:

- preferir funções simples a hierarquias de classes;
- preferir composição a frameworks internos;
- preferir um arquivo novo apenas quando houver uma responsabilidade nova real;
- evitar abstrações preventivas;
- reutilizar mecanismos já existentes antes de adicionar dependências;
- preservar APIs pequenas e legíveis.

---

# Parte XIX — Estado consolidado do Sorting Core

## 88. Algoritmos atualmente incorporados

O núcleo de sorting utilizado para validar a arquitetura é composto por:

```text
Selection Sort
Insertion Sort
Merge Sort
Quick Sort
Radix Sort
```

Cada algoritmo possui:

- uma implementação Python de referência;
- uma implementação C++;
- testes de correção;
- comparação entre backends quando aplicável;
- instrumentação de operações algorítmicas.

O registro de algoritmos é automatizado sempre que possível. Adicionar um novo algoritmo não deve exigir manutenção manual de listas repetidas em bindings, CMake, API, testes ou catálogos.

## 89. Uma implementação por backend

Permanece congelado o princípio:

> **um corpo Python e um corpo C++ por algoritmo.**

Não existem versões paralelas como `merge_sort.py`, `merge_sort_instrumented.py` ou `merge_sort_animated.py`.

A observabilidade é determinada pela política de execução.

Em Python:

```text
DirectProbe  → execução direta
Probe        → métricas
TraceProbe   → métricas + eventos
```

A lógica algorítmica permanece a mesma.

## 90. API pública de sorting

A entrada principal permanece:

```python
sort(
    values,
    method=...,
    backend=...,
    metrics=...,
    trace=...,
)
```

Os backends públicos são `python` e `cpp`.

O contrato numérico do backend C++ permanece:

```text
NumPy
float64
1 dimensão
C-contiguous
```

O uso normal não exige que o usuário conheça bindings, registries ou implementações internas.

---

# Parte XX — Instrumentação consolidada

## 91. Metrics atualmente implementadas

A instrumentação efetivamente consolidada para sorting utiliza:

```text
comparisons
swaps
writes
```

### `comparisons`

Comparações entre chaves que participam da decisão algorítmica.

### `swaps`

Trocas explícitas entre duas posições diferentes. Uma troca de uma posição consigo mesma não é contabilizada.

### `writes`

Escritas lógicas realizadas pelo algoritmo, inclusive em buffers auxiliares quando estes fazem parte da formulação. Uma troca real implica duas escritas.

Outras métricas propostas originalmente, como `function_calls`, `max_recursion_depth`, `auxiliary_bytes_peak`, `inclusive_time` e `exclusive_time`, não fazem parte do núcleo atual. Permanecem possibilidades futuras, mas só serão implementadas se uma atividade concreta justificar seu custo.

## 92. Trace canônico em Python

O projeto adotou uma simplificação importante:

> **o Trace completo é canônico no backend Python.**

Assim:

```text
Python
    execução direta
    métricas
    trace/replay

C++
    execução direta
    métricas
    benchmark
```

A API rejeita explicitamente uma solicitação de Trace no backend C++.

Essa decisão evita transporte de grandes sequências de eventos via pybind11, duplicação da infraestrutura de visualização, complexidade de serialização prematura e acoplamento desnecessário entre frontend didático e backend de performance.

Python e C++ continuam comparáveis por resultado e Metrics.

## 93. Modelo de evento

O Trace utiliza eventos estruturados:

```python
TraceEvent(
    kind=...,
    indices=...,
    values=...,
    data=...,
)
```

Há duas categorias principais.

### Eventos operacionais

```text
compare
swap
write
```

São produzidos pelo próprio `TraceProbe`.

### Eventos semânticos

Atualmente:

```text
Selection Sort → select_minimum
Insertion Sort → select_key
Merge Sort     → merge_range
Quick Sort     → choose_pivot, partition
Radix Sort     → radix_pass
```

Operações genéricas permitem reconstruir mudanças de estado; eventos semânticos permitem explicar o algoritmo.

## 94. Destino de escritas

Eventos `write` podem indicar seu destino lógico, por exemplo:

```text
values
buffer
indices
ordered_values
```

Isso permite distinguir uma alteração do estado principal de uma operação em estrutura auxiliar sem alterar a definição da métrica `writes`.

---

# Parte XXI — Replay genérico

## 95. Separação entre Trace e Replay

O projeto distingue explicitamente:

```text
Trace         → o que aconteceu?
Replay        → em qual ponto da execução estamos?
Visualization → como representar visualmente esse ponto?
```

O Replay não conhece sorting.

Seu núcleo reside em:

```text
src/tca/core/replay.py
```

E trabalha genericamente com:

```text
initial_state
events
reducer
```

A relação fundamental é:

\[
S_{t+1} = R(S_t, e_t)
\]

onde `S_t` é o estado, `e_t` é um evento e `R` é um reducer específico do domínio.

## 96. Navegação temporal

O Replay mantém frames independentes e permite:

```python
replay.current
replay.state
replay.position
replay.total_steps
replay.finished

replay.next()
replay.previous()
replay.seek(step)
replay.reset()
```

A navegação para trás não exige inverter operações. Os estados são reconstruídos antecipadamente para exemplos didáticos pequenos.

## 97. Reducers específicos de domínio

A interpretação dos eventos pertence ao domínio.

Para sorting:

```text
TraceEvent
    ↓
sorting_reducer
    ↓
SortingState
```

O `SortingState` contém atualmente:

```text
values
Metrics acumuladas
```

Assim, qualquer frame pode fornecer simultaneamente estado do vetor, evento atual, comparações acumuladas, swaps acumulados, writes acumulados e posição no replay.

## 98. Reutilização futura em Geometria Computacional

A principal razão para manter o Replay genérico é permitir:

```text
Sorting
    Trace
      ↓
SortingReducer
      ↓
SortingState

Geometria Computacional
    Trace
      ↓
GeometryReducer
      ↓
GeometryState
```

Exemplos de eventos geométricos futuros:

```text
select_point
orientation_test
candidate_point
accept_point
reject_point
add_edge
remove_edge
segment_intersection
edge_flip
move_sweep_line
```

Possíveis estados:

```text
points
segments
active_points
active_edges
candidate
hull
sweep_line
```

A implementação desses elementos não é requisito atual. O compromisso atual é apenas que o núcleo de Replay não impeça essa evolução.

---

# Parte XXII — Visualização

## 99. Objetivos

A camada de visualização deverá permitir, no mínimo:

- inspeção passo a passo;
- avanço e retorno;
- acesso direto a uma etapa;
- play e pause;
- slider temporal;
- destaque dos elementos relevantes;
- exibição das Metrics acumuladas;
- descrição do evento atual.

A visualização deve consumir o Replay e não reexecutar o algoritmo.

## 100. Tecnologia preferencial

A solução preferencial inicial será:

```text
Plotly Graph Objects
```

A escolha busca minimizar infraestrutura.

Não serão introduzidos inicialmente:

```text
Dash
Streamlit
Solara
NiceGUI
ipywidgets
ipympl
ipycanvas
```

Plotly deverá ser suficiente para sorting, Geometria Computacional, animação, interação, notebooks e HTML interativo sem transformar o TCA em uma aplicação web.

## 101. Infraestrutura visual mínima

Não será criada preventivamente uma hierarquia de `BaseRenderer`, `ReplayController`, `SortingController`, `GeometryController`, `WidgetAdapter` ou `FrontendAdapter`.

A primeira implementação deverá ser pequena:

```text
src/tca/visualization/
    sorting.py
```

Esse módulo deverá converter:

```text
Sorting Replay
      ↓
Plotly Figure
```

Quando Geometria Computacional realmente exigir visualização:

```text
src/tca/visualization/
    sorting.py
    geometry.py
```

Somente depois de existir duplicação concreta entre esses módulos deverá ser avaliada a extração de uma abstração compartilhada.

---

# Parte XXIII — Decisões específicas dos algoritmos atuais

## 102. Merge Sort

Variante consolidada:

```text
top-down
recursiva
estável
buffer auxiliar único O(n)
reutilizado durante toda a execução
```

A instrumentação contabiliza comparações entre chaves, writes no buffer e writes de retorno ao vetor. Merge Sort não realiza swaps explícitos.

Para tamanhos potência de dois:

\[
writes = 2n\log_2 n
\]

## 103. Quick Sort

A implementação possui duas dimensões configuráveis.

### Estratégia de pivô

```text
first
quarter
random
```

`quarter` representa uma posição correspondente a aproximadamente um quarto do intervalo, e não um quartil estatístico dos valores.

### Estratégia de recursão

```text
classic
bounded
```

`classic` executa a formulação recursiva convencional.

`bounded` recorre no menor subproblema e continua iterativamente no maior, limitando a profundidade da pilha mesmo quando as partições são ruins.

Configuração padrão:

```text
pivot = first
recursion = bounded
```

Essa escolha protege a pilha, mas não altera a possibilidade de tempo quadrático para entradas desfavoráveis.

## 104. PRNG determinístico do projeto

O projeto possui um PRNG reutilizável próprio, atualmente baseado em SplitMix64, com comportamento equivalente entre Python e C++.

Ele é utilizado pelo Quick Sort de pivô aleatório e poderá ser reutilizado quando houver necessidade concreta.

Dataset RNG e algorithm RNG continuam sendo conceitos distintos.

## 105. Radix Sort para `float64`

O Radix Sort atual utiliza uma ordenação por chave decimal quantizada:

```text
truncate(value × 10^digits)
```

com `digits = 3` por padrão.

A operação é truncamento em direção a zero, não arredondamento.

Os valores originais não são substituídos pelas chaves. O algoritmo ordena uma permutação estável de índices e aplica essa permutação aos valores ao final.

Características:

```text
LSD
base 10
estável
suporta valores negativos
comparisons = 0
swaps = 0
```

Valores diferentes que produzam a mesma chave quantizada preservam sua ordem relativa original. Portanto, o contrato do Radix é uma ordenação segundo a chave quantizada, e não necessariamente a ordem total exata dos `float64`.

---

# Parte XXIV — Roadmap consolidado de Sorting

## 106. Milestones concluídos

### M0 — Baseline e invariantes
Concluído.

### M1 — Merge Sort
Concluído.

### M2 — Quick Sort
Concluído, incluindo estratégias de pivô, recursão bounded e PRNG determinístico reutilizável.

### M3 — Radix Sort
Concluído, incluindo quantização decimal reutilizável, estabilidade, negativos e paridade Python/C++.

### M4 — Trace
Concluído, incluindo `Trace`, `TraceEvent`, `TraceProbe`, `make_probe`, eventos operacionais e eventos semânticos.

### M5.1 — Trace na API pública
Concluído.

### M5.2 — Execução traçada de alto nível
Concluído. A API oferece resultado autocontido contendo `initial_values`, `final_values`, `Metrics` e `Trace`.

### M5.3 — Replay genérico
Concluído.

### M5.4 — Reducer de sorting
Concluído.

### M5.5 — Metrics por frame
Concluído.

## 107. Próximo milestone imediato

### M5.6 — Visualização interativa

Objetivo:

```text
Sorting Replay
      ↓
Plotly Figure
```

Requisitos mínimos:

- barras representando o vetor;
- evento atual;
- elementos ativos destacados;
- Metrics acumuladas;
- slider;
- play;
- pause;
- inspeção passo a passo.

A implementação deverá ser deliberadamente pequena. Não será criado um frontend independente, servidor ou framework web.

---

# Parte XXV — Roadmap experimental

## 108. M6 — Datasets reproduzíveis

Após a visualização básica, o foco passa à experimentação.

Tamanhos previstos:

```text
n = 10^k
k = 0, 1, ..., 6
```

Famílias:

```text
uniform
sorted
reverse
nearly_sorted
nearly_reverse
many_duplicates
all_equal
```

A quantidade definitiva de replicações deverá permanecer configurável. A campanha deve usar seeds fixas e reconstruíveis.

## 109. Família `many_duplicates`

A política experimental preferida evolui de uma cardinalidade fixa para uma cardinalidade dependente do tamanho:

\[
\text{distinct}(n) \approx \sqrt{n}
\]

A definição exata deverá ser congelada antes da campanha formal.

## 110. M7 — Schema e persistência de resultados

Objetivo:

- formalizar linhas brutas dos experimentos;
- registrar IDs;
- preservar seeds;
- guardar configurações;
- permitir reanálise sem rerodar a campanha.

Resultados brutos devem ser preservados antes de qualquer agregação estatística.

## 111. M8 — Timing e Metrics

As duas medições serão executadas separadamente.

### TIME

```text
DirectProbe
sem Trace
sem Metrics
```

### METRICS

```text
Probe
tempo descartado
```

O tempo de uma execução instrumentada não será reportado como benchmark do algoritmo.

## 112. M9 — Memória

A memória de processo deverá ser medida isoladamente. A execução de memória não será misturada com TIME, METRICS ou TRACE quando isso introduzir interferência mensurável.

## 113. M10 — Orquestração e cutoff

A campanha precisa reconhecer que algoritmos quadráticos não são praticáveis até `10^6`.

O runner deverá suportar cutoff granular por:

```text
algorithm
backend
family
```

Os resultados devem registrar explicitamente estados como executado, interrompido, timeout ou não aplicável.

## 114. M11 — Pilot

Antes da campanha completa será executado um estudo piloto para definir empiricamente:

- warmups;
- número de repetições temporais;
- timeout;
- comportamento dos cutoffs;
- volume dos resultados;
- custo total previsto da campanha.

## 115. M12 — Campanha completa

A campanha completa utilizará datasets, configuração, seeds e protocolo congelados pelo pilot.

Cada algoritmo/backend deve receber a mesma instância base de dados em uma combinação experimental equivalente.

## 116. M13 — Notebook e apresentação de resultados

O notebook será consumidor dos resultados persistidos.

Não deverá conter implementações autoritativas, geração manual não reproduzível de datasets, benchmark ad hoc escondido em células ou lógica que só exista no notebook.

Deverá concentrar explicação, inspeção, visualização, estatística, comparações e interpretação.

---

# Parte XXVI — Modalidades de execução

## 117. Separação operacional

A infraestrutura passa a reconhecer explicitamente quatro finalidades:

```text
NORMAL
TIME
METRICS
TRACE
```

- **NORMAL:** uso convencional da biblioteca.
- **TIME:** benchmark temporal com `DirectProbe`, sem coleta adicional.
- **METRICS:** contagem semântica com `Probe`.
- **TRACE:** demonstração, inspeção e animação com `TraceProbe`, pequenos exemplos e backend Python.

Essas modalidades representam uma regra metodológica e não precisam necessariamente se tornar um enum ou nova API pública.

## 118. Invariante experimental

Nenhum experimento deverá inferir performance temporal a partir de uma execução TRACE. Da mesma forma, uma execução dedicada a medir memória não deve ser usada automaticamente como observação oficial de tempo.

```text
mesmo algoritmo
mesmo dataset
      │
      ├── TIME
      ├── METRICS
      ├── MEMORY
      └── TRACE
```

Cada execução responde a uma pergunta diferente.

---

# Parte XXVII — Testes como proteção arquitetural

## 119. Testes registry-driven

Sempre que uma propriedade deve valer para todos os algoritmos, os testes devem preferencialmente utilizar:

```python
available_sorting_algorithms()
```

em vez de repetir manualmente nomes de algoritmos.

Testes específicos continuam apropriados para estabilidade, fórmulas de comparações/writes, estratégia de pivô, quantização e eventos semânticos.

## 120. Estado de validação desta revisão

Na consolidação deste adendo, a suíte contém:

```text
315 testes aprovados
```

A quantidade exata naturalmente evoluirá. O número de testes não é uma meta em si; funciona apenas como fotografia do nível de validação existente neste ponto do projeto.

---

# Parte XXVIII — Critério para crescimento futuro

## 121. Regra de três perguntas

Antes de adicionar uma nova ferramenta, abstração ou camada, deverão ser respondidas três perguntas:

1. **qual necessidade atual ela resolve?**
2. **o que já existe não consegue resolver isso de forma suficientemente simples?**
3. **o custo permanente de manter essa nova peça é proporcional ao benefício?**

Se as respostas não justificarem a inclusão, a decisão padrão será:

```text
não adicionar ainda
```

## 122. Preferência por poucas ferramentas

O projeto deverá preferir uma ferramenta que cubra satisfatoriamente vários casos a uma coleção de ferramentas especializadas.

Exemplo atual:

```text
Plotly
```

é preferido como primeira solução de visualização porque pode atender sorting, Geometria Computacional, animação, interação, notebooks e HTML sem introduzir um framework web adicional.

Isso não transforma Plotly em decisão irrevogável. Significa apenas que uma segunda tecnologia visual deverá demonstrar uma necessidade concreta não atendida pela primeira.

## 123. Definition of Done revisada para infraestrutura

Uma capacidade estrutural está concluída quando:

- resolve o requisito que motivou sua criação;
- possui testes proporcionais;
- possui API pequena;
- não exige conhecimento de detalhes internos para uso cotidiano;
- não cria trabalho repetitivo ao adicionar novos algoritmos;
- possui um caminho plausível de reutilização quando essa reutilização já é relevante;
- pode permanecer sem novas abstrações até aparecer uma necessidade concreta.

> **Infraestrutura concluída é infraestrutura que pode parar de crescer.**

---

# Apêndice C — Estado arquitetural consolidado

A arquitetura efetivamente adotada para sorting pode ser resumida por:

```text
                     ┌──────── Python reference ────────┐
                     │                                  │
values ──→ sort() ───┤                                  ├──→ resultado
                     │                                  │
                     └──────── C++ / pybind11 ──────────┘
                                      │
                                      │
                        resultado + Metrics
```

No backend Python:

```text
                    ┌─ DirectProbe ─→ execução
Algorithm body ─────┼─ Probe ───────→ Metrics
                    └─ TraceProbe ──→ Metrics + Trace
```

Para demonstração:

```text
Algorithm
    ↓
Trace
    ↓
Replay genérico
    ↓
SortingReducer
    ↓
SortingState
    ↓
Plotly
```

Futuramente, para Geometria Computacional:

```text
Geometry Algorithm
       ↓
     Trace
       ↓
Replay genérico
       ↓
GeometryReducer
       ↓
 GeometryState
       ↓
     Plotly
```

O componente compartilhado não é o algoritmo nem o renderer. É a ideia de:

\[
\text{estado inicial}
+
\text{sequência de eventos}
+
\text{reducer}
\rightarrow
\text{execução reproduzível}
\]

Essa passa a ser a principal ponte arquitetural entre a infraestrutura validada em sorting e a futura etapa de Geometria Computacional.
