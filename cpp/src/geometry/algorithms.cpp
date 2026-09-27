#include <algorithm>
#include <stdexcept>

#include "tca/geometry/algorithms.hpp"
#include "tca/geometry/numeric.hpp"
#include "tca/geometry/primitives.hpp"

namespace tca::geometry {

// snippet:start q05-triangle-disjointness
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
// snippet:end q05-triangle-disjointness

// snippet:start q06-convexity
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
// snippet:end q06-convexity

// snippet:start q07-first-intersection
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
// snippet:end q07-first-intersection

// snippet:start q07-location
int locate_from_first_intersection(const Point2& point, const Polygon2& polygon,
                                   const std::optional<RayIntersection>& intersection) {
    if (polygon.size() < 3) {
        throw std::invalid_argument("locate_from_first_intersection: polygon must have "
                                    "at least three vertices");
    }

    // Se nao existe intersecao, a semirreta pode seguir ate o infinito
    // sem atravessar a fronteira. Logo, p0 esta no exterior.
    if (!intersection) {
        return 0;
    }

    // Ponto u: primeira intersecao da semirreta com o poligono.
    const Point2& u = intersection->point;

    // Se u coincide com p0, entao p0 pertence a fronteira.
    if (almost_equal(point.x, u.x) && almost_equal(point.y, u.y)) {
        return 2;
    }

    // Indice i do lado pi -> pi+1 associado a primeira intersecao.
    const std::size_t i = intersection->edge_index;

    if (i >= polygon.size()) {
        throw std::invalid_argument(
            "locate_from_first_intersection: invalid edge index");
    }

    // Recupera os vertices do lado pi -> pi+1.
    const Point2& a = polygon[i];
    const Point2& b = polygon[(i + 1) % polygon.size()];

    // Vetor correspondente ao lado orientado pi -> pi+1.
    const Vector2 edge = {
        b.x - a.x,
        b.y - a.y,
    };

    // Vetor de u ate p0.
    const Vector2 u_to_point = {
        point.x - u.x,
        point.y - u.y,
    };

    // O sinal do produto vetorial determina de que lado da aresta
    // orientada encontra-se p0:
    //
    // side < 0 -> direita
    // side > 0 -> esquerda
    // snippet:start q07-side-decision
    const int side = sign(cross(edge, u_to_point));

    // A Questao 7 assume que o poligono esta orientado no sentido
    // horario. Nesse caso, seu interior esta a direita de cada lado.
    if (side < 0) {
        return 1; // interior
    }

    if (side > 0) {
        return 0; // exterior
    }
    // snippet:end q07-side-decision

    throw std::logic_error(
        "locate_from_first_intersection: ambiguous intersection edge");
}
// snippet:end q07-location

} // namespace tca::geometry