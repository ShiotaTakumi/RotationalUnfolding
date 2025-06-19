#!/usr/bin/env python3

"""
This script interactively generates a configuration file unfold_config.ini
to be used as input for the rotational unfolding C++ program.

The configuration includes:
- The base path to the data directory
- A polyhedron category (e.g., platonic, archimedean, prism, etc.)
- The file name of a .adj adjacency data file
- The output file path for the resulting unfolding data

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

    # --- Prompt for base data path ---
    base_path = input("Enter base path to data directory (e.g., ../../data): ").strip()
    if not os.path.isdir(base_path):
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
    adj_dir = os.path.join(base_path, "polyhedron", category, "adjacent")
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

    # --- Create output path ---
    unfolding_base = os.path.join(out_base, "raw", category)
    os.makedirs(unfolding_base, exist_ok=True)
    output_path = os.path.join(unfolding_base, file + ".ufd")

    # --- Write to unfold_config.ini ---
    config_path = os.path.join(output_dir, "unfold_config.ini")
    with open(config_path, "w") as f:
        f.write("[polyhedron]\n")
        f.write("base_path   = " + base_path + "\n")
        f.write("category    = " + category + "\n")
        f.write("file        = " + file + "\n\n")
        f.write("[output]\n")
        f.write("output_path = " + output_path + "\n")

    print("\nSuccess!")
    print(f"Wrote configuration to unfold_config.ini.")

if __name__ == "__main__":
    main()
