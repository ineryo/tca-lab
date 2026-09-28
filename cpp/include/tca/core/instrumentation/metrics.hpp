#pragma once

#include <cstddef>

namespace tca::instrumentation {

/** Accumulated semantic operations performed by an instrumented algorithm. */
struct Metrics {
#define TCA_METRIC(name) std::size_t name = 0;

#include "tca/core/instrumentation/metrics.def"

#undef TCA_METRIC

    /** Resets every metric counter to zero. */
    void reset() noexcept {
#define TCA_METRIC(name) name = 0;

#include "tca/core/instrumentation/metrics.def"

#undef TCA_METRIC
    }

    /** Calls @p visitor with each metric name and its current value. */
    template <typename Visitor> void for_each_metric(Visitor&& visitor) const {
#define TCA_METRIC(name) visitor(#name, name);

#include "tca/core/instrumentation/metrics.def"

#undef TCA_METRIC
    }
};

} // namespace tca::instrumentation