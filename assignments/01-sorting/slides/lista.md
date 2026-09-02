---
marp: true
theme: tca
paginate: true
html: true
---

# Técnicas Computacionais Avançadas

## Lista 01 — Algoritmos de Ordenação

Aluno: Igor de Melo Nery Oliveira  
Matrícula: 2025109640  
Data: Setembro, 2026.

---

## Do algoritmo ao experimento

Implementei e comparei seis estratégias de ordenação em **Python** e **C++**.

- Dados reproduzíveis, sete tamanhos e sete famílias de entrada;
- Medições separadas de tempo, memória e operações elementares;
- Visualização passo a passo para tornar as estratégias observáveis.

---

## Extensão da atividade

O projeto estende propositalmente o pedido da lista para investigar:

- memória, além do tempo e das operações;
- diferenças entre C++ e Python;
- uma visualização HTML do passo a passo dos algoritmos.

A intenção é manter essa análise comparativa nas tarefas posteriores da disciplina.

---

## Algoritmos implementados

| Método | Resumo |
| --- | --- |
| **Selection** | Seleciona o menor elemento restante; O(n²). |
| **Insertion** | Insere a chave; próximo de O(n) em dados ordenados. |
| **Merge Smarter** | Intercala com buffer reutilizado; O(n log n). |
| **Quick Classic** | Primeiro pivô; pode degradar em entradas ordenadas. |
| **Quick Smarter** | Pivô pseudoaleatório e recursão limitada. |
| **Radix Decimal** | LSD sem comparações entre elementos. |

---

## Visualização das estratégias

<iframe src="../artifacts/sorting_comparison.html" title="Comparação animada dos algoritmos de ordenação" style="width: 100%; height: 300px; border: 0;"></iframe>

Os seis métodos ordenam a mesma entrada de 16 elementos, com valores repetidos. A animação é didática e não integra o benchmark. Melhor visualizado em <a href="../artifacts/sorting_comparison.html" target="_blank">AQUI</a>.

---

## Famílias de entrada

| Família | Construção | O que ela evidencia |
| --- | --- | --- |
| `uniform_random` | Valores quantizados. | Caso geral. |
| `sorted`, `reverse_sorted`, `nearly_sorted`, `nearly_reverse_sorted` | Ordem crescente, decrescente ou com pequenas trocas. | Adaptação à ordem inicial e escolha do pivô. |
| `many_repeated`, `all_equal` | Muitas chaves repetidas ou uma única chave. | Tratamento de repetições. |

---

## Campanha de análise

**7 tamanhos × 7 famílias × 5 repetições = 245 casos**

Tamanhos: 1, 10, 10², 10³, 10⁴, 10⁵ e 10⁶.

**245 casos × 6 métodos × 2 backends × 3 medições = 8.820 execuções**

Os resultados são persistidos incrementalmente, permitindo retomar uma campanha interrompida.

---

## Métricas de análise

- **Tempo:** média de `elapsed_seconds` em cinco repetições.
- **Memória:** média do pico adicional de memória.
- **Telemetria:** `comparisons`, `swaps` e `writes`.

As medições são independentes para não instrumentar o tempo normal. Linhas contínuas representam Python; tracejadas, C++.

---

<!-- _class: theoretical-table -->

## Complexidade teórica esperada

| Família | Selection | Insertion | Merge<br>Smarter | Quick<br>Classic | Quick<br>Smarter | Radix* |
| --- | --- | --- | --- | --- | --- | --- |
| `uniform_random` | n² | n² | n log n | n log n | n log n | n |
| `sorted` | n² | n | n log n | n² | n log n | n |
| `reverse_sorted` | n² | n² | n log n | n² | n log n | n |
| `nearly_sorted` | n² | n | n log n | n² | n log n | n |
| `nearly_reverse_sorted` | n² | n² | n log n | n² | n log n | n |
| `many_repeated` | n² | n² | n log n | n log n | n log n | n |
| `all_equal` | n² | n | n log n | n log n | n log n | n |

\* Com dígitos decimais limitados. Quick Smarter: n log n esperado; o pior caso do Quick continua n².

---

## Resultados da campanha

<!-- figure-include: assignments/01-sorting/artifacts/sorting_results.html?height=300&title=Resultados%20da%20campanha&depends_on=assignments/01-sorting/solucao.ipynb -->
<iframe src="../artifacts/sorting_results.html" width="100%" height="300" title="Resultados da campanha" frameborder="0"></iframe>
<!-- figure-include-end -->

Melhor visualizado em <a href="../artifacts/sorting_results.html" target="_blank">AQUI</a>.

---

## Análise dos resultados — efeito da entrada

- **Selection** mantém aproximadamente n(n − 1)/2 comparações: é o mais lento de forma sistemática e quase não reage à organização inicial.
- **Insertion** é o mais rápido em `sorted`, `nearly_sorted` e `all_equal`; em entradas aleatórias ou inversas, os deslocamentos o levam de volta ao comportamento O(n²).
- **Quick Classic** é rápido em `uniform_random`, mas a escolha fixa do primeiro pivô gera partições degeneradas em entradas ordenadas, inversas e próximas desses casos.
- **Quick Smarter** e **Merge Smarter** são os métodos mais regulares entre as famílias; a estratégia de pivô e recursão torna o Quick Smarter robusto onde o Classic falha.

---

## Análise dos resultados — recursos e implementação

- **Memória:** Radix apresentou o maior pico adicional em todas as famílias, seguido pelo Merge; ambos usam estruturas auxiliares proporcionais a n.
- **Python × C++:** para n = 100.000, os ganhos medianos medidos foram **66×** no Selection, **99×** no Quick Classic e **990×** no Insertion.
- **Merge Smarter:** usa um único buffer auxiliar O(n) e preserva o comportamento n log n independentemente da ordem inicial. É uma escolha consistente quando se aceita essa memória adicional previsível.
- **Quick:** pode usar menos memória auxiliar, mas o Classic sofre partições degeneradas: os resultados registram `RecursionError` em Python e *stack overflow* em C++. O Smarter reduz esse risco com pivô pseudoaleatório e recursão limitada, sem eliminar o pior caso teórico.

---

<!-- _class: family-winners -->

## Conclusão — melhor tempo por família

Backend C++, n = 100.000; média de cinco execuções.

<!-- figure-include: assignments/01-sorting/artifacts/family_winners.html?height=250&title=Melhor%20tempo%20por%20fam%C3%ADlia&depends_on=assignments/01-sorting/solucao.ipynb -->
<iframe src="../artifacts/family_winners.html" width="100%" height="250" title="Melhor tempo por família" frameborder="0"></iframe>
<!-- figure-include-end -->

Insertion vence entradas ordenadas; Quick Classic, aleatórias e repetidas; Quick Smarter, inversas. A escolha acompanha a estrutura da entrada.

---

## ANEXOS

> Code Snippets e detalhes de implementação

---

<!-- _class: code-compare -->

### Selection Sort

##### C++

##### Python

<!-- snippet-include: cpp/src/algorithms/sorting/selection_sort.cpp#selection-sort -->
```cpp
template <typename ProbeType>
void selection_sort_impl(std::span<double> values, ProbeType& probe) {
    for (std::size_t index_i = 0; index_i < values.size(); ++index_i) { // i=(0)..(n-1)
        std::size_t marker = index_i;                                   // m=i

        for (std::size_t index_j = index_i + 1; index_j < values.size();
             ++index_j) {                                    // j=(i+1)..(n)
            if (probe.lt(values[index_j], values[marker])) { // se xj < xm
                marker = index_j;                            // m=j
            }
        }

        probe.swap(values, index_i, marker); // swap(x_i, x_m)
    }
}
```
<!-- snippet-include-end -->

<!-- snippet-include: src/tca/reference/sorting/selection_sort.py#selection-sort -->
```python
def selection_sort(
    values,
    metrics: Metrics | None = None,
    trace: Trace | None = None,
) -> None:
    probe = make_probe(metrics, trace)

    for index_i in range(len(values) - 1):  # i=(1)..(n-1)
        marker = index_i  # m=i

        probe.event(
            "select_minimum",
            indices=(marker,),
            values=(values[marker],),
        )  # mínimo atual m=i

        for index_j in range(index_i + 1, len(values)):  # j=(i+1)..(n)
            if probe.lt(
                values[index_j],
                values[marker],
                indices=(index_j, marker),
                roles=("current", "marker"),
            ):  # se x_j < x_m
                marker = index_j  # m=j

                probe.event(
                    "select_minimum",
                    indices=(marker,),
                    values=(values[marker],),
                )  # novo mínimo m=j

        probe.swap(values, index_i, marker)  # swap(x_i, x_m)
```
<!-- snippet-include-end -->

---

<!-- _class: code-compare -->

### Insertion Sort

##### C++

##### Python

<!-- snippet-include: cpp/src/algorithms/sorting/insertion_sort.cpp#insertion-sort -->
```cpp
template <typename ProbeType>
void insertion_sort_impl(std::span<double> values, ProbeType& probe) {
    for (std::size_t index_i = 1; index_i < values.size(); ++index_i) { // i=(1)..(n-1)
        const double value_marker = values[index_i];                    // v = xi
        std::size_t index_j = index_i;                                  // j = i

        while (index_j > 0 &&
               probe.lt(value_marker, values[index_j - 1]) // enquanto x_{j-1} > v
        ) {
            probe.write(values, index_j, values[index_j - 1]); // x_j = x_{j-1}
            --index_j;                                         // j = j - 1
        }

        probe.write(values, index_j, value_marker); // x_j = v
    }
}
```
<!-- snippet-include-end -->

<!-- snippet-include: src/tca/reference/sorting/insertion_sort.py#insertion-sort -->
```python
def insertion_sort(
    values,
    metrics: Metrics | None = None,
    trace: Trace | None = None,
) -> None:
    probe = make_probe(metrics, trace)

    for index_i in range(1, len(values)):  # i=(1)..(n-1)
        value_marker = values[index_i]  # v = x_i
        index_j = index_i  # j = i

        probe.event(
            "select_key",
            indices=(index_i,),
            values=(value_marker,),
        )  # seleciona v = x_i

        while index_j > 0 and probe.lt(
            value_marker,
            values[index_j - 1],
            indices=(index_i, index_j - 1),
            roles=("key", "current"),
        ):  # enquanto x_{j-1} > v
            probe.write(values, index_j, values[index_j - 1])  # x_j = x_{j-1}
            index_j -= 1  # j = j - 1

        probe.write(values, index_j, value_marker)  # x_j = v
```
<!-- snippet-include-end -->

---

<!-- _class: code-compare -->

### Merge Sort — Separação

##### C++

##### Python

<!-- snippet-include: cpp/src/algorithms/sorting/merge_sort.cpp#merge-sort -->
```cpp
template <typename ProbeType>
void merge_sort_recursive(std::span<double> values, std::span<double> buffer,
                          std::size_t start, std::size_t end, ProbeType& probe,
                          const tca::algorithms::MergeSortOptions& options) {

    if (end - start < 2) { // se n < 2 então retorne {caso básico da recursão}
        return;
    }

    const std::size_t middle = (start + end) / 2; // m = n/2

    merge_sort_recursive(values, buffer, start, middle, probe,
                         options); // mergesort(l, m) {recursão esquerda}

    merge_sort_recursive(values, buffer, middle, end, probe,
                         options); // mergesort(r, n-m) {recursão direita}

    if (options.buffer == tca::algorithms::MergeBuffer::Local) {
        std::vector<double> local_buffer(end - start);

        merge(values, std::span<double>{local_buffer}, // aloca buffer local
              start, start, middle, end,
              probe); // {combinação classic}

    } else {
        merge(values,
              buffer, // usa buffer único reutilizado
              0, start, middle, end,
              probe); // {combinação smarter}
    }
}
```
<!-- snippet-include-end -->

<!-- snippet-include: src/tca/reference/sorting/merge_sort.py#merge-sort -->
```python
def _merge_sort(
    values,
    buffer,
    start: int,
    end: int,
    probe,
    buffer_strategy: str,
) -> None:
    if end - start < 2:  # se n < 2 então retorne {caso básico da recursão}
        return

    middle = (start + end) // 2  # m = n/2

    _merge_sort(
        values,
        buffer,
        start,
        middle,
        probe,
        buffer_strategy,
    )  # mergesort(l, m) {recursão esquerda}

    _merge_sort(
        values,
        buffer,
        middle,
        end,
        probe,
        buffer_strategy,
    )  # mergesort(r, n-m) {recursão direita}

    probe.event(
        "merge_range",
        indices=(start, middle, end),
    )  # combina [start..middle) com [middle..end)

    _merge(
        values,
        buffer,
        start,
        middle,
        end,
        probe,
        buffer_strategy,
    )  # {combinação}
```
<!-- snippet-include-end -->

---

<!-- _class: code-compare -->

### Merge Sort — Combinação

##### C++

##### Python

<!-- snippet-include: cpp/src/algorithms/sorting/merge_sort.cpp#merge-sort-combine -->
```cpp
template <typename ProbeType>
void merge(std::span<double> values, std::span<double> buffer,
           std::size_t buffer_offset, std::size_t start, std::size_t middle,
           std::size_t end, ProbeType& probe) {
    for (std::size_t index_k = start; index_k < end; ++index_k) {
        const std::size_t index_buffer = index_k - buffer_offset;

        probe.write(buffer, index_buffer,
                    values[index_k]); // l = x[start..m], r = x[m..end] {separação}
    }

    std::size_t index_l = start;  // i = 1
    std::size_t index_r = middle; // j = 1

    for (std::size_t index_k = start; index_k < end; ++index_k) {
        // para k = 1..n {combinação}

        const std::size_t index_buffer_l = index_l - buffer_offset;
        const std::size_t index_buffer_r = index_r - buffer_offset;

        if (index_l >= middle) {
            probe.write(values, index_k,
                        buffer[index_buffer_r]); // x_k = r_j
            ++index_r;                           // j = j+1

        } else if (index_r >= end) {
            probe.write(values, index_k,
                        buffer[index_buffer_l]); // x_k = l_i
            ++index_l;                           // i = i+1

        } else if (probe.lt(buffer[index_buffer_r],
                            buffer[index_buffer_l])) { // se r_j < l_i então
            probe.write(values, index_k,
                        buffer[index_buffer_r]); // x_k = r_j
            ++index_r;                           // j = j+1

        } else {
            probe.write(values, index_k,
                        buffer[index_buffer_l]); // x_k = l_i
            ++index_l;                           // i = i+1
        }
    }
}
```
<!-- snippet-include-end -->

<!-- snippet-include: src/tca/reference/sorting/merge_sort.py#merge-sort-combine -->
```python
def _merge(
    values,
    buffer,
    start: int,
    middle: int,
    end: int,
    probe,
    buffer_strategy: str,
) -> None:
    if buffer_strategy == "local":
        working_buffer = [None] * (end - start)  # buffer local {classic}
        buffer_offset = start

    else:
        working_buffer = buffer  # buffer único reutilizado {smarter}
        buffer_offset = 0

    for index_k in range(start, end):
        index_buffer = index_k - buffer_offset

        probe.write(
            working_buffer,
            index_buffer,
            values[index_k],
            target="buffer",
        )  # l = x[start..m], r = x[m..end] {separação}

    index_l = start  # i = 1
    index_r = middle  # j = 1

    for index_k in range(start, end):  # para k = 1..n {combinação}
        index_buffer_l = index_l - buffer_offset
        index_buffer_r = index_r - buffer_offset

        if index_l >= middle:
            probe.write(
                values,
                index_k,
                working_buffer[index_buffer_r],
                target="values",
            )  # x_k = r_j
            index_r += 1  # j = j+1

        elif index_r >= end:
            probe.write(
                values,
                index_k,
                working_buffer[index_buffer_l],
                target="values",
            )  # x_k = l_i
            index_l += 1  # i = i+1
        elif probe.lt(
            working_buffer[index_buffer_r],
            working_buffer[index_buffer_l],
            indices=(index_r, index_l),
            roles=("right", "left"),
        ):  # se r_j < l_i então
            probe.write(
                values,
                index_k,
                working_buffer[index_buffer_r],
                target="values",
            )  # x_k = r_j
            index_r += 1  # j = j+1

        else:
            probe.write(
                values,
                index_k,
                working_buffer[index_buffer_l],
                target="values",
            )  # x_k = l_i
            index_l += 1  # i = i+1
```
<!-- snippet-include-end -->

---

## Merge Smarter — escolha de memória

- O buffer auxiliar é criado uma única vez na chamada pública e compartilhado por toda a recursão.
- Cada chamada trabalha apenas no intervalo `[start, end)` do vetor; os limites e o deslocamento no buffer substituem a criação de subvetores.
- As subpartições de uma mesma etapa são disjuntas e as chamadas recursivas ocorrem sequencialmente. Assim, um único buffer é suficiente quando as funções respeitam seus intervalos de leitura e escrita.
- Em comparação ao **Merge Classic**, a complexidade espacial continua O(n), mas são evitadas alocações temporárias repetidas durante as intercalações.

---

## Merge Classic × Merge Smarter — tempo

`uniform_random`, n = 100.000, média de cinco repetições:

| Backend | Classic — tempo | Smarter — tempo | Ganho do Smarter |
| --- | ---: | ---: | ---: |
| Python | 0,525 s | **0,489 s** | 6,9% |
| C++ | 0,0106 s | **0,0083 s** | 21,8% |

As comparações e escritas são essencialmente as mesmas. O ganho do Smarter vem de reduzir a recorrência de alocações temporárias.

---

<!-- _class: code-compare -->

### Quick Sort — Recursão

##### C++

##### Python

<!-- snippet-include: cpp/src/algorithms/sorting/quick_sort.cpp#quick-sort -->
```cpp
template <typename ProbeType>
void quick_sort_recursive(std::span<double> values, std::size_t index_r,
                          std::size_t index_s, ProbeType& probe,
                          const tca::algorithms::QuickSortOptions& options,
                          tca::PRNG& prng) {
    while (index_r < index_s) { // enquanto s > r
        const std::size_t index_j =
            partition(values, index_r, index_s, probe, options.pivot, prng);

        if (options.recursion == tca::algorithms::QuickRecursion::Classic) {
            if (index_j > index_r) {
                quick_sort_recursive(values, index_r, index_j - 1, probe, options,
                                     prng);
            }

            if (index_j < index_s) {
                quick_sort_recursive(values, index_j + 1, index_s, probe, options,
                                     prng);
            }

            return;
        }

        const std::size_t left_size = index_j - index_r;
        const std::size_t right_size = index_s - index_j;

        if (left_size < right_size) {
            if (index_j > index_r) {
                quick_sort_recursive(values, index_r, index_j - 1, probe, options,
                                     prng);
            }

            index_r = index_j + 1; // continua iterativamente pela direita

        } else {
            if (index_j < index_s) {
                quick_sort_recursive(values, index_j + 1, index_s, probe, options,
                                     prng);
            }

            index_s = index_j - 1; // continua iterativamente pela esquerda
        }
    }
}
```
<!-- snippet-include-end -->

<!-- snippet-include: src/tca/reference/sorting/quick_sort.py#quick-sort -->
```python
def _quick_sort(
    values,
    index_r: int,
    index_s: int,
    probe,
    pivot: str,
    recursion: str,
    prng: PRNG,
) -> None:
    while index_r < index_s:  # enquanto s > r
        index_j = _partition(values, index_r, index_s, probe, pivot, prng)

        if recursion == "classic":
            _quick_sort(values, index_r, index_j - 1, probe, pivot, recursion, prng)
            _quick_sort(values, index_j + 1, index_s, probe, pivot, recursion, prng)
            return

        left_size = index_j - index_r
        right_size = index_s - index_j

        if left_size < right_size:
            _quick_sort(values, index_r, index_j - 1, probe, pivot, recursion, prng)
            index_r = index_j + 1  # continua iterativamente pela direita

        else:
            _quick_sort(values, index_j + 1, index_s, probe, pivot, recursion, prng)
            index_s = index_j - 1  # continua iterativamente pela esquerda
```
<!-- snippet-include-end -->

---

<!-- _class: code-compare -->

### Quick Sort — Particionamento

##### C++

##### Python

<!-- snippet-include: cpp/src/algorithms/sorting/quick_sort.cpp#quick-sort-partition -->
```cpp
template <typename ProbeType>
std::size_t partition(std::span<double> values, std::size_t index_r,
                      std::size_t index_s, ProbeType& probe,
                      tca::algorithms::QuickPivot pivot, tca::PRNG& prng) {
    const std::size_t index_pivot = choose_pivot(index_r, index_s, pivot, prng);
    probe.swap(values, index_r, index_pivot); // move o pivô para x_r

    const double value_pivot = values[index_r]; // v = x_r
    std::size_t index_i = index_r;              // i = r
    std::size_t index_j = index_s + 1;          // j = s+1

    while (true) { // repita {separação}
        ++index_i; // i = i+1

        while (index_i <= index_s &&
               probe.lt(values[index_i], value_pivot)) { // até x_i >= v
            ++index_i;                                   // i = i+1
        }

        --index_j; // j = j-1

        while (probe.lt(value_pivot, values[index_j])) { // até x_j <= v
            --index_j;                                   // j = j-1
        }

        if (index_j <= index_i) { // até j <= i
            break;
        }

        probe.swap(values, index_i, index_j); // troque x_i com x_j
    }

    probe.swap(values, index_r, index_j); // troque x_r com x_j

    return index_j;
}
```
<!-- snippet-include-end -->

<!-- snippet-include: src/tca/reference/sorting/quick_sort.py#quick-sort-partition -->
```python
def _partition(
    values, index_r: int, index_s: int, probe, pivot: str, prng: PRNG
) -> int:
    index_pivot = _choose_pivot(index_r, index_s, pivot, prng)

    probe.event(
        "choose_pivot",
        indices=(index_pivot,),
        values=(values[index_pivot],),
        start=index_r,
        end=index_s,
        strategy=pivot,
    )

    probe.swap(values, index_r, index_pivot)  # move o pivô para x_r

    value_pivot = values[index_r]  # v = x_r
    index_i = index_r  # i = r
    index_j = index_s + 1  # j = s+1

    while True:  # repita {separação}
        index_i += 1  # i = i+1

        # até x_i >= v
        while index_i <= index_s and probe.lt(
            values[index_i],
            value_pivot,
            indices=(index_i, index_r),
            roles=("current", "pivot"),
        ):
            index_i += 1  # i = i+1

        index_j -= 1  # j = j-1

        while probe.lt(
            value_pivot,
            values[index_j],
            indices=(index_r, index_j),
            roles=("pivot", "current"),
        ):  # até x_j <= v
            index_j -= 1  # j = j-1

        if index_j <= index_i:  # até j <= i
            break

        probe.swap(values, index_i, index_j)  # troque x_i com x_j

    probe.swap(values, index_r, index_j)  # troque x_r com x_j

    probe.event(
        "partition",
        indices=(index_r, index_j, index_s),
        values=(value_pivot,),
    )  # partition.indices = (start, pivot, end)

    return index_j
```
<!-- snippet-include-end -->

---

## Quick Classic × Quick Smarter

| Decisão | Quick Classic | Quick Smarter |
| --- | --- | --- |
| Pivô | Primeiro elemento do intervalo. | Pivô pseudoaleatório reproduzível. |
| Recursão | Chama recursivamente as duas partições. | Chama recursivamente a menor partição e itera sobre a maior. |
| Consequência | Partições degeneradas podem consumir toda a pilha. | A profundidade da pilha fica limitada e o algoritmo é mais robusto. |

As duas variantes usam o mesmo particionamento; a comparação experimental mede conjuntamente a política de pivô e a estratégia de recursão.

---

<!-- _class: code-compare -->

### Radix Sort

##### C++

##### Python

<!-- snippet-include: cpp/src/algorithms/sorting/radix_sort.cpp#radix-sort -->
```cpp
template <typename ProbeType>
void radix_sort_impl(std::span<double> values, ProbeType& probe, int digits) {
    if (digits < 0 || digits > tca::MAX_DECIMAL_DIGITS) {
        throw std::invalid_argument("digits must be between 0 and 15");
    }

    if (values.size() < 2) { // se n < 2 então retorne {caso básico}
        return;
    }

    std::vector<std::int64_t> raw_keys(values.size());

    for (std::size_t index_i = 0; index_i < values.size(); ++index_i) {
        raw_keys[index_i] = tca::decimal_key(values[index_i],
                                             digits); // k_i = trunc(x_i * 10^digits)
    }

    const auto keys =
        normalize_keys(raw_keys, digits); // remove zeros comuns da quantizacao

    const auto minimum_key =
        *std::min_element(keys.begin(), keys.end()); // k_min = min(k)

    std::vector<std::uint64_t> shifted_keys(values.size());

    for (std::size_t index_i = 0; index_i < keys.size(); ++index_i) {
        shifted_keys[index_i] =
            // keys[index_i] - minimum_key seria um problema pois
            // se keys[index_i] for INT64_MAX e minimum_key for INT64_MIN,
            // a diferença não cabe em int64_t
            // Logo, a aritmética é feita em uint64_t.
            // A diferença representa corretamente a distância, sem overflow signed
            static_cast<std::uint64_t>(keys[index_i]) -
            static_cast<std::uint64_t>(minimum_key); // y_i = k_i - k_min
    }

    const auto maximum_key = *std::max_element(shifted_keys.begin(),
                                               shifted_keys.end()); // max = max(y)

    const int effective_digits =
        digit_count(maximum_key); // numero efetivo de digitos LSD

    std::vector<std::size_t> indices(values.size());

    for (std::size_t index_i = 0; index_i < indices.size(); ++index_i) {
        indices[index_i] = index_i; // idx = [0, 1, ..., n-1]
    }

    std::uint64_t exponent = 1; // exp = 1

    for (int pass = 0; pass < effective_digits;
         ++pass) { // para cada digito efetivo {passadas LSD}
        indices = counting_sort_by_digit(indices, shifted_keys, exponent, probe);
        // counting(idx, exp)

        exponent *= 10; // exp = 10 * exp
    }

    std::vector<double> ordered_values(values.size()); // x' = vetor ordenado

    for (std::size_t index_k = 0; index_k < indices.size();
         ++index_k) { // para k = 0..n-1 {reordenação final}
        const std::size_t index_source = indices[index_k];

        probe.write(std::span<double>{ordered_values}, index_k,
                    values[index_source]); // x'_k = x_idx[k]
    }

    for (std::size_t index_k = 0; index_k < values.size();
         ++index_k) { // para k = 0..n-1
        probe.write(values, index_k,
                    ordered_values[index_k]); // x_k = x'_k
    }
}
```
<!-- snippet-include-end -->

<!-- snippet-include: src/tca/reference/sorting/radix_sort.py#radix-sort -->
```python
def radix_sort(
    values,
    metrics: Metrics | None = None,
    trace: Trace | None = None,
    *,
    digits: int = 3,
) -> None:
    if not isinstance(digits, int):
        raise TypeError("digits must be an integer")

    if not 0 <= digits <= MAX_DECIMAL_DIGITS:
        raise ValueError(f"digits must be between 0 and {MAX_DECIMAL_DIGITS}")

    probe = make_probe(metrics, trace)

    if len(values) < 2:  # se n < 2 então retorne {caso básico}
        return

    raw_keys = [
        decimal_key(value, digits) for value in values
    ]  # k_i = trunc(x_i * 10^digits)

    keys = _normalize_keys(
        raw_keys,
        digits,
    )  # remove zeros comuns introduzidos pela quantização

    minimum_key = min(keys)  # k_min = min(k)
    shifted_keys = [key - minimum_key for key in keys]  # y_i = k_i - k_min
    indices = list(range(len(values)))  # idx = [0, 1, ..., n-1]

    maximum_key = max(shifted_keys)  # max = max(y)
    effective_digits = _digit_count(maximum_key)  # número efetivo de dígitos LSD

    exponent = 1  # exp = 1

    for _ in range(effective_digits):  # para cada dígito efetivo {passadas LSD}
        indices = _counting_sort_by_digit(
            indices,
            shifted_keys,
            exponent,
            probe,
        )  # counting(idx, exp)

        probe.event(
            "radix_pass",
            values=tuple(values[index_source] for index_source in indices),
            exponent=exponent,
            order=tuple(indices),
        )

        exponent *= 10  # exp = 10 * exp

    ordered_values = [None] * len(values)  # x' = vetor ordenado

    for index_k, index_source in enumerate(
        indices
    ):  # para k = 0..n-1 {reordenação final}
        probe.write(
            ordered_values,
            index_k,
            values[index_source],
            target="ordered_values",
        )  # x'_k = x_idx[k]

    for index_k, value in enumerate(ordered_values):  # para k = 0..n-1
        probe.write(values, index_k, value, target="values")  # x_k = x'_k
```
<!-- snippet-include-end -->

---

## Radix Decimal — funcionamento

- Cada valor `x` é convertido na chave inteira `trunc(x × 10^digits)`, com `digits` limitado de 0 a 15.
- As chaves são normalizadas e deslocadas pelo menor valor, tornando-as não negativas sem perder a ordem da quantização.
- O algoritmo aplica *counting sort* estável do dígito menos significativo — *least significant digit* (LSD) — para o mais significativo e, ao final, materializa os valores na ordem dos índices obtidos.

Portanto, a ordenação é exata para a precisão decimal escolhida: valores que só diferem abaixo de `10^-digits` pertencem à mesma chave. Quanto menor o número de dígitos efetivos, menor o número de passadas LSD.
