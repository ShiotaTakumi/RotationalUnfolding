# Rotational Unfolding

[![MIT](https://img.shields.io/badge/license-MIT-9e1836.svg?logo=&style=plastic)](LICENSE)
<img src="https://img.shields.io/badge/purpose-research-8A2BE2.svg?logo=&style=plastic">
<img src="https://img.shields.io/github/v/release/ShiotaTakumi/RotationalUnfolding?include_prereleases&style=plastic">
<img src="https://img.shields.io/github/last-commit/ShiotaTakumi/RotationalUnfolding?style=plastic">
<img src="https://img.shields.io/badge/MacOS-15.5-000000.svg?logo=macOS&style=plastic">
<img src="https://img.shields.io/badge/Shell-bash-FFD500.svg?logo=shell&style=plastic">
<img src="https://img.shields.io/badge/C++-GCC%2014.2.0-00599C.svg?logo=cplusplus&style=plastic">
<img src="https://img.shields.io/badge/Python-3.12.0-3776AB.svg?logo=python&style=plastic">


## Overview
This program checks whether a given polyhedron, in which all edge lengths are equal, has an overlapping unfolding.

## Algorithm Details
Please refer to the following paper for details:

Takumi Shiota and Toshiki Saitoh, "Overlapping edge unfoldings for convex regular-faced polyhedra", Theoretical Computer Science, Vol. 1002: 114593, June 2024.

[![DOI®](https://img.shields.io/badge/DOI%C2%AE-10.1016/j.tcs.2024.114593-FAB70C.svg?logo=doi&style=plastic)](https://doi.org/10.1016/j.tcs.2024.114593)

## Environment Setup
This project uses Python 3.12.0.
If you want to match the environment, please set up the virtual environment using the following steps:
```bash
# Install Python 3.12.0 with pyenv
pyenv install 3.12.0
pyenv local 3.12.0

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```
## Contents
- [apps/](apps/): Wrapper scripts providing example entry points for running the program
- [drawing/](drawing/): Output directory for SVG drawings of partial unfoldings
- [include/rotational_unfolding/](include/rotational_unfolding/): Core program implementing the rotational unfolding algorithm
- [polyhedron/](polyhedron/): Directory containing polyhedron adjacency and base face data
- [scripts/](scripts/): Core scripts for various processing tasks
- [unfolding/](unfolding/): Directory storing unfolding results
- [.gitignore](.gitignore): Specifies intentionally untracked files to ignore by Git
- [LICENSE](LICENSE): License information for this repository
- [README.md](README.md): This file
- [requirements.txt](requirements.txt): Python dependencies required for running the project

## Acknowledgements
This work was supported in part by JSPS KAKENHI Grant Numbers JP18H04091, JP19K12098, and JP21H05857.
