# Spiral 🍃

This repository contains the code
of [Spiral](https://github.com/menonsamir/spiral), which has been modified to
work alongside the Ethereum-PIR project.

## Build System

![Build System](.github/images/execution_environment.png)

Building Spiral can be complicated. To reduce the possibility for errors, I have
abstracted the setup process into individual containerised execution
environments. Each environment is based on an `Ubuntu` image, and contains all
the required dependencies to build, run and debug Spiral applications.

The source code of Spiral is hosted on your local machine, and is mounted
into `/tmp/Spiral` of the respective execution environment. This 'volume
mount' allows you to edit the source code on your local machine, and have the
changes reflect directly in the environment.

## Build Prerequisites

- An x86-64 machine is a must. The code uses Intel-based SIMD instructions to
  accelerate the query-database processing.
- [Docker](https://docs.docker.com/get-docker/) is required to build and run the
  execution environments.
- A native Linux environment is **strongly** preferred. This process has been
  tested on an [Arch Linux](https://archlinux.org/) machine.
- [CLion](https://www.jetbrains.com/clion/) is the recommended IDE for
  development.

### Building on ARM-based machines

Although an x86-64 machine is required, ARM machines (such as M1,2,3 Macs) might
be able to run Spiral using an x86_64 emulator. An emulator is very
expensive, so ensure you have adequate resources to run Spiral.

## Build Instructions

Clone the repository onto your local machine:

```bash
git clone https://github.com/kinda-raffy/Spiral.git Spiral
```

or

```bash
gh repo clone kinda-raffy/Spiral Spiral
```

Then, `cd` into the root of the repository:

```bash
cd Spiral
```

### CLion

1. Create a toolchain image using Docker:
    ```bash
    docker build -t spiral_toolchain .
    ```
2. Open the root project in CLion.
3. Load the parent `./CMakeLists.txt` file as the CMake project.
4. Go to `File > Settings > Build, Execution, Deployment > Toolchains`, and
   add the built Docker image as a new toolchain called 'Docker_Spiral'.
5. CLion will automatically detect pre-configured build profiles and should
   build the project automatically.

### Command Line

First create a single toolchain image using Docker:

```bash
docker build -t spiral_toolchain .
```

The Client and Server are separate applications that must be run adjacent to
one another. To do this, create two terminals and follow the instructions
for _both_ terminals unless otherwise specified.

1. Run the execution environment with the appropriate container settings.
   ```bash
   docker run -it \
          -u root \
          -v /HOST_PATH_TO_SPIRAL/Spiral:/tmp/Spiral \
          -v /HOST_PATH_TO_SPIRAL/Spiral/Process_Workspace:/home/ubuntu/Process_Workspace \
          --rm spiral_toolchain:latest \
          /bin/bash -c "cd /tmp/Spiral; exec bash"
   ```
   Ensure that the `HOST_PATH_TO_SPIRAL` is the path to the root of the
   repository on your local machine (Excluding the root project folder
   named `Spiral/`).
2. Decide on the database configuration you would like to use. Certain
   configurations, such as the database and element size, are required
   at compilation. This [section](#popular-configurations) has some popular
   configurations. For this example, we will use a database of size
   `2^20` with elements of `32` bytes each. This configuration has the
   build folder name of `build_20_32`.
3. Generate the build files. Note: replace `build_20_32` with the build folder
   name of your desired database configuration. This command can be ran in any
   of the two terminals.
    ```bash
    /usr/bin/cmake -DCMAKE_BUILD_TYPE=Release \
                   -DCMAKE_TOOLCHAIN_FILE=/home/ubuntu/vcpkg/scripts/buildsystems/vcpkg.cmake \
                   -DUSE_TIMERLOG=ON \
                   -DUSE_NATIVELOG=OFF \
                   -DUSE_LOG=ON \
                   -S /tmp/Spiral -B /tmp/Spiral/build_20_32  # Ensure you replace build_20_32 with your build folder name.
    ```
4. Build the Client and Server executables. Over here, you will need to specify
   a number of build parameters. These parameters are determined during
   automatic parameter selection, and can be found in the 'build
   options' of the [configuration](#popular-configurations) table.
    1. On the **client** terminal, specify the `Client` target.
       ```bash
       /usr/bin/cmake --build /tmp/Spiral/build_20_32 \
                      --target Client -v -j4 \
                      -- PARAMSET=PARAMS_DYNAMIC \
                         TEXP=4 \
                         TEXPRIGHT=56 \
                         TCONV=4 \
                         TGSW=4 \
                         QPBITS=14 \
                         PVALUE=4 \
                         QNUMFIRST=1 \
                         QNUMREST=0 \
                         OUTN=2
       ```
    2. On the **server** terminal, specify the `Server` target.
        ```bash
        /usr/bin/cmake --build /tmp/Spiral/build_20_32 \
                       --target Server -v -j4 \
                       -- PARAMSET=PARAMS_DYNAMIC \
                          TEXP=4 \
                          TEXPRIGHT=56 \
                          TCONV=4 \
                          TGSW=4 \
                          QPBITS=14 \
                          PVALUE=4 \
                          QNUMFIRST=1 \
                          QNUMREST=0 \
                          OUTN=2
        ```

### Popular Configurations

| Build Folder Name | Description                                                | Build Options                                                                                                        |
|-------------------|------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------|
| `build_20_256`    | Database size of `2^20` with elements of `256` bytes each. | `-- PARAMSET=PARAMS_DYNAMIC TEXP=8 TEXPRIGHT=56 TCONV=4 TGSW=9 QPBITS=21 PVALUE=256 QNUMFIRST=1 QNUMREST=0 OUTN=2`   |
| `build_10_32`     | Database size of `2^10` with elements of `32` bytes each.  | `-- PARAMSET=PARAMS_DYNAMIC TEXP=4 TEXPRIGHT=56 TCONV=4 TGSW=4 QPBITS=14 PVALUE=4 QNUMFIRST=1 QNUMREST=0 OUTN=2`     |
| `build_20_32`     | Database size of `2^20` with elements of `32` bytes each.  | `-- PARAMSET=PARAMS_DYNAMIC TEXP=4 TEXPRIGHT=56 TCONV=4 TGSW=5 QPBITS=16 PVALUE=16 QNUMFIRST=1 QNUMREST=0 OUTN=2`    |
| `build_30_32`     | Database size of `2^30` with elements of `32` bytes each.  | `-- PARAMSET=PARAMS_DYNAMIC TEXP=16 TEXPRIGHT=56 TCONV=4 TGSW=13 QPBITS=21 PVALUE=256 QNUMFIRST=1 QNUMREST=0 OUTN=2` |

## Execution Instructions

### CLion

1. After building the CMake project, select the build option and the target you
   would like to run.
2. Run (Shift+F10) or Debug (Shift+F9) the selected target.

### Command Line

These instructions assume you have the two terminals from
the [build process](#build-instructions) still open. Otherwise, re-run the
execution environments on two separate terminals.

1. On the **client** terminal, run the `Client` executable.
    ```bash
    /tmp/Spiral/build_20_32/Client/Client 8 7 1234
    ```
2. On the **server** terminal, run the `Server` executable.
    ```bash
    /tmp/Spiral/build_20_32/PIR_Server/Server 8 7 1234
    ```

#### Mandatory Considerations

- The `Client` and `Server` executables must be run with the same parameters to
  ensure message verification is successful.
- The `Client` should always be ran before the `Server`. Otherwise, the
  receiving pipe on `Server` might hang.

## Issues

If you face any issues during the build or execution process, please open an
issue in this repository. Provide in-depth details of the following:

- Your environment (OS, CPU, RAM).
- All the commands you have tried to run and their ouputs to the lead up to this
  issue.
- The full error message you are receiving.