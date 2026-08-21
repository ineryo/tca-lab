cmake_minimum_required(VERSION 4.2...4.4)

# =============================================================================
# Project
# =============================================================================

# scikit-build-core defines SKBUILD and the SKBUILD_PROJECT_* variables.
# When CMake is invoked directly (e.g. VS Code CMake Tools), those variables
# do not exist, so we provide a standalone fallback.
if(SKBUILD)
    project(
        ${SKBUILD_PROJECT_NAME}
        VERSION ${SKBUILD_PROJECT_VERSION}
        LANGUAGES CXX
    )
    set(TCA_BUILD_CONTEXT "scikit-build-core")
else()
    project(
        tca
        VERSION 0.1.0
        LANGUAGES CXX
    )
    set(TCA_BUILD_CONTEXT "standalone-cmake")
endif()

message(STATUS "TCA build context: ${TCA_BUILD_CONTEXT}")

# =============================================================================
# C++ configuration
# =============================================================================

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# =============================================================================
# Python
# =============================================================================

# When CMake is invoked directly, prefer the uv-managed virtual environment
# belonging to this repository.
#
# During a scikit-build-core build, Python discovery is already managed by
# the isolated build environment, so we do not override it.

if(NOT SKBUILD AND NOT DEFINED Python_EXECUTABLE)
    if(WIN32)
        set(_TCA_VENV_PYTHON
            "${CMAKE_SOURCE_DIR}/.venv/Scripts/python.exe"
        )
    else()
        set(_TCA_VENV_PYTHON
            "${CMAKE_SOURCE_DIR}/.venv/bin/python"
        )
    endif()

    if(EXISTS "${_TCA_VENV_PYTHON}")
        set(
            Python_EXECUTABLE
            "${_TCA_VENV_PYTHON}"
            CACHE FILEPATH
            "Python interpreter used by TCA"
        )
    endif()
endif()

find_package(
    Python 3.12
    REQUIRED
    COMPONENTS
        Interpreter
        Development.Module
)

# The project is intentionally pinned to the Python 3.12 family.
if(
    NOT Python_VERSION_MAJOR EQUAL 3
    OR NOT Python_VERSION_MINOR EQUAL 12
)
    message(
        FATAL_ERROR
        "TCA requires Python 3.12.x, but CMake found "
        "${Python_VERSION} at ${Python_EXECUTABLE}"
    )
endif()

message(STATUS "Python executable: ${Python_EXECUTABLE}")
message(STATUS "Python version:    ${Python_VERSION}")

# =============================================================================
# pybind11
# =============================================================================

# Use CMake's modern FindPython integration.
set(PYBIND11_FINDPYTHON ON)

# First try the normal CMake lookup.
#
# This normally succeeds when the project is built through scikit-build-core,
# because pybind11 is part of the isolated build environment.
find_package(pybind11 CONFIG QUIET)

# When CMake is invoked directly (for example by VS Code CMake Tools),
# pybind11 usually lives inside the project's virtual environment and its
# CMake package directory is not automatically part of CMAKE_PREFIX_PATH.
if(NOT pybind11_FOUND)

    execute_process(
        COMMAND
            "${Python_EXECUTABLE}"
            -c
            "import pybind11; print(pybind11.get_cmake_dir())"

        RESULT_VARIABLE
            _TCA_PYBIND11_RESULT

        OUTPUT_VARIABLE
            _TCA_PYBIND11_CMAKE_DIR

        ERROR_VARIABLE
            _TCA_PYBIND11_ERROR

        OUTPUT_STRIP_TRAILING_WHITESPACE
        ERROR_STRIP_TRAILING_WHITESPACE
    )

    if(NOT _TCA_PYBIND11_RESULT EQUAL 0)
        message(
            FATAL_ERROR
            "pybind11 was not found by CMake and could not be located "
            "through Python.\n"
            "Python executable:\n"
            "  ${Python_EXECUTABLE}\n\n"
            "Python error:\n"
            "  ${_TCA_PYBIND11_ERROR}"
        )
    endif()

    # Defensive cleanup in case the returned path is quoted.
    string(
        REGEX REPLACE
        "^\"(.*)\"$"
        "\\1"
        _TCA_PYBIND11_CMAKE_DIR
        "${_TCA_PYBIND11_CMAKE_DIR}"
    )

    # Convert a Windows-native path to CMake's preferred forward-slash form.
    file(
        TO_CMAKE_PATH
        "${_TCA_PYBIND11_CMAKE_DIR}"
        _TCA_PYBIND11_CMAKE_DIR
    )

    message(
        STATUS
        "pybind11 discovered through Python: "
        "${_TCA_PYBIND11_CMAKE_DIR}"
    )

    if(
        NOT EXISTS
        "${_TCA_PYBIND11_CMAKE_DIR}/pybind11Config.cmake"
    )
        message(
            FATAL_ERROR
            "Python returned a pybind11 CMake directory, but "
            "pybind11Config.cmake was not found there:\n"
            "  ${_TCA_PYBIND11_CMAKE_DIR}"
        )
    endif()

    set(
        pybind11_DIR
        "${_TCA_PYBIND11_CMAKE_DIR}"
        CACHE PATH
        "Directory containing pybind11Config.cmake"
        FORCE
    )

    find_package(
        pybind11
        CONFIG
        REQUIRED
    )
endif()

message(STATUS "pybind11 version:   ${pybind11_VERSION}")
message(STATUS "pybind11 CMake dir: ${pybind11_DIR}")
# =============================================================================
# Native C++ library
# =============================================================================

# Discover sorting implementations from the *_sort.cpp naming convention.
file(
    GLOB
    TCA_SORTING_SOURCES
    CONFIGURE_DEPENDS
    "${CMAKE_CURRENT_SOURCE_DIR}/cpp/src/algorithms/sorting/*_sort.cpp"
)

list(
    SORT
    TCA_SORTING_SOURCES
)

# -------------------------------------------------------------------------
# Generate the sorting catalog used by the C++ registry.
# -------------------------------------------------------------------------

set(
    TCA_GENERATED_INCLUDE_DIR
    "${CMAKE_CURRENT_BINARY_DIR}/generated"
)

set(
    TCA_SORTING_CATALOG_DIR
    "${TCA_GENERATED_INCLUDE_DIR}/tca/algorithms/sorting"
)

set(
    TCA_SORTING_CATALOG
    "${TCA_SORTING_CATALOG_DIR}/algorithms.def"
)

file(
    MAKE_DIRECTORY
    "${TCA_SORTING_CATALOG_DIR}"
)

file(
    WRITE
    "${TCA_SORTING_CATALOG}"
    ""
)

foreach(
    TCA_SORTING_SOURCE
    IN LISTS TCA_SORTING_SOURCES
)
    get_filename_component(
        TCA_SORTING_FUNCTION
        "${TCA_SORTING_SOURCE}"
        NAME_WE
    )

    string(
        REGEX REPLACE
        "_sort$"
        ""
        TCA_SORTING_METHOD
        "${TCA_SORTING_FUNCTION}"
    )

    file(
        APPEND
        "${TCA_SORTING_CATALOG}"
        "TCA_SORTING_ALGORITHM(${TCA_SORTING_METHOD}, ${TCA_SORTING_FUNCTION})\n"
    )
endforeach()

set(
    TCA_CPP_SOURCES
    cpp/src/core.cpp
    cpp/src/algorithms/sorting/registry.cpp
    ${TCA_SORTING_SOURCES}
)

add_library(
    tca_cpp
    STATIC
    ${TCA_CPP_SOURCES}
)

target_include_directories(
    tca_cpp
    PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}/cpp/include

    PRIVATE
        ${TCA_GENERATED_INCLUDE_DIR}
)

target_compile_features(
    tca_cpp
    PUBLIC
        cxx_std_20
)

# Required for linking the static library into a Python extension on platforms
# where position-independent code is necessary.
set_target_properties(
    tca_cpp
    PROPERTIES
        POSITION_INDEPENDENT_CODE ON
)

# =============================================================================
# Python extension
# =============================================================================

set(
    TCA_BINDING_SOURCES
    cpp/bindings/module.cpp
    cpp/bindings/prng.cpp
    cpp/bindings/sorting.cpp
)

pybind11_add_module(
    _core
    MODULE
    ${TCA_BINDING_SOURCES}
)

target_link_libraries(
    _core
    PRIVATE
        tca_cpp
)

target_include_directories(
    _core
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/cpp/include
)

target_compile_features(
    _core
    PRIVATE
        cxx_std_20
)

# =============================================================================
# Installation
# =============================================================================

# scikit-build-core stages this module into the Python package.
#
# Windows:  _core*.pyd
# Linux:    _core*.so
# macOS:    _core*.so
install(
    TARGETS
        _core

    LIBRARY DESTINATION
        tca

    RUNTIME DESTINATION
        tca
)

# =============================================================================
# Configuration summary
# =============================================================================

message(STATUS "")
message(STATUS "------------------------------------------------------------")
message(STATUS " TCA configuration")
message(STATUS "------------------------------------------------------------")
message(STATUS " Project:          ${PROJECT_NAME}")
message(STATUS " Version:          ${PROJECT_VERSION}")
message(STATUS " Build context:    ${TCA_BUILD_CONTEXT}")
message(STATUS " C++ standard:     C++20")
message(STATUS " C++ compiler:     ${CMAKE_CXX_COMPILER}")
message(STATUS " Compiler ID:      ${CMAKE_CXX_COMPILER_ID}")
message(STATUS " Compiler version: ${CMAKE_CXX_COMPILER_VERSION}")
message(STATUS " Python:           ${Python_EXECUTABLE}")
message(STATUS " Python version:   ${Python_VERSION}")
message(STATUS " pybind11 version: ${pybind11_VERSION}")
message(STATUS "------------------------------------------------------------")
message(STATUS "")