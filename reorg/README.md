# Reorganized Layout (Work in Progress)

This directory contains the reorganized implementation of the rotational unfolding pipeline. While marked as "Work in Progress," **all processing phases and the visualization utility are fully implemented and operational.** This is the canonical entry point for running experiments.

このディレクトリは回転展開パイプラインの再構成された実装を含みます。"Work in Progress" と表記されていますが、**すべての処理フェーズと可視化ユーティリティは完全に実装済みであり、動作可能です。** 実験を実行するための正規エントリポイントです。

---

## Pipeline Overview / パイプライン概要

The pipeline consists of four independent stages executed in sequence:

パイプラインは順に実行される 4 つの独立した段階で構成されます：

| Stage | Module | Input | Output |
|-------|--------|-------|--------|
| Phase 1 | `rotational_unfolding` | `polyhedron.json`, `root_pairs.json` | `raw.jsonl`, `run.json` |
| Phase 2 | `nonisomorphic` | `raw.jsonl` | `noniso.jsonl` |
| Phase 3 | `exact` | `noniso.jsonl` | `exact.jsonl` |
| Drawing | `drawing` | `raw.jsonl` / `noniso.jsonl` / `exact.jsonl` | `draw/<type>/*.svg` |

- **Phase 1**: Enumerates all rotational unfoldings via the C++ core. C++ コアにより全回転展開を列挙する。
- **Phase 2**: Removes geometrically equivalent (isomorphic) unfoldings. 幾何学的に等価な（同型な）展開図を除去する。
- **Phase 3**: Performs exact overlap verification using SymPy symbolic computation. SymPy シンボリック計算による厳密重なり検証を行う。
- **Drawing**: Generates SVG visualizations for verification. 検証用の SVG 可視化を生成する。

Each stage reads its input as read-only and produces its own output. Downstream outputs are strict subsets of upstream outputs.

各段階は入力を読み取り専用で扱い、独自の出力を生成します。下流出力は上流出力の厳密な部分集合です。

---

## Quick Start / クイックスタート

### Full Pipeline (One Command) / 一括実行（1 コマンド）

Run the entire pipeline for a single polyhedron:

1 つの多面体に対してパイプライン全体を実行する：

```bash
PYTHONPATH=reorg/python python -m run_all --poly polyhedra/archimedean/s07
```

This executes Phase 1 → Phase 2 → Phase 3 → Drawing (exact) in order. If any step fails, execution stops immediately.

Phase 1 → Phase 2 → Phase 3 → Drawing (exact) を順に実行します。いずれかのステップが失敗した場合、実行は即座に停止します。

### Individual Phase Execution / 個別実行

Each phase can also be run independently:

各フェーズは個別に実行できます：

**Phase 1 — Rotational Unfolding / 回転展開:**

```bash
PYTHONPATH=reorg/python python -m rotational_unfolding run --poly polyhedra/<class>/<name>
```

**Phase 2 — Nonisomorphic Filtering / 非同型フィルタリング:**

```bash
PYTHONPATH=reorg/python python -m nonisomorphic run --poly polyhedra/<class>/<name>
```

**Phase 3 — Exact Overlap Detection / 厳密重なり判定:**

```bash
PYTHONPATH=reorg/python python -m exact run --poly polyhedra/<class>/<name>
```

**Drawing — SVG Visualization / SVG 可視化:**

```bash
PYTHONPATH=reorg/python python -m drawing run --type raw|noniso|exact --poly polyhedra/<class>/<name>
```

### Examples / 実行例

```bash
# Full pipeline for Archimedean solid s07
PYTHONPATH=reorg/python python -m run_all --poly polyhedra/archimedean/s07

# Full pipeline for Johnson solid n20
PYTHONPATH=reorg/python python -m run_all --poly polyhedra/johnson/n20

# Phase 3 only (requires existing noniso.jsonl)
PYTHONPATH=reorg/python python -m exact run --poly polyhedra/johnson/n66

# Draw raw unfoldings
PYTHONPATH=reorg/python python -m drawing run --type raw --poly polyhedra/archimedean/s07

# Draw exact-verified unfoldings (no labels, shape only)
PYTHONPATH=reorg/python python -m drawing run --type exact --poly polyhedra/johnson/n20
```

All commands are `cwd`-independent. Run from the repository root.

すべてのコマンドは `cwd` 非依存です。リポジトリルートから実行してください。

---

## Directory Structure / ディレクトリ構成

```
reorg/
├── README.md                          # This file / 本ファイル
├── cpp/                               # C++ core (Phase 1 binary)
│   ├── include/                       #   Header files
│   ├── src/                           #   Source files
│   ├── rotunfold                      #   Compiled binary
│   ├── CMakeLists.txt
│   └── Makefile
├── data/                              # Input data (polyhedron definitions)
│   └── polyhedra/
│       ├── archimedean/               #   e.g., s01, s04, s07, ...
│       ├── johnson/                   #   e.g., n20, n21, n66, ...
│       ├── platonic/
│       ├── prism/
│       └── antiprism/
├── python/                            # Python modules
│   ├── rotational_unfolding/          #   Phase 1: enumeration CLI
│   ├── nonisomorphic/                 #   Phase 2: deduplication CLI
│   ├── exact/                         #   Phase 3: exact overlap CLI
│   ├── drawing/                       #   Drawing: SVG visualization
│   └── run_all/                       #   Full pipeline orchestrator
├── output/                            # Computation outputs (generated)
│   └── polyhedra/
│       └── <class>/<name>/
│           ├── raw.jsonl              #     Phase 1 output
│           ├── run.json               #     Phase 1 metadata
│           ├── noniso.jsonl           #     Phase 2 output
│           ├── exact.jsonl            #     Phase 3 output
│           └── draw/                  #     Drawing output (verification only)
│               ├── raw/               #       SVGs from raw.jsonl
│               ├── noniso/            #       SVGs from noniso.jsonl
│               └── exact/             #       SVGs from exact.jsonl
├── docs/                              # Phase documentation
│   ├── PHASE1_RUN.md
│   ├── PHASE2_NONISO.md
│   ├── PHASE3_EXACT.md
│   ├── DRAWING_UTILITY.md
│   └── RUN_ALL.md
└── tools/                             # Data conversion utilities
    ├── convert_legacy_input.py
    └── batch_convert_all.sh
```

---

## Output Directory / 出力ディレクトリ

`reorg/output/` contains all computation outputs. These files are **generated artifacts** and are overwritten on each run.

`reorg/output/` はすべての計算成果物を含みます。これらは**生成された成果物**であり、実行のたびに上書きされます。

- `raw.jsonl` — Complete enumeration (Phase 1) / 完全列挙（Phase 1）
- `run.json` — Execution metadata (Phase 1) / 実行メタデータ（Phase 1）
- `noniso.jsonl` — Deduplicated records (Phase 2) / 重複除去済みレコード（Phase 2）
- `exact.jsonl` — Overlap-verified records with classification (Phase 3) / 重なり検証済みレコード・分類付き（Phase 3）

**`draw/` subdirectories are verification-only outputs.** SVG files under `draw/` are for visual confirmation and are not research artifacts. They are `.gitignore` targets.

**`draw/` サブディレクトリは検証専用の出力です。** `draw/` 配下の SVG ファイルは目視確認用であり、研究成果物ではありません。`.gitignore` の対象です。

---

## Prerequisites / 前提条件

- Python 3.8+
- SymPy (`pip install sympy`) — required by Phase 3
- C++ compiler (GCC, C++17) — required to build the Phase 1 binary
- The C++ binary must be pre-compiled at `reorg/cpp/rotunfold`

---

## Design Principles / 設計方針

- **Architectural separation**: Each phase is an independent Python module. No phase imports another. `run_all` orchestrates via `subprocess` only.
- **Read-only inputs**: Each phase treats its input as read-only and never modifies upstream outputs.
- **Filter-only downstream**: Phase 2 and Phase 3 are pure filters — they remove records but never modify record content.
- **Overwrite policy**: All outputs are overwritten on each run. There are no timestamped directories or experiment IDs in the output path.
- **Legacy preservation**: The legacy implementation outside `reorg/` is preserved and unmodified.

- **アーキテクチャ的分離**: 各フェーズは独立した Python モジュール。フェーズ間の import はない。`run_all` は `subprocess` のみで統合する。
- **入力は読み取り専用**: 各フェーズは入力を読み取り専用として扱い、上流出力を変更しない。
- **下流はフィルターのみ**: Phase 2 と Phase 3 は純粋なフィルター — レコードを除去するが、内容は変更しない。
- **上書きポリシー**: すべての出力は実行のたびに上書きされる。出力パスにタイムスタンプやエクスペリメント ID は含まれない。
- **Legacy の保持**: `reorg/` 外の legacy 実装は保持されており、変更されていない。
