#!/usr/bin/env python3

"""
This script calls scripts/generate_input.py to generate an unfold_config.ini
file in the current working directory.

Usage:
    python3 make_ini.py

After generating the configuration file, it can be passed to the C++ executable as follows:

    ./a.out unfold_config.ini

The C++ program will then prompt for base_face_id and base_edge_id interactively.
"""

import subprocess
import os
import sys

def main():
    # Relative path to scripts/generate_input.py
    script_path = os.path.join(os.path.dirname(__file__), "../../scripts/generate_input.py")
    # Get current working directory
    output_dir = os.getcwd()

    if not os.path.isfile(script_path):
        print("Error: scripts/generate_input.py not found.")
        sys.exit(1)

    try:
        subprocess.run(["python3", script_path, output_dir], check=True)
    except subprocess.CalledProcessError as e:
        print("Error: Failed to execute generate_input.py.")
        sys.exit(e.returncode)

if __name__ == "__main__":
    main()
