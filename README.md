# EEC283 Project - RISCV Verification Automation Framework

This repository captures the essential information regarding the project proposed for the EEC283 coursework. We are working on automating the RISC-V verification process. We will be using the existing RISC-V IPs and methodologies to demonstrate the proof of concept. A more detailed description of the project can be viewed [here](https://github.com/pavandheerajkota/EEC283_RISCV_Verification_Automation_Framework/blob/640b9225b172323abeb22027dcffc70e9e568391/EEC_283_Project_Proposal%20-%20Group7.pdf).

As described in the proposal, we will be using the Ibex core to demonstrate our idea. In particular, we will using the Ibex Simple System infrastructure and its co-simulation environment. To get started, we first need to install the required tools to bring-up the exisitng environment. A detailed step-by-step guide is provided below for reference.

## Ibex - Spike Co-Simulation Environment Setup

```
# Ibex - Spike Co‑Simulation Environment Setup

# Note: Execute the commands in the given order. Please use the sudo prefix with commands when installing/ downloading under the root directory

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
  export PATH="$RISCV_TOOL_PREFIX/verilator-$VERILATOR_TAG/bin:$PATH"

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

# Ibex cosim setup

  cd $HOME
  python3 -m venv ibex_setup
  source ibex_setup/bin/activate
  git clone https://github.com/lowRISC/ibex.git
  cd ibex

  # Edit file before proceeding - Comment out line 33 in the python_requirements.txt file available in the Ibex repository root
  ![image](https://github.com/user-attachments/assets/e8e1807a-4d9f-4e2a-9716-e6bf153c2e33)

  pip3 install -U -r python-requirements.txt
  sudo apt-get install libelf-dev
  sudo apt-get install srecord
  sudo ln -s /opt/riscv/bin/riscv64-unknown-elf-gcc /opt/riscv/bin/riscv32-unknown-elf-gcc
  sudo ln -s /opt/riscv/bin/riscv64-unknown-elf-objcopy /opt/riscv/bin/riscv32-unknown-elf-objcopy
  sudo ln -s /opt/riscv/bin/riscv64-unknown-elf-objdump /opt/riscv/bin/riscv32-unknown-elf-objdump
  cd examples/sw/benchmarks/coremark/ibex

  # Edit file before proceeding - Update line 7 in the core_portme.mak file as shown below -> RV_ISA = rv32im -> rv32im_zicsr
  ![image](https://github.com/user-attachments/assets/c4ad0125-ae20-4b7f-82c2-00c5e4c56285)

  cd ..
  fusesoc --cores-root=. run --target=sim --setup --build lowrisc:ibex:ibex_simple_system_cosim --RV32E=0 --RV32M=ibex_pkg::RV32MFast
  make -C ./examples/sw/benchmarks/coremark SUPPRESS_PCOUNT_DUMP=1
  build/lowrisc_ibex_ibex_simple_system_cosim_0/sim-verilator/Vibex_simple_system --meminit=ram,examples/sw/benchmarks/coremark/coremark.elf
```
After the running the final command, your output should be similar to the one shown below.

![image](https://github.com/user-attachments/assets/ef2f6a55-3900-4241-a7b3-5de68f9ea094)

## RISC-V Compliance Test Generation

The following section shows us the steps to automate the testcase generation process for compliance testing, given the cosim environment is already setup.

```
  git clone https://github.com/imphil/riscv-compliance.git
  cd riscv-compliance
  git checkout ibex

  export RISCV_TARGET=ibex
  export RISCV_ISA=rv32i
  export RISCV_PREFIX=riscv32-unknown-elf-
  export TARGET_SIM=<path/to/your/compiled/binary/from/the/setup/process>

  realpath ../examples/sw/simple_system/common/link.ld # Copy the output of this command.
  cd riscv-test-env/p/
  cp <Output of realpath command> ./
  cd -
  cd riscv-test-suite/rv32imc

  # Edit file before proceeding - Update line 46 in the MakeFile as shown below -> -march = rv32imc -> rv32imc_zicsr
  ![image](https://github.com/user-attachments/assets/6bd34cdc-fef9-422b-92eb-149378234c39)

  cd -
  make clean
  make RISCV_ISA=rv32imc # Please update the value of the RISCV_ISA attribute depending on the extensions supported by the core.
  find work/rv32imc/ -type f -name "*.elf"
  cd .. # Move back to the Ibex home directory
```
If the test generation was successful, your find command's output should be similar to the one below.

![image](https://github.com/user-attachments/assets/981a3b02-8675-41be-a4c7-eecb9849cac9)

## RISC-V Co-simulation Automation

This section captures an initial version of the script that can be used for the co-simulation automation.

```
# Current directory should be the Ibex home directory

  #!/bin/bash
  
  # Define the directory containing the ELF files
  SEARCH_DIR="<path/to/your/directory>"
  
  # Define the path to the simulation binary
  SIM_BINARY="build/lowrisc_ibex_ibex_simple_system_cosim_0/sim-verilator/Vibex_simple_system"
  
  # Find all .elf files and run the simulator for each
  find "$SEARCH_DIR" -type f -name "*.elf" | while read -r elf_file; do
      echo "Running simulation with ELF file: $elf_file"
      "$SIM_BINARY" --meminit=ram,"$elf_file"
  done
```

## RISC-V Co-simulation Automation Script

This section describes the features and functionality of the script developed to automate the verification of a RISC-V core. You can check out the script [here](https://github.com/pavandheerajkota/EEC283_RISCV_Verification_Automation_Framework/blob/863ed626cecc2e59072556ba1e3926ffd5271886/src/verify_compliance.py).

For the proof of concept, we have used [Ibex core](https://github.com/lowRISC/ibex) as the validation vehicle. We have used the Ibex Simple System-based cosim environment to test our setup.

To generate the ELFs for testing the various instructions supported by each extension, we have used the [RISCV compliance test suite](https://github.com/imphil/riscv-compliance.git).

The image shown below describes the options supported by our script and their required values.

![image](https://github.com/user-attachments/assets/4871862f-3138-4d60-8610-be3a37473064)

To run the automation, please follow the below steps

```
# Current directory should be the Ibex home directory and assumes you have already completed the Co-sim environment setup and RISC-V compliance test generation setup

  git clone https://github.com/pavandheerajkota/EEC283_RISCV_Verification_Automation_Framework.git
  chmod +x ./EEC283_RISCV_Verification_Automation_Framework/src/verify_compliance.py
  ./EEC283_RISCV_Verification_Automation_Framework/src/verify_compliance.py  \
  --sim-binary  <PATH_TO_YOUR_SIMULATION_BINARY>   --compliance <PATH_TO_YOUR_RISCV_COMPLIANCE_BASE_DIR>   --extensions 
  <EXTENSIONS_SUPPORTED_BY_YOUR_CORE>

# Example command for Ibex MaxPerf Configuration:
  ./EEC283_RISCV_Verification_Automation_Framework/src/verify_compliance.py \
  --sim-binary /home/pkota/Documents/riscv_verif_automation_framework/ibex/build/lowrisc_ibex_ibex_simple_system_cosim_0/sim-verilator/Vibex_simple_system \
  --compliance /home/pkota/Documents/riscv_verif_automation_framework/ibex/riscv-compliance \
  --extensions IMC
```
After the automation flow, your output should be similar to the one shown below
![image](https://github.com/user-attachments/assets/6aed9e50-56ef-418d-94fb-fa561923b31d)









