# Rotational Unfolding — Python Modules

## Overview

This directory contains the Python modules for the rotational unfolding pipeline.
Each module is an independent CLI that can be invoked via `python -m <module>`.

このディレクトリは回転展開パイプラインの Python モジュールを含みます。
各モジュールは `python -m <module>` で呼び出せる独立した CLI です。

## Modules

| Module | Phase | Description |
|--------|-------|-------------|
| `rotational_unfolding` | Phase 1 | C++ core invocation, raw.jsonl + run.json generation |
| `nonisomorphic` | Phase 2 | Isomorphic duplicate removal |
| `exact` | Phase 3 | Exact overlap detection (SymPy) |
| `drawing` | — | SVG visualization (verification utility) |
| `run_all` | — | Full pipeline orchestrator |

## Usage

All commands require `PYTHONPATH=reorg/python` and are run from the repository root.

すべてのコマンドは `PYTHONPATH=reorg/python` を必要とし、リポジトリルートから実行します。

The `--poly` argument takes a path to a polyhedron data directory (e.g., `polyhedra/archimedean/s07`).
This path supports shell Tab completion.

`--poly` 引数は多面体データディレクトリへのパスを取ります（例: `polyhedra/archimedean/s07`）。
このパスはシェルの Tab 補完に対応しています。

### Full Pipeline (One Command)

```bash
PYTHONPATH=reorg/python python -m run_all --poly polyhedra/archimedean/s07
```

### Individual Phase Execution

```bash
# Phase 1: Rotational unfolding
PYTHONPATH=reorg/python python -m rotational_unfolding run --poly polyhedra/archimedean/s07

# Phase 2: Nonisomorphic filtering
PYTHONPATH=reorg/python python -m nonisomorphic run --poly polyhedra/archimedean/s07

# Phase 3: Exact overlap detection
PYTHONPATH=reorg/python python -m exact run --poly polyhedra/archimedean/s07

# Drawing (raw / noniso / exact)
PYTHONPATH=reorg/python python -m drawing run --type raw --poly polyhedra/archimedean/s07
PYTHONPATH=reorg/python python -m drawing run --type exact --poly polyhedra/johnson/n66

# Drawing without labels (polygons only)
PYTHONPATH=reorg/python python -m drawing run --type exact --poly polyhedra/johnson/n66 --no-labels
```

## Output

All outputs are written to `reorg/output/polyhedra/<class>/<name>/`:

```
reorg/output/polyhedra/<class>/<name>/
├── raw.jsonl       # Phase 1
├── run.json        # Phase 1 metadata
├── noniso.jsonl    # Phase 2
├── exact.jsonl     # Phase 3
└── draw/           # Drawing (verification only, .gitignore target)
    ├── raw/
    ├── noniso/
    └── exact/
```

## Requirements

- Python 3.8+
- SymPy (`pip install sympy`) — required by Phase 3
- C++ binary (`reorg/cpp/rotunfold`) must be built — required by Phase 1
- Polyhedron data in `reorg/data/polyhedra/`
