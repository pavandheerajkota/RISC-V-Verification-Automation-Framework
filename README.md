# EEC283 Project - RISCV Verification Automation Framework

This repository captures the essential information regarding the project proposed for the EEC283 coursework. We (Team 7) are working on automating the RISC-V verification process. We will be using the existing RISC-V IPs and methodologies to demonstrate the proof of concept. A more detailed description of the project can be viewed here (insert link to proposal). 

As described in the proposal, we will be using the Ibex core to demonstrate our idea. In particular, we will using the Ibex Simple System infrastructure and its co-simulation environment. To get started, we first need to install the required tools to bring-up the exisitng environment. A detailed step-by-step guide is provided below for reference.

```
# Ibex - Spike Co‑Simulation Environment Setup

# Note: Execute the commands in the given order

# Setting the required environment variables

export RISCV_TOOL_PREFIX="/opt"
export RISCV="$RISCV_TOOL_PREFIX/riscv"
export NUM_CORES="$(nproc)" 
export VERILATOR_TAG="v4.220"

# Moving into the installation directory

cd /opt
mkdir src
cd src

# Installing system dependencies (common)

sudo apt-get update
sudo apt-get install -y \
  build-essential git curl wget ca-certificates ccache \
  autoconf automake libtool pkg-config \
  libmpc-dev libmpfr-dev libgmp-dev \
  bison flex texinfo gawk \
  libexpat-dev libelf-dev zlib1g-dev \
  python3 python3-pip python3-venv

# Installing verilator version 4.220 (Version 5.xx will not work with Ibex)

git clone --branch "$VERILATOR_TAG" https://github.com/verilator/verilator.git
cd verilator
autoconf
./configure --prefix="$RISCV_TOOL_PREFIX/verilator-$VERILATOR_TAG"
make -j"$NUM_CORES"
make install
cd ..

# Installing RISC-V GNU Toolchain

git clone https://github.com/riscv-collab/riscv-gnu-toolchain.git
cd riscv-gnu-toolchain
./configure --prefix="$RISCV" --with-arch=rv64imafdc_zicsr_zifencei_zba_zbb_zbc_zbs --with-abi=lp64d --enable-multilib
make -j"$NUM_CORES"
cd ..
export PATH="$RISCV_TOOL_PREFIX/riscv/bin:$RISCV_TOOL_PREFIX:$PATH"

# Installing Spike (Version specific to Ibex co-simulation)

git clone -b ibex_cosim https://github.com/lowRISC/riscv-isa-sim.git riscv-isa-sim-cosim
cd riscv-isa-sim-cosim
mkdir build
cd  build
../configure --enable-commitlog --enable-misaligned --prefix="$RISCV_TOOL_PREFIX/spike-cosim"
make -j8 install
export PKG_CONFIG_PATH="$RISCV_TOOL_PREFIX/spike-cosim/lib/pkgconfig"

# Ibex Setup









```
