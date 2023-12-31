cmake_minimum_required(VERSION 3.12)

set(CMAKE_C_COMPILER clang++-12)
set(CMAKE_CXX_COMPILER clang++-12)

project(Spiral VERSION 0.1 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_FLAGS_RELEASE "-g -std=c++17 -MD -march=native")
set(CMAKE_CXX_FLAGS_DEBUG "-g -std=c++17 -MD -march=native")
if (CMAKE_BUILD_TYPE STREQUAL "Release")
    message("Release build.")
    # WARN: Change this to -O3 for release
    message(WARNING "The release build is not optimised (-O0).")
    add_compile_options(-O3)
elseif (CMAKE_BUILD_TYPE STREQUAL "Debug")
    message("Debug build.")
    add_compile_options(-O3)
else()
    message("Unknown build type: ${CMAKE_BUILD_TYPE}, defaulting to -O3.")
    add_compile_options(-O3)
endif()
option(NOAVX512 "Disable AVX-512" OFF)
option(NOAVX2 "Disable AVX2" OFF)
if (NOAVX512)
    message("Disabling AVX-512")
    add_compile_options(-mno-avx512f)
endif()
if (NOAVX2)
    message("Disabling AVX2")
    add_compile_options(-mno-avx2)
endif()
if (NOCRT)
    message("Disabling CRT")
    add_compile_options(-DNOCRT=1)
endif()

option(USE_LOG "Enable logs from the modified implementation" OFF)
if(USE_LOG)
    message("Logging enabled.")
    add_definitions(-DLOG)
endif()
option(USE_TIMERLOG "Enable timer logging" OFF)
if(USE_TIMERLOG)
    message("Timer logging enabled.")
    add_definitions(-DTIMERLOG)
endif()
option(USE_NATIVELOG "Enable logs from the original implementation" OFF)
if(USE_NATIVELOG)
    message("Native logging enabled.")
    add_definitions(-DNATIVELOG)
endif()

find_package(HEXL CONFIG REQUIRED)
find_package(nlohmann_json CONFIG REQUIRED)
find_package(simdjson CONFIG REQUIRED)
find_package(Boost 1.83.0 REQUIRED)

add_subdirectory(Seperated)
add_subdirectory(Client)
add_subdirectory(PIR_Server)
