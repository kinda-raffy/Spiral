cmake_minimum_required(VERSION 3.12)

#set(CMAKE_BUILD_TYPE "Release")
set(CMAKE_C_COMPILER clang++-12)
set(CMAKE_CXX_COMPILER clang++-12)

project(spiral VERSION 0.1 LANGUAGES CXX)

# CXX options
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_FLAGS_RELEASE "-g -std=c++17 -MD -march=native")
set(CMAKE_CXX_FLAGS_DEBUG "-g -std=c++17 -MD -march=native")

if (CMAKE_BUILD_TYPE STREQUAL "Release")
    message("Release build.")
    # WARN: Change this to -O3 for release
    message(WARNING "The release build is not optimised (-O0).")
    add_compile_options(-O0)
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

# main target
set(SRC_FILES src/spiral.cpp src/core.cpp src/constants.cpp src/poly.cpp src/util.cpp src/client.cpp src/testing.cpp)
set(HEADER_FILES include/spiral.h include/core.h include/constants.h include/poly.h include/util.h include/client.h include/testing.h)
add_executable(spiral ${SRC_FILES} ${HEADER_FILES})
target_include_directories(spiral PUBLIC include)
#target_include_directories(spiral PUBLIC /home/$ENV{USER}/vcpkg/installed/)
# Case: Create image under ubuntu user but run container under root.
target_include_directories(spiral PUBLIC /home/ubuntu/vcpkg/installed/)

# Must specify:
# -DCMAKE_TOOLCHAIN_FILE=/home/ubuntu/vcpkg/scripts/buildsystems/vcpkg.cmake

find_package(HEXL CONFIG REQUIRED)
target_link_libraries(spiral PRIVATE HEXL::hexl)

add_compile_definitions(
    TEXP=$(TEXP)
    TEXPRIGHT=$(TEXPRIGHT)
    TCONV=$(TCONV)
    TGSW=$(TGSW)
    QPBITS=$(QPBITS)
    PVALUE=$(PVALUE)
    QNUMFIRST=$(QNUMFIRST)
    QNUMREST=$(QNUMREST)
    OUTN=$(OUTN)
)