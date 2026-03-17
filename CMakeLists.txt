cmake_minimum_required(VERSION 3.12)
project(MetaEngine)

set(CMAKE_CXX_STANDARD 17)

# processo para procurar a biblioteca pybind11
find_package(Python COMPONENTS Interpreter Development REQUIRED)
execute_process(
    COMMAND "${Python_EXECUTABLE}" -c "import pybind11; print(pybind11.get_cmake_dir())"
    OUTPUT_VARIABLE pybind11_DIR
    OUTPUT_STRIP_TRAILING_WHITESPACE
)
find_package(pybind11 REQUIRED)

include_directories(include)
include_directories(libs)

pybind11_add_module(
    meta_engine 
    src/bindings.cpp 
    src/ILS.cpp 
    src/tabuSearch.cpp 
    src/simulatedAnnealing.cpp
    src/greedy.cpp
    src/algGenetico.cpp
)