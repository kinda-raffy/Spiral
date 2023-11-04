# Ubuntu Installation Instructions

To install Spiral on a fresh installation of Ubuntu 20.04 without
[our build system](../README.md#build-system), proceed with these instructions,
otherwise refer to the [general](../README.md) instructions.

Note: These instructions assume the logged-in user is called "ubuntu". Without
our build system, consider this step as mandatory.

# Installation and Setup

The following commands will install the required dependencies and setup the
Ubuntu environment for Spiral.

```bash
sudo apt-get update
sudo apt-get install -y \
    apt-utils \
    build-essential \
    clang-12 \
    git-lfs \
    pkg-config \
    python3 \
    python3-pip \
    cmake
```

The following command is optional, but highly recommended for development.

```bash
sudo apt-get install -y \
    gdb \
    neovim \
    ranger \
    htop \
    tar \
    unzip \
    zip \
    curl
```

Then, `cd` into the user directory:

```bash
cd /home/ubuntu
```

Clone the Spiral repository:

```bash
git clone https://github.com/kinda-raffy/Spiral.git Spiral
```

Download and install vcpkg which we use as our package manager:

```bash
git clone https://github.com/Microsoft/vcpkg.git vcpkg
./vcpkg/bootstrap-vcpkg.sh -disableMetrics
```

Finally, install the required packages:

```bash
./vcpkg/vcpkg install hexl nlohmann-json
pip install tabulate
```

## Build Instructions

The Client and Server are treated as two separate executables and will require
separate terminals to run. To do this, create two terminals and follow the
instructions for _both_ terminals unless otherwise specified.

1. `cd` into the root of the repository.
    ```bash
    cd /home/ubuntu/Spiral
    ```
2. Decide on the database configuration you would like to use. Certain
   configurations, such as the database and element size, are required
   at compilation. This [section](README.md#popular-configurations) has some
   popular
   configurations. For this example, we will use a database of size
   `2^20` with elements of `32` bytes each. This configuration has the
   build folder name of `build_20_32`.
3. Generate the build files. Note: replace `build_20_32` with the build folder
   name of your desired database configuration. This command can be ran in any
   of the two terminals.
   ```bash
   cmake -DCMAKE_BUILD_TYPE=Release \
         -DCMAKE_TOOLCHAIN_FILE=/home/ubuntu/vcpkg/scripts/buildsystems/vcpkg.cmake \
         -DUSE_TIMERLOG=ON \
         -DUSE_NATIVELOG=OFF \
         -DUSE_LOG=ON \
         -S /home/ubuntu/Spiral -B /home/ubuntu/Spiral/build_20_32  # Ensure you replace build_20_32 with your build folder name.
   ```
4. Build the Client and Server executables. Over here, you will need to specify
   a number of build parameters. These parameters are determined during
   automatic parameter selection, and can be found in the 'build
   options' of the [configuration](#popular-configurations) table.
    1. On the **client** terminal, specify the `Client` target.
       ```bash
       cmake --build /home/ubuntu/Spiral/build_20_32 \
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
       cmake --build /home/ubuntu/Spiral/build_20_32 \
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

## Execution Instructions

These instructions assume you have the two terminals from
the [build process](#build-instructions) open.

1. On the **client** terminal, run the `Client` executable.
    ```bash
    ./build_20_32/Client/Client 8 7 1234
    ```
2. On the **server** terminal, run the `Server` executable.
    ```bash
    ./build_20_32/PIR_Server/Server 8 7 1234
    ```
