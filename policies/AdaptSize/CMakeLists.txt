cmake_minimum_required(VERSION 3.15)
project(adaptsize)

set(CMAKE_CXX_STANDARD 17)

find_package(pybind11 REQUIRED)

# Source list
add_library(adaptsize MODULE
    bindings.cpp
    adaptsize_code/lru_variants.cpp
    adaptsize_code/utils/random_helper.cpp
)

# include directories
target_include_directories(adaptsize PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/adaptsize_code
    ${CMAKE_CURRENT_SOURCE_DIR}/adaptsize_code/cache
    ${CMAKE_CURRENT_SOURCE_DIR}/adaptsize_code/utils
)

# Python module suffix fix (Windows)
if (WIN32)
    set_target_properties(adaptsize PROPERTIES SUFFIX ".pyd")
endif()

target_link_libraries(adaptsize PRIVATE pybind11::module)











