#include <pybind11/pybind11.h>
#include "lru_variants.h"
#include "request.h"

namespace py = pybind11;

PYBIND11_MODULE(adaptsize, m) {

    py::class_<AdaptSizeCache>(m, "AdaptSizeCache")
        .def(py::init<>())
        .def("set_size", &AdaptSizeCache::setSize)
        .def("lookup", [](AdaptSizeCache &cache, int64_t id, int64_t size) {
            SimpleRequest req(id, size);
            return cache.lookup(req);
        })
        .def("admit", [](AdaptSizeCache &cache, int64_t id, int64_t size) {
            SimpleRequest req(id, size);
            cache.admit(req);
        });
}
