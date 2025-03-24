> 📌 **This repository originated from** [here](https://github.com/IntelligentMOtionlab/SNU_ComputerGraphics).

>🔹 The content is **identical** to the original repository.

# Requirements

This is a baseline code for **SNU Computer Graphics (4190.410)**.
This code uses [Pyglet](https://github.com/pyglet/pyglet) which is a cross-platform windowing library under Python 3.8+. 
Supported platforms are:

* Windows 7 or later
* Mac OS X 10.3 or later
* Linux, with the following libraries (most recent distributions will have these in a default installation):


# Installation

## 0. Installing IDE
If you haven't installed an IDE, download **VSCode** or **PyCharm**

- [Download VSCode](https://code.visualstudio.com/download)
- [Download PyCharm](https://www.jetbrains.com/ko-kr/pycharm/download/?section=windows)



## 1. Installing Conda
If Conda is not installed, download **Miniconda (recommended)** or Anaconda:

- **[Download Miniconda](https://www.anaconda.com/docs/getting-started/miniconda/install)**
- [Download Anaconda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html)

After installation, verify Conda is installed correctly:

    conda --version


## 2. Clone or Download the Repository
### Option 1. Clone via Git

    git clone git@github.com:SNU-IntelligentMotionLab/SNU_ComputerGraphics_.git

### Option 2: Download as ZIP
If you don't have Git, 
1. Click "Code" → "Download ZIP"
2. Extract the ZIP file and open the folder.

## 3. Creating Environmnet
Once inside the project folder, create a Conda environment using `environment.yml`:

    conda env create -f environment.yml

Then, activate the environment:

    conda activate snu_graphics

### ❗ Note:

If you have installed additional packages, be sure to update `environment.yml` manually.

```yaml
# environment.yml
name: snu_graphics
channels:
  # - conda-forge -> you can install pyglet from conda-forge
  - defaults
dependencies:
  - python>=3.8
  - pip
  # Install Pyglet here if you encounter any issues
  # - pyglet
  # You can add more Conda packages here  
  # - numpy==1.23.1
  # - scipy
  - pip:
      - pyglet>=2.1.0
      # - another-pip-package  
```

### 4. Running the Code
You can execute the code easily by:

    python3 main.py

You can then see the result, as shown in the image below.
![Animation](assets/example.gif)
