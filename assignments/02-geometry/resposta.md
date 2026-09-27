---
title: "Lista 02 — Geometria Computacional"
subtitle: "Técnicas Computacionais Avançadas — PPGEC/UFAL"
author: "Igor de Melo Nery Oliveira"
date: "22 de setembro de 2026"
lang: pt-BR
---

As soluções consideram o plano $\mathbb{R}^2$, com orientação anti-horária
positiva e aritmética em `double`. As primitivas e os algoritmos foram
implementados em C++ e expostos pela API `tca.geometry`. Este relatório
organiza o raciocínio, os exemplos e os resultados do
[notebook revisado](solucao.ipynb); Python é a camada de
demonstração e análise.

A tolerância numérica é centralizada no kernel C++: valores de módulo até
$\varepsilon=10^{-12}$ são considerados nulos. As classificações de localização
usam **0 = exterior**, **1 = interior** e **2 = fronteira**.

## Questão 1 — Pseudo-ângulo

### Interpretação e critério

Para ordenar vetores em torno da origem, basta saber qual direção vem antes
da outra; não é necessário medir o ângulo em radianos. `pseudo_angle`
atribui valores em $[0,8)$, começando no semieixo positivo de $x$ e crescendo
no sentido anti-horário.

Os sinais das coordenadas identificam o quadrante. Uma comparação adicional
divide esse quadrante em dois trechos, separados pela diagonal. Em cada
trecho, uma razão entre coordenadas e um ajuste constante produzem a chave
de ordenação. A chave preserva a ordem das direções, sem calcular norma,
raiz quadrada ou função trigonométrica. Ela não representa um ângulo em graus.

### Verificação e leitura da figura

Os quatro semieixos produziram os valores de referência:

| Vetor | $(1,0)$ | $(0,1)$ | $(-1,0)$ | $(0,-1)$ |
|:--|--:|--:|--:|--:|
| Pseudo-ângulo | 0 | 2 | 4 | 6 |

Os vetores $(0,0)$ e $(10^{-13},10^{-13})$ foram rejeitados com uma exceção
`ValueError`, capturada no notebook, e a mensagem
`pseudo_angle: vector cannot be the zero vector`. Ambos são considerados
nulos pela tolerância adotada e, portanto, sem direção definida.

O experimento utiliza os 48 pontos de $\{-3,-2,-1,0,1,2,3\}^2$, excluindo a
origem. Pontos selecionados sobre os eixos e as diagonais recebem perturbações
de até $10^{-3}$, com semente 42, para exercitar as transições das comparações.
Após o embaralhamento, os pseudo-ângulos são ordenados pelo Merge Sort C++.

Na figura, a ordem de entrada não acompanha a posição geométrica, enquanto
a ordem final percorre as direções no sentido anti-horário. Os valores
permitem conferir as transições entre quadrantes; pontos sobre uma mesma
semirreta podem compartilhar a mesma chave.

<!-- figure-include: assignments/02-geometry/artifacts/q01_pseudo_angle.html?width=100%&height=550&caption=Figura 1 — Ordem de entrada, pseudo-ângulos e ordenação angular dos 48 pontos. -->
<iframe src="artifacts/q01_pseudo_angle.html" width="100%" height="550" title="interactive plot" frameborder="0"></iframe>

**Figura 1 — Ordem de entrada, pseudo-ângulos e ordenação angular dos 48 pontos.**
<!-- figure-include-end -->

### Contagem de operações

A contagem do **cálculo principal**, para uma entrada admitida, é:

| Operação | Quantidade por execução |
|:--|--:|
| Comparações para escolher quadrante e trecho | 3 |
| Divisões | 1 |
| Somas ou subtrações de ajuste | no máximo 1 |
| Inversões de sinal | até 2 |
| Multiplicações | 0 |
| Raízes quadradas | 0 |
| Valores absolutos | 0 |
| Funções trigonométricas | 0 |

A validação `is_zero(vector.x) && is_zero(vector.y)` é adicional e não
integra essa contagem. Como `is_zero` usa `std::abs`, a validação
acrescenta até dois valores absolutos e dois testes de nulidade; o segundo
teste depende do primeiro, pelo curto-circuito de `&&`. Essa decisão de
projeto rejeita entradas sem direção e mantém a política numérica comum.

O custo da primitiva é $O(1)$.

<details>
<summary>Ver implementação de <code>pseudo_angle</code></summary>

<!-- snippet-include: cpp/src/geometry/primitives.cpp#q01-pseudo-angle -->
```cpp
double pseudo_angle(const Point2& vector) {

    if (is_zero(vector.x) && is_zero(vector.y)) {
        throw std::invalid_argument("pseudo_angle: vector cannot be the zero vector");
    }

    double result = 0.0;

    if (vector.x >= 0.0) {
        if (vector.y >= 0.0) {
            result =
                vector.x >= vector.y ? vector.y / vector.x : 2.0 - vector.x / vector.y;
        } else {
            result = vector.x >= -vector.y ? 8.0 + vector.y / vector.x
                                           : 6.0 - vector.x / vector.y;
        }
    } else {
        if (vector.y >= 0.0) {
            result = -vector.x >= vector.y ? 4.0 + vector.y / vector.x
                                           : 2.0 - vector.x / vector.y;
        } else {
            result = -vector.x >= -vector.y ? 4.0 + vector.y / vector.x
                                            : 6.0 - vector.x / vector.y;
        }
    }

    return result;
}
```
<!-- snippet-include-end -->

</details>

## Questão 2 — Pertinência a um ângulo convexo

### Interpretação e critério

Os vetores $u$ e $v$ delimitam uma abertura convexa com vértice na origem.
Para decidir se $w$ está nessa abertura, verifica-se de que lado de cada
direção limite ele se encontra. O produto vetorial
$u\times v=u_xv_y-u_yv_x$ fornece essa informação sem calcular ângulos.

Se $u\times v>0$, a abertura vai de $u$ a $v$ no sentido anti-horário:
$w$ pertence a ela quando $u\times w\geq0$ e $w\times v\geq0$.
Se $u\times v<0$, o percurso é horário e ambas as desigualdades se invertem.
As igualdades incluem a fronteira.

A função `entre(u,v,w)` retorna **0** se $u$ e $v$ são colineares,
**1** se $w$ pertence ao ângulo convexo, incluindo sua fronteira, e **2** se
está fora. Os sinais são avaliados com a tolerância do projeto.

### Verificação

| Configuração geométrica | $u$ | $v$ | $w$ | Retorno |
|:--|:--|:--|:--|--:|
| Dentro da abertura | $(1,0)$ | $(0,1)$ | $(1,1)$ | 1 |
| Fora da abertura | $(1,0)$ | $(0,1)$ | $(-1,-1)$ | 2 |
| Fronteira, na direção de $u$ | $(1,0)$ | $(0,1)$ | $(1,0)$ | 1 |
| Fronteira, na direção de $v$ | $(1,0)$ | $(0,1)$ | $(0,1)$ | 1 |
| Direções delimitadoras colineares | $(1,0)$ | $(2,0)$ | $(0,1)$ | 0 |

A figura aplica o critério aos mesmos 48 pontos da Questão 1. Os três
pares $(u,v)$ são:

- caso 1: $(0{,}5,0)$ e $(0,0{,}5)$;
- caso 2: $(0,-0{,}5)$ e $(-0{,}5,0)$;
- caso 3: $(2{,}5,1{,}5)$ e $(-1{,}5,-1{,}5)$.

Os casos permitem verificar que a classificação acompanha a abertura
convexa, inclusive quando o percurso de $u$ para $v$ é horário.

<!-- figure-include: assignments/02-geometry/artifacts/q02_entre.html?width=100%&height=550&caption=Figura 2 — Classificação angular em três configurações de u e v. -->
<iframe src="artifacts/q02_entre.html" width="100%" height="550" title="interactive plot" frameborder="0"></iframe>

**Figura 2 — Classificação angular em três configurações de u e v.**
<!-- figure-include-end -->

A decisão utiliza até três produtos vetoriais e um número fixo de testes:
tempo e espaço auxiliar $O(1)$.

<details>
<summary>Ver implementação de <code>entre</code></summary>

<!-- snippet-include: cpp/src/geometry/primitives.cpp#q02-entre -->
```cpp
int entre(const Point2& u, const Point2& v, const Point2& w) {
    // Obs.:O algoritmo considera a fronteira (quando w e colinear com u ou v) como
    // pertencente ao angulo convexo.

    // Sinal (-1, 0, 1) do produto vetorial u x v.
    // O resultado e 0 quando u e v sao considerados colineares pela tolerancia
    // numerica.
    const int uv = sign(cross(u, v));

    // Classificacao como 0 quando u e v sao colineares.
    if (uv == 0) {
        return 0;
    }

    const int uw = sign(cross(u, w));
    const int wv = sign(cross(w, v));

    // Se u x v > 0, o angulo convexo vai de u ate v no sentido anti-horario.
    // w pertence a esse angulo se estiver a esquerda de u e antes de v.
    if (uv > 0) {
        return (uw >= 0 && wv >= 0) ? 1 : 2;
    }

    // Se u x v < 0, o angulo convexo vai de u ate v no sentido horario.
    // w pertence a esse angulo se estiver a direita de u e depois de v.
    return uw <= 0 && wv <= 0 ? 1 : 2;
}
```
<!-- snippet-include-end -->

</details>

## Questão 3 — Localização por coordenadas baricêntricas

### Interpretação e critério

As coordenadas baricêntricas descrevem a contribuição de cada vértice para
a posição de um ponto. No interior, as três contribuições são positivas;
sobre um lado, a contribuição do vértice oposto é nula; ao cruzar esse lado
para fora, ela se torna negativa.

Para um triângulo não degenerado,

$$
P=\lambda_1P_1+\lambda_2P_2+\lambda_3P_3,
\qquad \lambda_1+\lambda_2+\lambda_3=1.
$$

A função `locate_point_in_triangle` retorna **0 — exterior** se alguma
coordenada é negativa; **2 — fronteira** se nenhuma é negativa e pelo menos
uma é nula; e **1 — interior** se todas são positivas. Uma coordenada nula,
sozinha, não basta: o ponto pode estar no prolongamento de um lado.

### Verificação

Para $P_1=(-2,-1)$, $P_2=(2,-1)$ e $P_3=(0,2)$, obtiveram-se:

| Configuração geométrica | Ponto | Coordenadas baricêntricas | Retorno |
|:--|:--|:--|--:|
| Interior | $(0,0)$ | $(1/3,1/3,1/3)$ | 1 |
| Fronteira, no vértice $P_1$ | $P_1$ | $(1,0,0)$ | 2 |
| Fronteira, no vértice $P_2$ | $P_2$ | $(0,1,0)$ | 2 |
| Fronteira, no vértice $P_3$ | $P_3$ | $(0,0,1)$ | 2 |
| Fronteira, no lado $P_1P_3$ | $(P_1+2P_3)/3=(-2/3,1)$ | $(1/3,0,2/3)$ | 2 |

A área orientada é $6$ na ordem anti-horária e $-6$ na ordem inversa.
Essa troca de sinal confirma a convenção de orientação.

A visualização utiliza uma **grade regular de 49 pontos**
$\{-3,-2,-1,0,1,2,3\}^2$, incluindo a origem e sem as perturbações da Questão 1.
Os três primeiros painéis mostram a mudança de sinal de cada coordenada
ao cruzar o lado oposto; o quarto reúne esses sinais na classificação.

<!-- figure-include: assignments/02-geometry/artifacts/q03_barycentric_location.html?width=100%&height=930&caption=Figura 3 — Coordenadas baricêntricas e localização dos 49 pontos da grade regular. -->
<iframe src="artifacts/q03_barycentric_location.html" width="100%" height="930" title="interactive plot" frameborder="0"></iframe>

**Figura 3 — Coordenadas baricêntricas e localização dos 49 pontos da grade regular.**
<!-- figure-include-end -->

### Justificativa do cálculo

Denotando a área orientada por $S$, calculam-se

$$
S_{ABC}=\frac12(B-A)\times(C-A),
$$

$$
\lambda_1=\frac{S_{PP_2P_3}}{S_{P_1P_2P_3}},\qquad
\lambda_2=\frac{S_{P_1PP_3}}{S_{P_1P_2P_3}},\qquad
\lambda_3=1-\lambda_1-\lambda_2.
$$

O sinal de cada razão indica de que lado da reta correspondente o ponto
se encontra. A implementação combina `oriented_area`,
`barycentric_coordinates` e `locate_point_in_triangle`. Para um triângulo,
o cálculo e a classificação custam $O(1)$.

<details>
<summary>Ver cálculo das coordenadas baricêntricas</summary>

<!-- snippet-include: cpp/src/geometry/primitives.cpp#q03-barycentric -->
```cpp
std::array<double, 3> barycentric_coordinates(const Point2& point,
                                              const Triangle2& triangle) {

    const double area = oriented_area(triangle);

    if (is_zero(area)) {
        throw std::invalid_argument(
            "barycentric_coordinates: triangle cannot be degenerate");
    }

    const Triangle2 triangle_1 = {
        point,
        triangle[1],
        triangle[2],
    };

    const Triangle2 triangle_2 = {
        triangle[0],
        point,
        triangle[2],
    };

    double coord1 = oriented_area(triangle_1) / area;
    double coord2 = oriented_area(triangle_2) / area;
    double coord3 = 1.0 - coord1 - coord2;

    return {coord1, coord2, coord3};
}
```
<!-- snippet-include-end -->

</details>

## Questão 4 — Recorte de um segmento por um triângulo

### Formulação

Recortar um segmento significa conservar apenas a parte que fica no
triângulo. Ao percorrê-lo, as coordenadas baricêntricas indicam quando se
entra no triângulo e quando se sai.

Adota-se a parametrização do notebook,

$$
P(t)=tA+(1-t)B,\qquad 0\leq t\leq1,
$$

na qual $t=0$ corresponde a $B$ e $t=1$ a $A$. Se $\alpha_i$ e $\beta_i$
são as coordenadas de $A$ e $B$, as coordenadas de $P(t)$ variam linearmente:

$$
\theta_i(t)=t\alpha_i+(1-t)\beta_i,\qquad i=1,2,3.
$$

Isso decorre da variação afim da área orientada:
$S_{P(t)P_2P_3}=tS_{AP_2P_3}+(1-t)S_{BP_2P_3}$.
Dividir pela área do triângulo dá a expressão de $\theta_1$; o mesmo
raciocínio vale para as outras duas coordenadas.

O exemplo usado em todos os itens é

$$
P_1=(0,0),\quad P_2=(4,0),\quad P_3=(0,4),\qquad
A=(-1,1),\quad B=(3,3).
$$

As coordenadas baricêntricas calculadas para esses extremos são

$$
\alpha=(1,-1/4,1/4),\qquad \beta=(-1/2,3/4,3/4).
$$

### Item (a) — Segmento completamente contido

Se os dois extremos estão no triângulo, o segmento entre eles também está,
pois o triângulo é convexo. Incluindo a fronteira, a condição necessária e
suficiente é

$$
\alpha_i\geq0\quad\text{e}\quad\beta_i\geq0,\qquad i=1,2,3.
$$

Cada $\theta_i(t)$ é uma combinação convexa de dois valores não negativos;
portanto, nenhuma coordenada se torna negativa durante o percurso.

#### Verificação do item (a)

No exemplo, $\alpha_2=-1/4$ e $\beta_1=-1/2$: ambos os extremos são
exteriores. O teste de contenção completa retorna `False`, mas parte do
segmento ainda pode atravessar o triângulo.

### Item (b) — Condição suficiente de exterioridade

Se os extremos estão no mesmo semiplano exterior a um lado, nenhum ponto
do segmento pode entrar no triângulo. Basta encontrar **uma mesma coordenada**
negativa nos dois extremos:

$$
\exists i:\quad\alpha_i<0\quad\text{e}\quad\beta_i<0.
$$

Nesse caso, $\theta_i(t)<0$ para todo $t\in[0,1]$. A condição é suficiente,
mas não necessária: sua falha não garante interseção.

#### Verificação do item (b)

Em $A$, a coordenada negativa é a segunda; em $B$, é a primeira. Como não
há uma mesma coordenada negativa nos dois extremos, o teste suficiente
de exterioridade retorna `False`. Os extremos são exteriores, mas esse
resultado não permite descartar o segmento. É preciso calcular as
interseções com as retas dos lados.

### Item (c) — Interseções com as retas dos lados

Ao atingir a reta de um lado, a coordenada do vértice oposto se anula:
$\theta_1=0$ identifica a reta $P_2P_3$; $\theta_2=0$, a reta $P_3P_1$; e
$\theta_3=0$, a reta $P_1P_2$.

#### Cálculo das interseções

Para cada coordenada, resolve-se uma equação linear:

$$
t\alpha_i+(1-t)\beta_i=0
\quad\Longrightarrow\quad
t_i=\frac{\beta_i}{\beta_i-\alpha_i},\qquad
X_i=t_iA+(1-t_i)B.
$$

A expressão vale quando $\alpha_i\ne\beta_i$. Para o encontro pertencer ao
segmento $AB$, exige-se $0\leq t_i\leq1$; para pertencer ao lado do triângulo,
as outras duas coordenadas também devem ser não negativas. Isso evita
confundir o lado com seu prolongamento.

Se $\alpha_i=\beta_i\ne0$, o segmento é paralelo à reta correspondente e
não a intercepta. Se ambas são zero, o segmento inteiro pertence a essa
reta, e as demais coordenadas delimitam a parte pertencente ao triângulo.
Como há apenas três coordenadas, o cálculo custa $O(1)$.

#### Exemplo e resultados

Para os extremos adotados,

$$
\theta_1(t)=\frac32t-\frac12,\qquad
\theta_2(t)=\frac34-t,\qquad
\theta_3(t)=\frac34-\frac12t.
$$

| Reta | Parâmetro | Ponto | Interpretação |
|:--|:--|:--|:--|
| $P_2P_3$: $x+y=4$ | $t_1=1/3$ | $X_1=(5/3,7/3)$ | entrada no triângulo |
| $P_3P_1$: $x=0$ | $t_2=3/4$ | $X_2=(0,3/2)$ | saída do triângulo |
| $P_1P_2$: $y=0$ | $t_3=3/2$ | $X_3=(-3,0)$ | fora do segmento $AB$ |

Os dois primeiros pontos têm as demais coordenadas não negativas. Logo,
a parte conservada é

$$
\boxed{\frac13\leq t\leq\frac34},\qquad
\boxed{X_1=(5/3,7/3),\quad X_2=(0,3/2)}.
$$

As localizações calculadas no notebook confirmam a mudança de região:

| Interpretação geométrica | $t$ | $P(t)$ | Retorno |
|:--|:--|:--|--:|
| Exterior, no extremo $B$ | $0$ | $(3,3)$ | 0 |
| Fronteira, na entrada | $1/3$ | $(5/3,7/3)$ | 2 |
| Interior | $1/2$ | $(1,2)$ | 1 |
| Fronteira, na saída | $3/4$ | $(0,3/2)$ | 2 |
| Exterior, no extremo $A$ | $1$ | $(-1,1)$ | 0 |

Na figura, os zeros das coordenadas no painel esquerdo correspondem aos
encontros geométricos no painel direito. Entre $1/3$ e $3/4$, as três
coordenadas são não negativas; fora desse intervalo, ao menos uma é negativa.
A verificação reutiliza as primitivas baricêntricas da Questão 3.

<!-- figure-include: assignments/02-geometry/artifacts/q04_clipping.html?width=100%&height=650&caption=Figura 4 — Coordenadas baricêntricas ao longo de AB e trecho conservado pelo recorte. -->
<iframe src="artifacts/q04_clipping.html" width="100%" height="650" title="interactive plot" frameborder="0"></iframe>

**Figura 4 — Coordenadas baricêntricas ao longo de AB e trecho conservado pelo recorte.**
<!-- figure-include-end -->

## Questão 5 — Disjunção entre triângulos

### Interpretação e solução

Dois triângulos são disjuntos quando não compartilham nenhum ponto. Tocar
em um vértice ou em uma aresta, portanto, já impede a disjunção.

O algoritmo procura primeiro interseções entre os pares de arestas,
incluindo cruzamentos, contatos e sobreposições colineares. Se não houver
encontro das bordas, verifica a contenção de um triângulo no outro.
Essa segunda etapa é necessária: um triângulo pode estar inteiramente
dentro do outro sem que suas arestas se cruzem.

Se nenhuma dessas situações ocorre, `triangles_are_disjoint` retorna
`True`. Triângulos degenerados são rejeitados com uma exceção `ValueError`.

### Verificação

Cada triângulo $T_i$ é comparado com o triângulo-base
$T_0=((0,0),(4,0),(0,4))$. A tabela apresenta os vértices na ordem de
entrada e o retorno de `triangles_are_disjoint(T0, Ti)`.

| Configuração em relação a $T_0$ | Triângulo | Vértices na ordem de entrada | Retorno |
|:--|:--|:--|:--:|
| Triângulos idênticos | $T_0$ | $(0,0)\to(4,0)\to(0,4)$ | `False` |
| Completamente separado | $T_1$ | $(5,5)\to(7,5)\to(5,7)$ | `True` |
| Sobreposição parcial | $T_2$ | $(2,1)\to(5,1)\to(2,4)$ | `False` |
| Completamente contido | $T_3$ | $(0{,}5,0{,}5)\to(1{,}5,0{,}5)\to(0{,}5,1{,}5)$ | `False` |
| Contato em um vértice | $T_4$ | $(4,0)\to(6,0)\to(4,2)$ | `False` |
| Aresta compartilhada | $T_5$ | $(0,0)\to(4,0)\to(2,-2)$ | `False` |
| Cruzamento de arestas | $T_6$ | $(2,-1)\to(5,2)\to(2,5)$ | `False` |

A figura distingue visualmente os seis casos. O triângulo contido justifica
a segunda etapa do algoritmo; os contatos confirmam que a fronteira faz
parte dos triângulos.

<!-- figure-include: assignments/02-geometry/artifacts/q05_triangle_disjointness.html?width=100%&height=880&caption=Figura 5 — Seis configurações de dois triângulos e respectivos resultados de disjunção. -->
<iframe src="artifacts/q05_triangle_disjointness.html" width="100%" height="880" title="interactive plot" frameborder="0"></iframe>

**Figura 5 — Seis configurações de dois triângulos e respectivos resultados de disjunção.**
<!-- figure-include-end -->

A matriz completa do notebook confirma a simetria da relação e o resultado
`False` na diagonal: nenhum triângulo é disjunto de si mesmo.

<details>
<summary>Ver resultados para todos os pares de triângulos</summary>

Cada célula contém o retorno de `triangles_are_disjoint` para o par indicado.

| | $T_0$ | $T_1$ | $T_2$ | $T_3$ | $T_4$ | $T_5$ | $T_6$ |
|:--|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| $T_0$ | `False` | `True` | `False` | `False` | `False` | `False` | `False` |
| $T_1$ | `True` | `False` | `True` | `True` | `True` | `True` | `True` |
| $T_2$ | `False` | `True` | `False` | `True` | `False` | `True` | `False` |
| $T_3$ | `False` | `True` | `True` | `False` | `True` | `True` | `True` |
| $T_4$ | `False` | `True` | `False` | `True` | `False` | `False` | `False` |
| $T_5$ | `False` | `True` | `True` | `True` | `False` | `False` | `False` |
| $T_6$ | `False` | `True` | `False` | `True` | `False` | `False` | `False` |

</details>

São no máximo nove testes entre arestas e seis localizações de vértices:
tempo e espaço auxiliar $O(1)$. A
[implementação completa está no apêndice](#ap-disjuncao).

## Questão 6 — Convexidade de um polígono

### Interpretação e critério

Ao caminhar pela borda de um polígono convexo, todas as mudanças de direção
ocorrem para o mesmo lado. Uma concavidade introduz um giro no sentido
oposto. Para um polígono simples, cuja borda não se cruza, basta percorrer
os vértices na ordem da borda e comparar os giros consecutivos.

Para cada trio consecutivo, incluindo os trios que atravessam o fechamento,
calcula-se o sinal de

$$
(P_{i+1}-P_i)\times(P_{i+2}-P_{i+1}).
$$

O primeiro giro estabelece o sinal de referência. Um sinal diferente
rejeita o polígono. Todos positivos correspondem ao percurso anti-horário;
todos negativos, ao horário. Portanto, a orientação global não altera a resposta.

**Política para colinearidade.** Um giro nulo também retorna `False`,
pois foi adotada uma representação mínima, sem vértices intermediários
colineares redundantes. Assim, uma região pode ser convexa como conjunto
e sua representação ser rejeitada por esse contrato. A função não remove
esses vértices.

### Verificação

| Configuração | Interpretação dos giros | Retorno de `is_convex` |
|:--|:--|:--:|
| Convexo anti-horário | Giros positivos | `True` |
| Mesmo convexo em ordem inversa | Giros negativos | `True` |
| Côncavo | Mudança de sinal | `False` |
| Retângulo com vértice colinear intermediário | Giro nulo no vértice redundante | `False` |

A inversão da ordem preserva a forma e a resposta. No último painel, a
rejeição decorre do vértice redundante, e não de uma reentrância geométrica.

<!-- figure-include: assignments/02-geometry/artifacts/q06_convexity.html?width=100%&height=930&caption=Figura 6 — Efeito da orientação, da concavidade e de um vértice colinear sobre o teste. -->
<iframe src="artifacts/q06_convexity.html" width="100%" height="930" title="interactive plot" frameborder="0"></iframe>

**Figura 6 — Efeito da orientação, da concavidade e de um vértice colinear sobre o teste.**
<!-- figure-include-end -->

Cada um dos $n$ vértices participa de um teste de custo constante.
A complexidade é **$O(n)$**, com espaço auxiliar **$O(1)$**. O
[algoritmo completo está no apêndice](#ap-convexidade).

## Questão 7 — Localização pela primeira interseção

### Interpretação geométrica

Considere uma semirreta horizontal para a direita, partindo de $p_0$, e seu
primeiro encontro $u$ com a borda. Entre $p_0$ e $u$ não há outro encontro
com a fronteira; logo, $p_0$ está na mesma região que o trecho imediatamente
anterior a $u$.

Em um polígono simples orientado no **sentido horário**, o interior fica
localmente à **direita** de cada lado percorrido. Conhecendo o lado
$p_i\to p_{i+1}$ atingido, basta identificar de que lado dele chega a
semirreta. O argumento usa a vizinhança da primeira interseção e vale
também para polígonos côncavos.

### Critério e informações necessárias

Basta armazenar **o ponto $u$ e o índice do lado $p_i\to p_{i+1}$**.
O índice permite recuperar os extremos do lado. Definindo
$e=p_{i+1}-p_i$, a decisão é:

- se $u=p_0$, o ponto está na fronteira: **2**;
- se não existe interseção, o ponto é exterior: **0**;
- nos demais casos, o sinal distingue os dois lados:

$$
e\times(p_0-u)<0\ \Longrightarrow\ \text{interior (1)},
$$

$$
e\times(p_0-u)>0\ \Longrightarrow\ \text{exterior (0)}.
$$

Não é necessário armazenar nem contar todas as interseções. A primeira
delimita um trecho livre de fronteira, e o lado orientado fornece o sinal
que identifica a região desse trecho. Em encontros num vértice, é preciso
associar o lado incidente adequado; o exemplo abaixo inclui esse caso.

### Verificação

O polígono do notebook tem vértices $(0,0)$, $(-1,4)$, $(2,1{,}5)$,
$(5,3{,}5)$ e $(4,0)$, nessa ordem. A área orientada calculada é **$-12$**,
confirmando o percurso horário.

A tabela numera os vértices de 1 a 5; `edge_index` começa em zero.

| Configuração geométrica | $p_0$ | Primeira interseção $u$ | Lado associado | Retorno |
|:--|:--|:--|:--|--:|
| Interior | $(1,1)$ | $(30/7,1)$ | $p_4\to p_5$ | 1 |
| Exterior à esquerda | $(-1,1{,}5)$ | $(-3/8,1{,}5)$ | $p_1\to p_2$ | 0 |
| Exterior à direita, sem interseção | $(5,2)$ | `None` | — | 0 |
| Exterior, na reentrância | $(2,2{,}5)$ | $(7/2,5/2)$ | $p_3\to p_4$ | 0 |
| Fronteira | $(2,0)$ | $(2,0)$ | $p_5\to p_1$ | 2 |
| Exterior, com a semirreta atingindo um vértice | $(-1,0)$ | $(0,0)$ | $p_1\to p_2$ | 0 |

Para interpretar o primeiro resultado, $p_4\to p_5$ tem vetor
$e=(-1,-7/2)$ e $p_0-u=(-23/7,0)$. O produto vale $-23/2<0$: o ponto
chega pela direita do lado e é interior. Para $p_0=(-1,1{,}5)$, o produto
vale $5/2>0$, confirmando o exterior.

Na figura, os segmentos tracejados terminam no primeiro encontro. O caso
da reentrância mostra que estar dentro do retângulo delimitador não basta
para estar dentro do polígono. Já o ponto na fronteira coincide com sua
própria primeira interseção.

<!-- figure-include: assignments/02-geometry/artifacts/q07_first_intersection.html?width=100%&height=810&caption=Figura 7 — Primeira interseção, lado associado e classificação dos seis pontos. -->
<iframe src="artifacts/q07_first_intersection.html" width="100%" height="810" title="interactive plot" frameborder="0"></iframe>

**Figura 7 — Primeira interseção, lado associado e classificação dos seis pontos.**
<!-- figure-include-end -->

### Custo e implementação

A busca `first_horizontal_intersection` percorre as arestas e conserva
apenas a interseção mais próxima, junto com seu lado: **$O(n)$** de tempo e
**$O(1)$** de espaço auxiliar. Depois disso,
`locate_from_first_intersection` classifica o ponto em **$O(1)$**.

A [busca completa está no apêndice](#ap-primeira-intersecao). O trecho
abaixo mostra a decisão pelo sinal, aplicada depois de verificar se há
interseção e se $u$ coincide com $p_0$.

<details>
<summary>Ver decisão pelo sinal do produto vetorial</summary>

<!-- snippet-include: cpp/src/geometry/algorithms.cpp#q07-side-decision -->
```cpp
    const int side = sign(cross(edge, u_to_point));

    // A Questao 7 assume que o poligono esta orientado no sentido
    // horario. Nesse caso, seu interior esta a direita de cada lado.
    if (side < 0) {
        return 1; // interior
    }

    if (side > 0) {
        return 0; // exterior
    }
```
<!-- snippet-include-end -->

</details>

## Apêndice — Implementações selecionadas

Os trechos abaixo vêm dos arquivos C++ canônicos. Reúnem implementações
mais extensas usadas nas explicações, sem código de visualização.

### Disjunção entre triângulos {#ap-disjuncao}

<details>
<summary>Ver implementação completa de <code>triangles_are_disjoint</code></summary>

<!-- snippet-include: cpp/src/geometry/algorithms.cpp#q05-triangle-disjointness -->
```cpp
bool triangles_are_disjoint(const Triangle2& first, const Triangle2& second) {
    // Triangulos degenerados nao fazem parte do dominio desta funcao.
    if (is_zero(oriented_area(first)) || is_zero(oriented_area(second))) {
        throw std::invalid_argument(
            "triangles_are_disjoint: triangles cannot be degenerate");
    }

    // Cada triangulo possui tres lados.
    const Segment2 first_edges[] = {
        {first[0], first[1]},
        {first[1], first[2]},
        {first[2], first[0]},
    };

    const Segment2 second_edges[] = {
        {second[0], second[1]},
        {second[1], second[2]},
        {second[2], second[0]},
    };

    // Busca exaustiva de intersecoes entre todos os lados dos dois triangulos.
    for (const Segment2& first_edge : first_edges) {
        for (const Segment2& second_edge : second_edges) {
            // Se houver interseccao entre algum par de lados, os triangulos nao sao
            // disjuntos.
            if (segments_intersect(first_edge, second_edge)) {
                return false;
            }
        }
    }

    // O primeiro triangulo esta completamente dentro do segundo?
    for (const Point2& point : first) {
        if (locate_point_in_triangle(point, second) != 0) {
            return false;
        }
    }

    // O segundo triangulo esta completamente dentro do primeiro?
    for (const Point2& point : second) {
        if (locate_point_in_triangle(point, first) != 0) {
            return false;
        }
    }

    // Se nenhum dos casos acima ocorreu, os triangulos sao disjuntos.
    return true;
}
```
<!-- snippet-include-end -->

</details>

### Convexidade {#ap-convexidade}

<details>
<summary>Ver algoritmo completo de convexidade</summary>

<!-- snippet-include: cpp/src/geometry/algorithms.cpp#q06-convexity -->
```cpp
bool is_convex(const Polygon2& polygon) {

    if (polygon.size() < 3) {
        throw std::invalid_argument(
            "is_convex: polygon must have at least three vertices");
    }

    int reference_orientation = 0;

    const std::size_t n = polygon.size();

    // O(n) algo: itera sobre todos os vertices do poligono
    for (std::size_t i = 0; i < n; ++i) {
        const Point2& a = polygon[i];
        const Point2& b = polygon[(i + 1) % n];
        const Point2& c = polygon[(i + 2) % n];

        const Vector2 ab = {
            b.x - a.x,
            b.y - a.y,
        };

        const Vector2 bc = {
            c.x - b.x,
            c.y - b.y,
        };

        const int current_orientation = sign(cross(ab, bc));

        // Um giro nulo significa que tres vertices consecutivos sao
        // colineares. Nesse caso, o vertice intermediario e redundante
        // e o poligono nao possui a representacao minima adotada.
        if (current_orientation == 0) {
            return false;
        }

        // A primeira orientacao define o sentido esperado
        // para todos os demais vertices.
        if (reference_orientation == 0) {
            reference_orientation = current_orientation;
            continue;
        }

        // Uma mudanca de sinal indica uma mudanca no sentido do giro
        // e, portanto, a existencia de uma concavidade.
        if (current_orientation != reference_orientation) {
            return false;
        }
    }

    // Todos os vertices produzem giros estritamente no mesmo sentido.
    return true;
}
```
<!-- snippet-include-end -->

</details>

### Busca da primeira interseção {#ap-primeira-intersecao}

<details>
<summary>Ver implementação completa de <code>first_horizontal_intersection</code></summary>

<!-- snippet-include: cpp/src/geometry/algorithms.cpp#q07-first-intersection -->
```cpp
std::optional<RayIntersection> first_horizontal_intersection(const Point2& point,
                                                             const Polygon2& polygon) {
    if (polygon.size() < 3) {
        throw std::invalid_argument(
            "first_horizontal_intersection: polygon must have at least three vertices");
    }

    std::optional<RayIntersection> first_intersection;
    const std::size_t n = polygon.size();

    // O(n): percorre cada lado do poligono uma unica vez.
    for (std::size_t i = 0; i < n; ++i) {
        const Point2& a = polygon[i];
        const Point2& b = polygon[(i + 1) % n];

        // Vetor AB = B - A, correspondente ao lado atual do poligono.
        const Vector2 ab = {
            b.x - a.x,
            b.y - a.y,
        };

        // Vetor AP = P - A, do vertice A ate o ponto p0.
        const Vector2 ap = {
            point.x - a.x,
            point.y - a.y,
        };

        // Se p0 pertence ao lado AB, a primeira intersecao e o proprio p0.
        // Esse caso sera posteriormente classificado como fronteira.
        if (sign(cross(ab, ap)) == 0 &&
            point.x >= std::min(a.x, b.x) - DEFAULT_TOLERANCE &&
            point.x <= std::max(a.x, b.x) + DEFAULT_TOLERANCE &&
            point.y >= std::min(a.y, b.y) - DEFAULT_TOLERANCE &&
            point.y <= std::max(a.y, b.y) + DEFAULT_TOLERANCE) {
            return RayIntersection{
                point,
                i,
            };
        }

        // Caso especial: a semirreta horizontal coincide com um lado
        // horizontal do poligono.
        if (almost_equal(a.y, b.y)) {
            const bool left_is_a = a.x < b.x;
            const Point2& u = left_is_a ? a : b;

            // Se p0 esta alinhado com esse lado e antes de seu extremo
            // esquerdo, esse vertice e a primeira intersecao u.
            if (almost_equal(point.y, a.y) && point.x < u.x - DEFAULT_TOLERANCE) {
                // Em u encontram-se dois lados. Para a classificacao,
                // guarda o lado incidente que nao e horizontal.
                const std::size_t edge_index =
                    left_is_a ? (i + n - 1) % n : (i + 1) % n;

                // Mantem somente a intersecao mais proxima de p0.
                if (!first_intersection || u.x < first_intersection->point.x) {
                    first_intersection = RayIntersection{
                        u,
                        edge_index,
                    };
                }
            }

            continue;
        }

        const double min_y = std::min(a.y, b.y);
        const double max_y = std::max(a.y, b.y);

        // Se a horizontal que passa por p0 nao atravessa o intervalo
        // vertical do lado AB, esse lado nao pode ser intersectado.
        //
        // O intervalo e tratado de forma semiaberta para evitar que um
        // vertice compartilhado seja considerado duas vezes.
        if (point.y <= min_y + DEFAULT_TOLERANCE ||
            point.y > max_y + DEFAULT_TOLERANCE) {
            continue;
        }

        // Calcula a coordenada x da intersecao entre a horizontal
        // y = point.y e o segmento AB.
        //
        // Parametrizando o lado pela coordenada y:
        //
        // x = a.x + (y - a.y) * (b.x - a.x) / (b.y - a.y)
        const double x = a.x + (point.y - a.y) * (b.x - a.x) / (b.y - a.y);

        // A semirreta parte de p0 para a direita, portanto intersecoes
        // localizadas a esquerda de p0 sao descartadas.
        if (x <= point.x + DEFAULT_TOLERANCE) {
            continue;
        }

        // Como todas as intersecoes possuem y = point.y, basta comparar
        // suas coordenadas x para obter aquela mais proxima de p0.
        if (!first_intersection || x < first_intersection->point.x) {
            first_intersection = RayIntersection{
                {x, point.y},
                i,
            };
        }
    }

    // std::nullopt indica que a semirreta nao encontrou o poligono.
    return first_intersection;
}
```
<!-- snippet-include-end -->

</details>
