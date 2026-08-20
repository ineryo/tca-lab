#include "tca/algorithms/sorting/selection_sort.hpp"

#include <utility>

namespace tca::algorithms {

void selection_sort(std::span<double> values) {
    for (std::size_t index_i = 0; index_i < values.size(); ++index_i) { // i=(0)..(n-1)
        std::size_t marker = index_i;                                   //   m=i

        for (std::size_t index_j = index_i + 1; index_j < values.size();
             ++index_j) {                           //   j=(i+1)..(n)
            if (values[index_j] < values[marker]) { //       se xj < xm
                marker = index_j;                   //           m=j
            }
        }

        std::swap(values[index_i], values[marker]); //       swap(x_i, x_m)
    }
}

} // namespace tca::algorithms