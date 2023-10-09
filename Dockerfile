FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y apt-utils build-essential clang-12 git-lfs pkg-config python3 python3-pip cmake curl zip unzip tar ranger
    # git lfs install

RUN cd /root && \
    git clone https://github.com/Microsoft/vcpkg.git && \
    ./vcpkg/bootstrap-vcpkg.sh -disableMetrics && \
    ./vcpkg/vcpkg install hexl

# RUN git clone https://github.com/menonsamir/spiral.git /root/spiral

WORKDIR /root/spiral

COPY . .

RUN pip install tabulate

RUN python3 select_params.py 20 256
