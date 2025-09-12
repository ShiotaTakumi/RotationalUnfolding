# Apps
C++ main file and Python wrapper scripts for running the rotational unfolding algorithm and related processes.
This directory serves as the main entry point of the project.

## Execution Steps
Follow these steps to run the rotational unfolding algorithm and related processes.

1. Setup root paths (only once)

    Run the following command to configure the root directories for polyhedron data, unfolding outputs, and drawings:
    ```bash
    ./run_setup_root_paths.py
    ```

2. Generate a path list for the target polyhedron (run this whenever you change the target polyhedron)

    ```bash
    ./run_generate_path_lists.py
    ```

3. Compile the main program (`main.cpp`)

    ```bash
    make
    ```

4. Run the rotational unfolding by specifying the target polyhedron (.ini file)

    ```bash
    ./a.out config/path_lists.ini
    ```

5. Remove isomorphic partial unfoldings

    ```bash
    ./run_isomorphic_remover.py config/path_lists.ini
    ```

6. Check exact overlaps using symbolic computation (**currently under development**)


### Optional
- Visualize partial unfoldings as SVG files:
    ```bash
    ./run_draw_partial_unfolding.py config/path_lists.ini
    ```
