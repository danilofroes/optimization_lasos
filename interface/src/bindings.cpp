#include <pybind11/pybind11.h>
#include <pybind11/stl.h> // converter std::vector e std::string em dict e string do Python
#include "include/ILS.hpp"
#include "include/tabuSearch.hpp"
#include "include/simulatedAnnealing.hpp"
#include "include/greedy.hpp"

namespace py = pybind11;

PYBIND11_MODULE(meta_engine, m) {
    // Binding para ILS
    py::class_<ILS>(m, "ILS")
        .def(py::init<>())
        .def("solve", &ILS::solve)
        .def("setParametros", [](ILS& self, const py::object& obj) {
            std::string s = py::module_::import("json").attr("dumps")(obj).cast<std::string>();
            self.setParametros(json::parse(s));
        })
        .def("getResultados", [](const ILS& self) {
            return py::module_::import("json").attr("loads")(self.getResultados().dump());
        })
        .def("getNome", &ILS::getNome);

    // Binding para Tabu Search
    py::class_<TabuSearch>(m, "TabuSearch")
        .def(py::init<>())
        .def("solve", &TabuSearch::solve)
        .def("setParametros", [](TabuSearch& self, const py::object& obj) {
            std::string s = py::module_::import("json").attr("dumps")(obj).cast<std::string>();
            self.setParametros(json::parse(s));
        })
        .def("getResultados", [](const TabuSearch& self) {
            return py::module_::import("json").attr("loads")(self.getResultados().dump());
        })
        .def("getNome", &TabuSearch::getNome);

    // Binding para Simulated Annealing
    py::class_<SimulatedAnnealing>(m, "SimulatedAnnealing")
        .def(py::init<>())
        .def("solve", &SimulatedAnnealing::solve)
        .def("setParametros", [](SimulatedAnnealing& self, const py::object& obj) {
            std::string s = py::module_::import("json").attr("dumps")(obj).cast<std::string>();
            self.setParametros(json::parse(s));
        })
        .def("getResultados", [](const SimulatedAnnealing& self) {
            return py::module_::import("json").attr("loads")(self.getResultados().dump());
        })
        .def("getNome", &SimulatedAnnealing::getNome);

    // Binding para Greedy (Algoritmos Gulosos)
    py::class_<Greedy>(m, "Greedy")
        .def(py::init<>())
        .def("solve", &Greedy::solve)
        .def("setParametros", [](Greedy& self, const py::object& obj) {
            std::string s = py::module_::import("json").attr("dumps")(obj).cast<std::string>();
            self.setParametros(json::parse(s));
        })
        .def("getResultados", [](const Greedy& self) {
            return py::module_::import("json").attr("loads")(self.getResultados().dump());
        })
        .def("getNome", &Greedy::getNome);
}