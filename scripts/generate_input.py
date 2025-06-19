#!/usr/bin/env python3

"""
This script interactively generates a configuration file path_list.ini
to be used as input for the rotational unfolding C++ program.

The configuration includes:
- Full path to the .adj adjacency data file
- Full path to the .base base face/edge pair file
- Output path for the resulting unfolding data

Usage:
    python3 generate_input.py [output_directory]

If no output_directory is given, the current directory is used.
"""

import os
import sys

# --- Define available categories ---
categories = ["platonic", "archimedean", "prism", "antiprism", "johnson"]

def main():
    # --- Parse output directory ---
    output_dir = sys.argv[1] if len(sys.argv) >= 2 else "."
    if not os.path.isdir(output_dir):
        print(f"Error: Output directory does not exist: {output_dir}")
        exit(1)

    # --- Prompt for data path ---
    data_path = input("Enter path to data directory (e.g., ../../data): ").strip()
    if not os.path.isdir(data_path):
        print("Error: Invalid base path.")
        exit(1)

    # --- Prompt for category selection ---
    print("\nSelect a polyhedron category:")
    print("  " + "  ".join(f"{idx}: {name}" for idx, name in enumerate(categories, start=1)))
    try:
        selection = int(input("Enter category number: "))
        if not (1 <= selection <= len(categories)):
            raise ValueError
    except ValueError:
        print("Error: Invalid category number.")
        exit(1)
    category = categories[selection - 1]

    # --- List available .adj files ---
    adj_dir = os.path.join(data_path, "polyhedron", category, "adjacent")
    if not os.path.isdir(adj_dir):
        print(f"Error: Directory not found: {adj_dir}")
        exit(1)

    adj_files = sorted(f[:-4] for f in os.listdir(adj_dir) if f.endswith(".adj"))
    print(f"\nAvailable .adj files in {adj_dir}:")
    print("  " + "  ".join(adj_files))

    # --- Prompt for file name ---
    file = input("Enter file name (without .adj extension): ").strip()
    if file not in adj_files:
        print("Error: Invalid file name.")
        exit(1)

    # --- Prompt for output base path ---
    out_base = input("Enter path for output directory (e.g., ../../unfolding): ").strip()
    if not out_base:
        print("Error: Output path is empty.")
        exit(1)

    # --- Construct full paths ---
    adj_path = os.path.join(data_path, "polyhedron", category, "adjacent", file + ".adj")
    base_path = os.path.join(data_path, "polyhedron", category, "base", file + ".base")
    unfolding_base = os.path.join(out_base, "raw", category)
    os.makedirs(unfolding_base, exist_ok=True)
    raw_path = os.path.join(unfolding_base, file + ".ufd")

    # --- Write to path_list.ini ---
    config_path = os.path.join(output_dir, "path_list.ini")
    with open(config_path, "w") as f:
        f.write("[paths]\n")
        f.write("adj_path  = " + adj_path + "\n")
        f.write("base_path = " + base_path + "\n")
        f.write("raw_path  = " + raw_path + "\n")

    print("\nSuccess!")
    print(f"Wrote configuration to {config_path}")

if __name__ == "__main__":
    main()
