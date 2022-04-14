#!/usr/bin/env bash

pmset noidle &
PMSETPID=$!

mkdir -p ~/EcoAssist_files
cd ~/EcoAssist_files || { echo "Could not change directory to EcoAssist_files. Command could not be run. Please install EcoAssist manually: https://github.com/PetervanLunteren/EcoAssist"; exit 1; }

ECO="EcoAssist"
if [ -d "$ECO" ]; then
  echo "Dir ${ECO} already exists! Skipping this step."
else
  echo "Dir ${ECO} does not exist! Clone repo..."
  git clone https://github.com/PetervanLunteren/EcoAssist.git
fi

CAM="cameratraps"
if [ -d "$CAM" ]; then
  echo "Dir ${CAM} already exists! Skipping this step."
else
  echo "Dir ${CAM} does not exist! Clone repo..."
  git clone https://github.com/Microsoft/cameratraps
  cd cameratraps || { echo "Could not change directory. Command could not be run. Please install EcoAssist manually: https://github.com/PetervanLunteren/EcoAssist"; exit 1; }
  git checkout e40755ec6f3b34e6eefa1306d5cd6ce605e0f5ab
  cd .. || { echo "Could not change directory. Command could not be run. Please install EcoAssist manually: https://github.com/PetervanLunteren/EcoAssist"; exit 1; }
fi

AI4="ai4eutils"
if [ -d "$AI4" ]; then
  echo "Dir ${AI4} already exists! Skipping this step."
else
  echo "Dir ${AI4} does not exist! Clone repo..."
  git clone https://github.com/Microsoft/ai4eutils
  cd ai4eutils || { echo "Could not change directory. Command could not be run. Please install EcoAssist manually: https://github.com/PetervanLunteren/EcoAssist"; exit 1; }
  git checkout c8692a2ed426a189ef3c1b3a5a21ae287c032a1d
  cd .. || { echo "Could not change directory. Command could not be run. Please install EcoAssist manually: https://github.com/PetervanLunteren/EcoAssist"; exit 1; }
fi

MD="md_v4.1.0.pb"
if [ -f "$MD" ]; then
  echo "File ${MD} already exists! Skipping this step."
else
  echo "File ${MD} does not exist! Downloading file..."
  curl --tlsv1.2 --keepalive --output md_v4.1.0.pb https://lilablobssc.blob.core.windows.net/models/camera_traps/megadetector/md_v4.1.0/md_v4.1.0.pb
fi

PATH2CONDA_SH=`conda info | grep 'base environment' | cut -d ':' -f 2 | xargs | cut -d ' ' -f 1`
PATH2CONDA_SH+="/etc/profile.d/conda.sh"
echo "Path to conda.sh: $PATH2CONDA_SH"
# shellcheck source=src/conda.sh
source "$PATH2CONDA_SH"

function fetch_os_type() {
  echo "Checking OS type and version..."
  OSver="unknown"  # default value
  uname_output="$(uname -a)"
  echo "$uname_output"
  # macOS
  if echo "$uname_output" | grep -i darwin >/dev/null 2>&1; then
    # Fetch macOS version
    sw_vers_output="$(sw_vers | grep -e ProductVersion)"
    echo "$sw_vers_output"
    OSver="$(echo "$sw_vers_output" | cut -c 17-)"
    macOSmajor="$(echo "$OSver" | cut -f 1 -d '.')"
    macOSminor="$(echo "$OSver" | cut -f 2 -d '.')"
    # Make sure OSver is supported
    if [[ "${macOSmajor}" = 10 ]] && [[ "${macOSminor}" < "${MACOSSUPPORTED}" ]]; then
      die "Sorry, this version of macOS (10.$macOSminor) is not supported. The minimum version is 10.$MACOSSUPPORTED."
    fi
    # Fix for non-English Unicode systems on MAC
    if [[ -z "${LC_ALL:-}" ]]; then
      export LC_ALL=en_US.UTF-8
    fi

    if [[ -z "${LANG:-}" ]]; then
      export LANG=en_US.UTF-8
    fi
    OS="osx"
  # Linux
  elif echo "$uname_output" | grep -i linux >/dev/null 2>&1; then
    OS="linux"
  else
    die "Sorry, the installer only supports Linux and macOS, quitting installer"
  fi
}

fetch_os_type

conda env remove -n ecoassistcondaenv
conda create -n ecoassistcondaenv python==3.7 -y
conda activate ecoassistcondaenv
pip install --upgrade pip setuptools wheel
pip install --upgrade pip
conda install -c conda-forge requests=2.26.0 -y
pip install -r EcoAssist/requirements.txt

## Check if CPU supports AVX instruction set, and install precompiled TensorFlow if it isn't,
case $OS in
linux*)
  if ! lscpu | grep -q " avx "; then
    echo "AVX is not supported by this CPU! Installing a version of TensorFlow compiled for older CPUs..."
    pip uninstall tensorflow -y
    pip install https://github.com/spinalcordtoolbox/docker-tensorflow-builder/releases/download/v1.15.5-py3.7/tensorflow-1.15.5-cp37-cp37m-linux_x86_64.whl
  else
    echo "AVX is supported on this Linux machine. Keeping default TensorFlow..."
  fi
  ;;
osx)
  if sysctl machdep.cpu.brand_string | grep -q "Apple M1"; then
    echo "AVX is not supported on M1 Macs! Installing a version of TensorFlow compiled for M1 Macs..."
    pip uninstall tensorflow -y
    pip install https://github.com/spinalcordtoolbox/docker-tensorflow-builder/releases/download/v1.15.5-py3.7/tensorflow-1.15.0-py3-none-any.whl
    pip freeze
  else
    echo "AVX is supported on this macOS machine. Keeping default TensorFlow..."
  fi
  ;;
esac

conda deactivate

kill $PMSETPID

echo "

The installation is done! You can close this window now and proceed to open EcoAssist by double clicking the EcoAssist_files/EcoAssist/open_EcoAssist.command file.

"
