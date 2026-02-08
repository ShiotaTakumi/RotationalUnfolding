# Rotational Unfolding

[![MIT](https://img.shields.io/badge/license-MIT-9e1836.svg?logo=&style=plastic)](LICENSE)
<img src="https://img.shields.io/badge/purpose-research-8A2BE2.svg?logo=&style=plastic">
<img src="https://img.shields.io/github/v/release/ShiotaTakumi/RotationalUnfolding?include_prereleases&style=plastic">
<img src="https://img.shields.io/github/last-commit/ShiotaTakumi/RotationalUnfolding?style=plastic">
<img src="https://img.shields.io/badge/MacOS-15.5-000000.svg?logo=macOS&style=plastic">
<img src="https://img.shields.io/badge/Shell-bash-FFD500.svg?logo=shell&style=plastic">
<img src="https://img.shields.io/badge/C++-GCC%2014.2.0-00599C.svg?logo=cplusplus&style=plastic">
<img src="https://img.shields.io/badge/Python-3.12.0-3776AB.svg?logo=python&style=plastic">

## Overview / 概要

This program determines whether a given convex regular-faced polyhedron admits an overlapping edge unfolding, using a rotational unfolding algorithm.

与えられた凸正面多面体が重なりのある辺展開を持つかどうかを、回転展開アルゴリズムによって判定するプログラムです。

## Algorithm Details / アルゴリズムの詳細

Please refer to the following paper for details:

詳細は以下の論文を参照してください：

Takumi Shiota and Toshiki Saitoh, "Overlapping edge unfoldings for convex regular-faced polyhedra", Theoretical Computer Science, Vol. 1002: 114593, June 2024.

[![DOI®](https://img.shields.io/badge/DOI%C2%AE-10.1016/j.tcs.2024.114593-FAB70C.svg?logo=doi&style=plastic)](https://doi.org/10.1016/j.tcs.2024.114593)

## Pipeline / パイプライン

The processing pipeline consists of the following four phases:

処理パイプラインは以下の 4 フェーズで構成されています：

| Phase | Module | Description / 説明 |
|-------|--------|-------------------|
| Phase 1 | `rotational_unfolding` | Raw enumeration of all partial unfoldings / 全部分展開の列挙 |
| Phase 2 | `nonisomorphic` | Removal of isomorphic duplicates / 同型な重複の除去 |
| Phase 3 | `exact` | Exact overlap detection using SymPy / SymPy による厳密重なり判定 |
| Drawing | `drawing` | SVG visualization of results / 結果の SVG 可視化 |

## Prerequisites / 前提条件

- Python 3.8+
- GCC 14+ (C++17)
- SymPy (`pip install sympy`) — Phase 3 で使用 / used by Phase 3

## Quick Start / クイックスタート

```bash
# Set up the virtual environment / 仮想環境のセットアップ
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Build the C++ core / C++ コアのビルド
cd cpp && make && cd ..

# Run the full pipeline / パイプラインの一括実行
PYTHONPATH=python python -m run_all --poly data/polyhedra/archimedean/s12L

# Run the full pipeline without labels / ラベルなしで一括実行
PYTHONPATH=python python -m run_all --poly data/polyhedra/archimedean/s12L --no-labels
```

### Running Individual Phases / 個別フェーズの実行

```bash
# Phase 1: Raw enumeration / 全列挙
PYTHONPATH=python python -m rotational_unfolding run --poly data/polyhedra/archimedean/s12L

# Phase 2: Nonisomorphic filtering / 同型除去
PYTHONPATH=python python -m nonisomorphic run --poly data/polyhedra/archimedean/s12L

# Phase 3: Exact overlap detection / 厳密重なり判定
PYTHONPATH=python python -m exact run --poly data/polyhedra/archimedean/s12L

# Drawing: SVG generation / SVG 描画
PYTHONPATH=python python -m drawing run --type exact --poly data/polyhedra/archimedean/s12L
PYTHONPATH=python python -m drawing run --type exact --poly data/polyhedra/archimedean/s12L --no-labels
```

## Directory Structure / ディレクトリ構成

```
RotationalUnfolding/
├── cpp/                  # C++ core (rotunfold binary) / C++ コア
├── data/                 # Polyhedron input data (JSON) / 多面体入力データ
│   └── polyhedra/
│       ├── antiprism/    # Antiprisms / 反角柱
│       ├── archimedean/  # Archimedean solids / アルキメデスの立体
│       ├── johnson/      # Johnson solids / ジョンソンの立体
│       ├── platonic/     # Platonic solids / 正多面体
│       └── prism/        # Prisms / 角柱
├── docs/                 # Design documents / 設計書
├── output/               # Pipeline outputs (JSONL, SVG) / パイプライン出力
│   └── polyhedra/
│       └── <class>/<name>/
│           ├── raw.jsonl
│           ├── noniso.jsonl
│           ├── exact.jsonl
│           ├── run.json
│           └── draw/
│               └── exact/
├── python/               # Python CLI modules / Python CLI モジュール
│   ├── rotational_unfolding/   # Phase 1
│   ├── nonisomorphic/          # Phase 2
│   ├── exact/                  # Phase 3
│   ├── drawing/                # Drawing utility
│   └── run_all/                # Pipeline orchestrator / 一括実行
├── tools/                # Data conversion utilities / データ変換ツール
├── requirements.txt      # Python dependencies / Python 依存パッケージ
└── LICENSE
```

## Acknowledgements / 謝辞

This work was supported in part by JSPS KAKENHI Grant Numbers JP18H04091, JP19K12098, JP21H05857, JP24KJ1816 and JP25K24391.

本研究は JSPS 科研費 JP18H04091, JP19K12098, JP21H05857, JP24KJ1816, JP25K24391 の助成を受けたものです。
