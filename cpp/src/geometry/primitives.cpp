#include <algorithm>
#include <stdexcept>

#include "tca/geometry/numeric.hpp"
#include "tca/geometry/primitives.hpp"

namespace tca::geometry {

namespace {

int orientation(const Point2& a, const Point2& b, const Point2& point) {
    // vetor AB = B - A
    const Vector2 ab = {
        b.x - a.x,
        b.y - a.y,
    };

    // vetor AP = P - A
    const Vector2 ap = {
        point.x - a.x,
        point.y - a.y,
    };

    // O sinal do produto vetorial AB x AP indica a orientação do ponto P
    // CCW-orientado
    // Positivo: P está à esquerda da reta AB (sentido anti-horário)
    // Negativo: P está à direita da reta AB (sentido horário)
    // Zero: P está colinear com a reta AB
    return sign(cross(ab, ap));
}

bool point_on_segment(const Point2& point, const Segment2& segment) {
    const Point2& a = segment[0];
    const Point2& b = segment[1];

    // Basicamente o algoritmo quer garantir que:
    // 1. P pertence a AB
    // 2. P esta entre A e B

    // O ponto deve pertencer à reta AB
    // Isto é: a orientação do ponto em relação à reta AB deve ser zero (colinearidade)
    if (orientation(a, b, point) != 0) {
        return false;
    }

    // O ponto deve estar dentro do retângulo delimitador do segmento AB (bounding box)
    return point.x >= std::min(a.x, b.x) - DEFAULT_TOLERANCE &&
           point.x <= std::max(a.x, b.x) + DEFAULT_TOLERANCE &&
           point.y >= std::min(a.y, b.y) - DEFAULT_TOLERANCE &&
           point.y <= std::max(a.y, b.y) + DEFAULT_TOLERANCE;
}

} // namespace

// snippet:start q01-pseudo-angle
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
// snippet:end q01-pseudo-angle

double cross(const Vector2& first, const Vector2& second) {
    return first.x * second.y - first.y * second.x;
}

// snippet:start q02-entre
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
// snippet:end q02-entre

double oriented_area(std::span<const Point2> vertices) {

    if (vertices.size() < 3) {
        throw std::invalid_argument(
            "oriented_area: polygon must have at least three vertices");
    }

    const Point2& origin = vertices[0];

    double twice_area = 0.0;

    for (std::size_t i = 1; i + 1 < vertices.size(); ++i) {
        const Vector2 first = {
            vertices[i].x - origin.x,
            vertices[i].y - origin.y,
        };

        const Vector2 next = {
            vertices[i + 1].x - origin.x,
            vertices[i + 1].y - origin.y,
        };

        twice_area += cross(first, next);
    }

    return 0.5 * twice_area;
}

// snippet:start q03-barycentric
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
// snippet:end q03-barycentric

int locate_point_in_triangle(const Point2& point, const Triangle2& triangle) {

    // 0: exterior
    // 1: interior
    // 2: fronteira

    const auto lambda = barycentric_coordinates(point, triangle);

    const int lambda_1 = sign(lambda[0]);
    const int lambda_2 = sign(lambda[1]);
    const int lambda_3 = sign(lambda[2]);

    // Alguma coordenada baricentrica negativa: ponto exterior.
    if (lambda_1 < 0 || lambda_2 < 0 || lambda_3 < 0) {
        return 0;
    }

    // Nenhuma negativa e pelo menos uma aproximadamente zero: fronteira.
    if (lambda_1 == 0 || lambda_2 == 0 || lambda_3 == 0) {
        return 2;
    }

    // Todas as coordenadas baricentricas sao positivas: interior.
    return 1;
}

bool segments_intersect(const Segment2& first, const Segment2& second) {
    const Point2& a = first[0];
    const Point2& b = first[1];

    const Point2& c = second[0];
    const Point2& d = second[1];

    // Orientações dos extremos C e D em relação à reta orientada AB.
    const int abc = orientation(a, b, c);
    const int abd = orientation(a, b, d);

    // Orientações dos extremos A e B em relação à reta orientada CD.
    const int cda = orientation(c, d, a);
    const int cdb = orientation(c, d, b);

    // Interseção própria: os extremos de cada segmento
    // estão em lados opostos da reta definida pelo outro.
    // isto e:
    // C e D devem estar em lados opostos da reta AB,
    // e A e B devem estar em lados opostos da reta CD.
    if (abc * abd < 0 && cda * cdb < 0) {
        return true;
    }

    // Casos de fronteira: contato em extremidades
    // ou segmentos colineares com sobreposição.

    // C pertence ao segmento AB.
    if (abc == 0 && point_on_segment(c, first)) {
        return true;
    }

    // D pertence ao segmento AB.
    if (abd == 0 && point_on_segment(d, first)) {
        return true;
    }

    // A pertence ao segmento CD.
    if (cda == 0 && point_on_segment(a, second)) {
        return true;
    }

    // B pertence ao segmento CD.
    if (cdb == 0 && point_on_segment(b, second)) {
        return true;
    }

    // Não ocorreu cruzamento próprio, contato em extremidade
    // nem sobreposição entre segmentos colineares.
    return false;
}

} // namespace tca::geometry