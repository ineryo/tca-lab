# Convenções de geometria

## Escopo e representação

- A geometria inicial é limitada a `R²`.
- O kernel C++ usa coordenadas `double`.
- A entrada Python futura deve preferir `NumPy float64`.
- Coleções de pontos e polígonos em Python devem usar, quando aplicável, a forma `(n, 2)`.

## Orientação

A orientação segue a convenção:

- CCW (anti-horário): sinal positivo;
- CW (horário): sinal negativo;
- colinear: zero segundo a política numérica centralizada.

## Degenerescências e fronteiras

Cada algoritmo deve explicitar e testar, quando relevantes, vetores nulos, pontos repetidos, segmentos e triângulos degenerados, pontos colineares e pontos na fronteira.

Também deve documentar se opera sobre segmento aberto ou fechado, e como distingue interior, fronteira e exterior. Essas convenções não podem ser assumidas silenciosamente.

## Política numérica

`cpp/include/tca/geometry/numeric.hpp` concentra a política prática de comparação para `double`. Ela não substitui o modelo teórico de números reais da disciplina nem fornece predicados exatos ou adaptativos.

## Evolução arquitetural

Algoritmos geométricos devem chamar primitivas centralizadas, em vez de repetir localmente expressões algébricas. Isso preserva a possibilidade de instrumentar primitivas no futuro sem modificar a definição matemática dos algoritmos.
