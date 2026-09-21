# Preparação do `ees108_TCA` para Geometria Computacional — Lista 2

## 1. Objetivo

Preparar o repositório `ees108_TCA` para iniciar a Lista 2 de Geometria Computacional de forma organizada, reutilizável e coerente com a arquitetura já existente do projeto, **sem implementar as soluções dos exercícios da lista**.

A preparação deve ser deliberadamente pequena. O objetivo não é construir antecipadamente uma biblioteca completa de Geometria Computacional, nem reproduzir toda a infraestrutura criada para Sorting. A Lista 2 trabalha principalmente com primitivas e algoritmos geométricos elementares, normalmente sobre exemplos pequenos. A infraestrutura criada agora deve apenas:

1. estabelecer convenções geométricas e numéricas;
2. preparar um local claro para o futuro kernel geométrico em C++;
3. preparar o namespace Python pelo qual esse kernel será acessado;
4. organizar a pasta da Lista 2;
5. preservar um caminho simples para probing, visualização e algoritmos maiores no futuro;
6. evitar decisões arquiteturais que obriguem refatorações desnecessárias depois.

A implementação matemática dos exercícios continuará sendo feita pelo aluno durante a resolução da lista.

---

## 2. Princípios desta preparação

### 2.1. A Lista 2 não deve repetir a arquitetura de Sorting

Sorting justificou uma infraestrutura extensa porque o próprio trabalho envolvia:

- comparação Python × C++;
- benchmarking;
- instrumentação detalhada;
- análise empírica de complexidade;
- replay de eventos;
- animações;
- diferentes variantes de algoritmos.

Esse não é o caso da Lista 2.

Nesta etapa, não criar uma implementação Python e outra C++ para cada operação geométrica, não criar seletor de backend e não criar infraestrutura de benchmark.

### 2.2. C++ será o kernel geométrico canônico

Quando as primitivas e algoritmos da Lista 2 forem implementados, a tendência do projeto será:

```text
Python / Jupyter
      |
      v
 tca.geometry
      |
   pybind11
      |
      v
C++ geometry kernel
```

A escolha de C++ é uma decisão de projeto pessoal, não uma exigência da disciplina.

Ela é útil porque as primitivas geométricas deverão ser reutilizadas muitas vezes em algoritmos posteriores, como fecho convexo, triangulação e eventualmente operações envolvendo malhas.

Entretanto, o benefício do C++ só é preservado se a bridge Python/C++ for usada em granularidade adequada.

Evitar futuramente esta arquitetura:

```text
loop Python
    -> chamada C++ de uma primitiva
    -> volta ao Python
    -> chamada C++ de outra primitiva
    -> ...
```

Preferir:

```text
Python
    -> uma chamada de algoritmo
        -> C++ chama internamente as primitivas quantas vezes forem necessárias
```

As primitivas ainda poderão ser expostas individualmente no Python para estudo, testes e uso em notebooks.

### 2.3. Não implementar backend Python paralelo

Não criar nesta etapa:

```text
backend="python"
backend="cpp"
```

nem implementações de referência Python equivalentes às rotinas C++.

Se no futuro surgir uma razão didática ou experimental concreta para comparar implementações, essa decisão pode ser revista.

### 2.4. Infraestrutura deve surgir por necessidade

Não antecipar módulos para conceitos que ainda não possuem código suficiente.

Evitar, neste momento:

```text
angles.py
segments.py
polygons.py
barycentric.py
intersection.py
clipping.py
convexity.py
...
```

ou equivalentes em C++.

Começar pequeno e dividir arquivos somente quando houver responsabilidade independente ou volume de código que justifique a separação.

---

## 3. Escopo da implementação pelo Hermes

A preparação deve criar somente a infraestrutura abaixo.

### 3.1. Criar documento de convenções

**CREATE**

```text
docs/geometry_conventions.md
```

O documento deve ser curto e normativo.

Deve registrar as decisões de projeto que todos os futuros algoritmos geométricos deverão respeitar.

Conteúdo mínimo:

#### Representação

- geometria inicialmente limitada a `R²`;
- coordenadas numéricas usando `double` no C++;
- entrada Python futura baseada preferencialmente em NumPy `float64`;
- conjuntos de pontos/polígonos no Python deverão seguir, quando aplicável, formato `(n, 2)`.

#### Orientação

Adotar explicitamente:

```text
CCW / anti-horário -> sinal positivo
CW  / horário      -> sinal negativo
colinear            -> zero segundo a política numérica
```

#### Degenerescências

Registrar que os futuros algoritmos devem tratar explicitamente, quando relevantes:

- vetores nulos;
- pontos repetidos;
- segmentos degenerados;
- pontos colineares;
- triângulos degenerados;
- pontos na fronteira.

O documento não deve definir agora a solução de cada caso para cada exercício. Deve apenas estabelecer que os comportamentos precisam ser explícitos e testados.

#### Segmentos e fronteiras

Registrar que cada algoritmo deve documentar quando opera com:

- segmento aberto;
- segmento fechado;
- interior;
- fronteira;
- exterior.

Não assumir essas convenções silenciosamente.

#### Instrumentação futura

Adicionar uma regra arquitetural simples:

> Algoritmos geométricos devem utilizar primitivas centralizadas em vez de reproduzir localmente suas expressões algébricas. Isso permitirá instrumentar chamadas de primitivas futuramente sem modificar a definição matemática dos algoritmos.

Não criar probing agora.

---

## 4. Política numérica centralizada

Este é o principal componente de infraestrutura que deve ser efetivamente implementado agora.

**CREATE**

```text
cpp/include/tca/geometry/numeric.hpp
```

Objetivo: impedir que tolerâncias e regras de comparação numérica sejam espalhadas pelos algoritmos.

O arquivo deve ser pequeno, header-only quando conveniente e independente de conceitos geométricos como triângulos ou polígonos.

Ele pode fornecer uma interface mínima equivalente conceitualmente a:

```text
is_zero(value)
almost_equal(a, b)
sign(value)
```

Os nomes concretos devem seguir o estilo já existente do projeto.

### Requisitos

- uma única política default de tolerância;
- constante/configuração centralizada;
- nenhuma literal como `1e-9`, `1e-12`, etc. deverá ser necessária nos futuros algoritmos;
- `sign` deve produzir uma classificação consistente para negativo, zero e positivo;
- documentar que essa é uma política prática para `double`, distinta do modelo teórico de números reais da disciplina;
- evitar abstrações genéricas excessivas;
- não implementar precisão arbitrária;
- não implementar predicados adaptativos/exatos nesta etapa.

A política deve ser simples o suficiente para ser substituída futuramente sem alterar todos os algoritmos geométricos.

---

## 5. Tipos geométricos: manter mínimos

Não criar uma hierarquia orientada a objetos.

Evitar:

```text
Point2 class
Vector2 class
Line2 class
Ray2 class
Segment2 class
Triangle2 class
Polygon2 class
```

como abstrações completas.

Se for necessário para tornar as assinaturas C++ legíveis, é aceitável criar um único arquivo mínimo:

```text
cpp/include/tca/geometry/types.hpp
```

**CREATE somente se realmente necessário durante a implementação.**

Nesse caso, limitar o arquivo a aliases ou estruturas triviais, por exemplo um tipo simples de ponto/vetor bidimensional.

Não adicionar comportamento geométrico aos tipos.

Se `std::array<double, 2>` for suficiente para a preparação atual, não criar `types.hpp` ainda.

---

## 6. Namespace geométrico no Python

**CREATE**

```text
src/tca/geometry/__init__.py
```

Objetivo: reservar a API pública estável para Geometria Computacional.

Nesta preparação, o módulo pode ser mínimo.

Não criar seletor de backend.

Não criar implementação Python dos algoritmos.

A API pública futura deverá permitir uso natural como:

```python
from tca.geometry import ...
```

em vez de exigir acesso direto a:

```python
from tca import _core
```

Não é necessário expor funções geométricas agora se nenhuma delas estiver implementada sem resolver os exercícios.

---

## 7. C++: preparar diretório, mas não criar código vazio desnecessário

**CREATE DIRECTORY**

```text
cpp/include/tca/geometry/
```

Apenas `numeric.hpp` é obrigatório neste momento.

Não criar antecipadamente arquivos vazios como:

```text
primitives.hpp
algorithms.hpp
segments.hpp
polygons.hpp
...
```

Eles devem nascer quando o aluno começar a implementar a Lista 2.

Da mesma forma, não criar ainda:

```text
cpp/src/geometry/algorithms.cpp
cpp/bindings/geometry.cpp
```

se não houver função geométrica real a compilar ou expor.

A primeira primitiva implementada pelo aluno será o momento adequado para criar esses arquivos e conectar o novo domínio ao CMake/pybind11.

Essa decisão evita infraestrutura vazia e mantém cada commit funcional.

---

## 8. Estrutura da Lista 2

**CREATE**

```text
assignments/02-geometry/
```

Conteúdo inicial:

```text
assignments/02-geometry/
├── README.md
├── lista_02-gc.pdf
├── solucao.ipynb
└── artifacts/
```

### `README.md`

**CREATE**

Deve explicar brevemente:

- objetivo da Lista 2;
- que as soluções serão desenvolvidas incrementalmente pelo aluno;
- que o kernel geométrico reutilizável ficará em `tca.geometry` / C++;
- que a lista não terá implementação Python paralela;
- que visualizações usarão Plotly;
- que probing e animações poderão ser adicionados posteriormente quando houver justificativa algorítmica.

Não incluir respostas dos exercícios.

### `lista_02-gc.pdf`

**COPY**

Copiar o PDF fornecido para a pasta da atividade.

### `solucao.ipynb`

**CREATE**

Criar apenas o esqueleto do notebook.

Estrutura sugerida:

```text
Título
Contexto / convenções
Questão 1
Questão 2
Questão 3
Questão 4
Questão 5
Questão 6
Questão 7
```

Cada questão deve começar vazia ou com uma pequena célula Markdown contendo apenas o enunciado resumido/referência à questão.

Não inserir pseudocódigo, algoritmo, fórmula de solução ou implementação.

O notebook utilizará a biblioteca do projeto à medida que as soluções forem desenvolvidas.

### `artifacts/`

**CREATE DIRECTORY**

Reservar para HTMLs e figuras produzidos durante a resolução.

---

## 9. Visualização

O projeto utiliza **Plotly** como biblioteca padrão de visualização.

Não introduzir Matplotlib.

Nesta Lista 2, não criar ainda uma infraestrutura genérica de visualização geométrica.

As primeiras figuras devem ser escritas diretamente no notebook com Plotly.

Exemplos de elementos que poderão ser visualizados durante a resolução:

- pontos;
- vetores;
- segmentos;
- triângulos;
- polígonos;
- regiões de interseção;
- resultados de clipping;
- semirretas usadas em localização.

Somente se aparecer repetição concreta de código deverá ser criado futuramente:

```text
src/tca/visualization/geometry.py
```

Possíveis helpers futuros:

```text
add_points(...)
add_segment(...)
add_polygon(...)
add_triangle(...)
```

Não criar esses helpers nesta preparação.

### Animações

Não implementar animações para a Lista 2 como requisito de infraestrutura.

Predicados e pequenos algoritmos geométricos normalmente são melhor explicados com figuras estáticas/interativas.

Reservar a infraestrutura de animação/replay para algoritmos futuros cujo estado evolua de forma pedagogicamente relevante, por exemplo:

- Graham Scan;
- Jarvis March;
- QuickHull;
- sweep line;
- triangulação incremental;
- algoritmos de malha.

---

## 10. Probing e métricas

Não implementar agora:

```text
GeometryProbe
GeometryMetrics
TraceProbe
EventLog geométrico
Replay geométrico
```

Entretanto, preservar desde o início o seguinte contrato:

> Uma operação geométrica fundamental deve existir em um único ponto do kernel. Algoritmos de nível superior devem chamá-la, e não reproduzir sua expressão matemática internamente.

Isso permitirá futuramente contabilizar métricas como:

```text
orientation_tests
intersection_tests
distance_evaluations
primitive_calls
```

sem reescrever os algoritmos.

A instrumentação deve ser adicionada somente quando houver um algoritmo suficientemente interessante para analisar — provavelmente fecho convexo ou triangulação.

---

## 11. Testes

Nesta preparação, não criar uma grande suíte de testes geométricos sem funções geométricas implementadas.

O único código matemático novo esperado agora é a política numérica.

Se houver forma simples de testá-la dentro da infraestrutura de testes C++ já existente, adicionar testes pequenos para:

- zero;
- positivo;
- negativo;
- valores próximos ao threshold;
- igualdade aproximada.

Não criar bindings públicos exclusivamente para testar `numeric.hpp`.

Quando a primeira primitiva geométrica for implementada pelo aluno, criar então:

```text
tests/python/geometry/
├── test_primitives.py
└── test_algorithms.py
```

Esses arquivos devem crescer junto com a Lista 2.

Como haverá somente uma implementação canônica, não criar:

```text
test_python_cpp_equivalence.py
```

O foco posterior dos testes geométricos deverá ser:

- casos regulares;
- fronteiras;
- degenerescências;
- orientação CW/CCW;
- colinearidade;
- vértices compartilhados;
- pontos coincidentes;
- segmentos horizontais/verticais quando relevantes.

---

## 12. Alterações que não devem ser realizadas agora

Não implementar ou adicionar nesta preparação:

- soluções da Lista 2;
- pseudo-ângulo;
- algoritmo `entre`;
- localização por coordenadas baricêntricas;
- clipping;
- interseção de triângulos;
- teste de convexidade;
- ponto-em-polígono;
- backend Python de geometria;
- comparação Python × C++;
- benchmarks geométricos;
- estimativa empírica de complexidade;
- GeometryProbe;
- GeometryMetrics;
- Event Log;
- replay;
- animações;
- módulo genérico de visualização;
- classes geométricas completas;
- CGAL;
- Shapely;
- Boost.Geometry;
- estruturas espaciais;
- GPU;
- SIMD;
- precisão arbitrária;
- predicados geométricos adaptativos/exatos.

Não adicionar dependências novas nesta preparação.

---

## 13. Estrutura esperada após a preparação

A mudança deve ser pequena.

```text
ees108_TCA/
│
├── cpp/
│   └── include/tca/
│       └── geometry/
│           └── numeric.hpp
│
├── src/tca/
│   └── geometry/
│       └── __init__.py
│
├── assignments/
│   └── 02-geometry/
│       ├── README.md
│       ├── lista_02-gc.pdf
│       ├── solucao.ipynb
│       └── artifacts/
│
└── docs/
    └── geometry_conventions.md
```

Opcionalmente:

```text
cpp/include/tca/geometry/types.hpp
```

somente se houver necessidade concreta.

Isso é intencionalmente muito menor que a estrutura de Sorting.

---

## 14. Estado futuro esperado durante a resolução da Lista 2

À medida que o aluno resolver as questões, a arquitetura deverá crescer organicamente para algo semelhante a:

```text
cpp/include/tca/geometry/
├── numeric.hpp
├── primitives.hpp
└── algorithms.hpp

cpp/src/geometry/
└── algorithms.cpp

cpp/bindings/
└── geometry.cpp

src/tca/geometry/
└── __init__.py

tests/python/geometry/
├── test_primitives.py
└── test_algorithms.py
```

Mas esses arquivos devem ser criados **quando existir código real que precise deles**, não antecipadamente.

A primeira primitiva implementada será o momento de criar `primitives.hpp` e o binding correspondente.

O primeiro algoritmo não trivial será o momento de criar `algorithms.hpp/.cpp`.

---

## 15. Critérios de aceite da preparação

A preparação estará concluída quando:

1. `docs/geometry_conventions.md` existir e registrar as convenções essenciais;
2. a política numérica estiver centralizada em `cpp/include/tca/geometry/numeric.hpp`;
3. `src/tca/geometry/__init__.py` existir;
4. `assignments/02-geometry/` estiver organizada com README, PDF, notebook vazio estruturado e `artifacts/`;
5. nenhuma questão da Lista 2 tiver sido resolvida ou parcialmente implementada;
6. nenhuma nova dependência tiver sido adicionada;
7. nenhuma infraestrutura de probing, replay, benchmark ou visualização genérica tiver sido criada;
8. o projeto continuar formatando, compilando e testando normalmente;
9. Black, Ruff, clang-format e a suíte de testes aplicável permanecerem verdes;
10. a mudança resultar em um commit pequeno, autocontido e fácil de revisar.

---

## 16. Ordem de execução sugerida ao Hermes

Executar nesta ordem:

```text
1. inspecionar estrutura e padrões atuais do repositório;
2. criar docs/geometry_conventions.md;
3. criar cpp/include/tca/geometry/numeric.hpp;
4. criar src/tca/geometry/__init__.py;
5. criar assignments/02-geometry/;
6. copiar lista_02-gc.pdf;
7. criar README.md da atividade;
8. criar solucao.ipynb apenas com estrutura de seções;
9. criar artifacts/;
10. formatar;
11. executar testes existentes;
12. revisar diff garantindo que nenhuma solução da Lista 2 foi introduzida.
```

Antes de criar `types.hpp`, verificar se ele é realmente necessário. Na ausência de necessidade concreta, não criá-lo.

---

## 17. Resumo da decisão arquitetural

A preparação deve seguir esta ideia:

```text
AGORA

convenções
    +
política numérica
    +
namespace geometry
    +
estrutura da atividade


DURANTE A LISTA

primitivas C++
    ↓
bindings Python
    ↓
algoritmos C++
    ↓
testes
    ↓
plots Plotly no notebook


DEPOIS, SE JUSTIFICADO

probing
visualização reutilizável
animações/replay
benchmarks
algoritmos geométricos maiores
```

O princípio central é:

> **A Lista 2 deve continuar simples; o que for criado como infraestrutura deve ter utilidade clara além de um único exercício.**

O objetivo desta preparação é permitir que o aluno comece a resolver a lista imediatamente após o commit, com decisões fundamentais já organizadas, mas ainda tendo que desenvolver por conta própria toda a lógica geométrica exigida pelos exercícios.
