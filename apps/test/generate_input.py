#!/usr/bin/env python3

"""
This script interactively generates a configuration file unfold_config.ini
to be used as input for the rotational unfolding C++ program.

The configuration includes:
- The base path to the data directory
- A polyhedron category (e.g., platonic, archimedean, prism, etc.)
- The file name of a .adj adjacency data file

After generating the configuration file, it can be passed to the C++ executable as follows:

    ./a.out unfold_config.ini

The C++ program will then prompt for base_face_id and base_edge_id interactively.
"""

import os

# --- Define available categories ---
categories = ["platonic", "archimedean", "prism", "antiprism", "johnson"]

def main():
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
    adj = input("Enter file name (without .adj extension): ").strip()
    if adj not in adj_files:
        print("Error: Invalid file name.")
        exit(1)

    # --- Write to unfold_config.ini ---
    output_filename = "unfold_config.ini"
    with open(output_filename, "w") as f:
        f.write("[polyhedron]\n")
        f.write("base_path = " + base_path + "\n")
        f.write("category  = " + category + "\n")
        f.write("adj       = " + adj + "\n")

    print(f"\nWrote configuration to '{output_filename}'.")

if __name__ == "__main__":
    main()
