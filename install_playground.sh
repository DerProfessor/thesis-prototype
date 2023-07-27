# install frontend
cd interface
yarn install

# install and run backend
cd ../backend
conda --version
# Create a conda environment (to install Diart requirements) with Python 3.8 and activate it
echo "Current shell: $SHELL"
# Detect the shell name from the SHELL environment variable
shell_name="$(basename "$SHELL")"
# Run the appropriate conda init command based on the detected shell
case "$shell_name" in
"bash")
  echo "bash shell detected"
  conda init bash
  ;;
"zsh")
  echo "zsh shell detected"
  conda init zsh
  ;;
"fish")
  echo "fish shell detected"
  conda init fish
  ;;
*) # Handle other or unknown shells
  echo "Unsupported shell: $shell_name"
  echo "Please initialize Conda manually for your shell."
  exit 1
  ;;
esac
# Now, your shell should be properly configured to use 'conda activate'
echo "Your shell has been configured to use 'conda activate'."
conda create -n env python=3.8
# Activate the environment
source ~/anaconda3/etc/profile.d/conda.sh # Fix to conda activate env not working
conda activate env
echo "Conda environment activated"

# Install diart requirements
conda install portaudio pysoundfile ffmpeg -c conda-forge
echo "Diart requirements installed"

# Install packages from 'requirements.txt'
pip install -r requirements.txt
echo "requirements.txt file installed"
