# Phase 1: Run — Rotational Unfolding Execution

**Status**: Implemented (Specification Frozen)
**Version**: 1.0.0
**Last Updated**: 2026-02-07

---

## Overview / 概要

Phase 1 implements the foundational execution layer for the rotational unfolding algorithm. It provides a command-line interface (CLI) for running the C++ core and generates machine-readable output in JSONL format.

Phase 1 は回転展開アルゴリズムの基盤実行層を実装します。C++ コアを実行するためのコマンドラインインターフェース（CLI）を提供し、JSONL 形式で機械可読な出力を生成します。

**This is the foundation phase.** Phase 1 establishes the stable input/output contract and execution model for all subsequent processing stages (nonisomorphic filtering, exact overlap detection, drawing), but does not implement those stages itself. The specification defined in this document is frozen and serves as the basis for Phase 2 and beyond.

**これは基盤確立フェーズです。** Phase 1 は、後続のすべての処理段階（同型除去、厳密重なり判定、描画）のための安定した入出力契約と実行モデルを確立しますが、それらの段階自体は実装しません。本文書で定義される仕様は凍結されており、Phase 2 以降の基礎として機能します。

---

## Purpose and Scope / 目的と範囲

### What Phase 1 Does / Phase 1 が行うこと

Phase 1 focuses on **reproducible execution** of the rotational unfolding algorithm and defines the canonical data contract for downstream processing:

1. **Unified entry point**: `python -m rotational_unfolding run` serves as the canonical way to run experiments.
2. **Input standardization**: Polyhedron data is stored in JSON format (`polyhedron.json`, `root_pairs.json`) as the normative input format.
3. **Output standardization**: Raw partial unfoldings are emitted as JSONL (`raw.jsonl`) with deterministic rounding and normalization.
4. **Experiment metadata**: Each run generates `run.json` containing all information needed to reproduce the experiment.
5. **cwd-independence**: The CLI resolves paths relative to the repository root, not the current working directory.
6. **Deterministic output paths**: Output is written to `output/polyhedra/<class>/<name>/` regardless of execution context.

Phase 1 は回転展開アルゴリズムの**再現可能な実行**に焦点を当て、下流処理のための正規のデータ契約を定義します：

1. **統一された入口**: `python -m rotational_unfolding run` が実験を実行する正規の方法として機能します。
2. **入力の標準化**: 多面体データは正規の入力形式として JSON 形式（`polyhedron.json`, `root_pairs.json`）で保存されます。
3. **出力の標準化**: 生の部分展開図は、決定的な丸めと正規化を伴う JSONL（`raw.jsonl`）として出力されます。
4. **実験メタデータ**: 各実行は、実験を再現するために必要なすべての情報を含む `run.json` を生成します。
5. **cwd 非依存**: CLI はリポジトリルートを基準にパスを解決し、現在の作業ディレクトリには依存しません。
6. **決定的な出力パス**: 出力は実行コンテキストに関わらず `output/polyhedra/<class>/<name>/` に書き込まれます。

### What Phase 1 Does NOT Do / Phase 1 が行わないこと

Phase 1 intentionally **does not** implement:

- **Nonisomorphic filtering**: All candidate unfoldings are output, including isomorphic duplicates.
- **Exact overlap detection**: Overlap is detected approximately (circumradius proximity) by the C++ core.
- **Drawing/visualization**: No SVG or graphical output is generated.
- **Post-processing pipeline**: No automated workflow for filtering or analysis.
- **Batch processing**: Each polyhedron must be run separately.

Phase 1 は意図的に以下を**実装しません**：

- **同型除去**: すべての候補展開図（同型な重複を含む）が出力されます。
- **厳密重なり判定**: 重なりは C++ コアによって近似的（外接円の近接性）に検出されます。
- **描画・可視化**: SVG やグラフィカルな出力は生成されません。
- **後処理パイプライン**: フィルタリングや解析の自動化されたワークフローはありません。
- **バッチ処理**: 各多面体は個別に実行する必要があります。

---

## Architecture / アーキテクチャ

Phase 1 uses a two-layer architecture:

Phase 1 は2層アーキテクチャを使用します：

```
┌─────────────────────────────────────────┐
│  Python CLI (rotational_unfolding)      │
│  - Argument parsing                     │
│  - Path resolution                      │
│  - Experiment directory management      │
│  - run.json generation                  │
└─────────────┬───────────────────────────┘
              │ subprocess
              ↓
┌─────────────────────────────────────────┐
│  C++ Core (rotunfold)                   │
│  - Rotational unfolding algorithm       │
│  - Overlap detection (approximate)      │
│  - JSONL output (raw.jsonl)             │
└─────────────────────────────────────────┘
```

### Responsibility Separation / 責務分離

| Component | Responsibility |
|-----------|----------------|
| **Python CLI** | Orchestration, metadata, reproducibility |
| **C++ Core** | Algorithm execution, numeric computation |

| コンポーネント | 責務 |
|-----------|----------------|
| **Python CLI** | オーケストレーション、メタデータ、再現性 |
| **C++ コア** | アルゴリズム実行、数値計算 |

The C++ core is treated as a **compute engine** that reads JSON input and writes JSONL output. It does not know about experiment IDs, directory structure, or metadata.

C++ コアは JSON 入力を読み込み JSONL 出力を書き込む**計算エンジン**として扱われます。実験 ID、ディレクトリ構造、メタデータについては関知しません。

---

## Input Format / 入力形式

Phase 1 defines JSON-based input as the **normative input format** for the rotational unfolding algorithm. Input files are stored in `data/polyhedra/`:

Phase 1 は JSON ベースの入力を回転展開アルゴリズムの**正規入力形式**として定義します。入力ファイルは `data/polyhedra/` に保存されます：

```
data/polyhedra/
└── <class>/
    └── <name>/
        ├── polyhedron.json
        └── root_pairs.json
```

### polyhedron.json

Defines the combinatorial structure of a polyhedron:

- `schema_version`: Format version (currently 1)
- `polyhedron.class` / `polyhedron.name`: Identifier
- `faces[]`: Array of faces with adjacency information

多面体の組合せ構造を定義：

- `schema_version`: フォーマットバージョン（現在 1）
- `polyhedron.class` / `polyhedron.name`: 識別子
- `faces[]`: 隣接情報を含む面の配列

### root_pairs.json

Specifies the starting configurations for unfolding search:

- `schema_version`: Format version (currently 1)
- `root_pairs[]`: Array of `{base_face, base_edge}` pairs

展開探索の開始構成を指定：

- `schema_version`: フォーマットバージョン（現在 1）
- `root_pairs[]`: `{base_face, base_edge}` ペアの配列

---

## Output Format / 出力形式

**Phase 1 Contract**: Each execution produces exactly two files as the canonical output:

- `raw.jsonl`: Complete enumeration of candidate partial unfoldings (generated by C++ core)
- `run.json`: Experiment metadata for reproducibility (generated by Python CLI)

These files are written to a deterministic location based on the polyhedron identifier:

**Phase 1 の契約**: 各実行は正規の出力として正確に2つのファイルを生成します：

- `raw.jsonl`: 候補部分展開図の完全列挙（C++ コアによって生成）
- `run.json`: 再現性のための実験メタデータ（Python CLI によって生成）

これらのファイルは多面体識別子に基づく決定的な場所に書き込まれます：

```
output/polyhedra/<class>/<name>/
├── raw.jsonl
└── run.json
```

Output paths are **cwd-independent** and **overwrite-on-rerun**: running the same polyhedron again replaces the previous output.

出力パスは **cwd 非依存**であり、**再実行時に上書き**されます：同じ多面体を再度実行すると前の出力を置き換えます。

### raw.jsonl

**Generated by**: C++ core
**Format**: JSON Lines (one record per line)
**Purpose**: Raw partial unfoldings found by the algorithm

**生成元**: C++ コア
**形式**: JSON Lines（1行1レコード）
**目的**: アルゴリズムが見つけた生の部分展開図

Each record represents a candidate partial unfolding:

```json
{
  "schema_version": 1,
  "record_type": "partial_unfolding",
  "base_pair": {"base_face": 0, "base_edge": 0},
  "symmetric_used": true,
  "faces": [
    {"face_id": 0, "gon": 8, "edge_id": 0, "x": 0.0, "y": 0.0, "angle_deg": 0.0},
    ...
  ]
}
```

**Key properties in Phase 1:**

- All coordinates are rounded to 6 decimal places (half away from zero)
- Angles are normalized to [-180, 180] degrees
- Isomorphic duplicates are NOT removed (Phase 1 guarantees enumeration, not uniqueness)
- Exact overlap status is NOT verified (Phase 1 uses approximate detection)
- Each record is self-contained and includes `base_pair` and `symmetric_used` for traceability

**Phase 1 における主要な特性：**

- すべての座標は小数点以下6桁に丸められる（0から遠ざかる方向）
- 角度は [-180, 180] 度に正規化される
- 同型な重複は除去されない（Phase 1 は列挙を保証し、一意性は保証しない）
- 厳密な重なりの状態は検証されない（Phase 1 は近似検出を使用）
- 各レコードは自己完結しており、トレーサビリティのため `base_pair` と `symmetric_used` を含む

### run.json

**Generated by**: Python CLI
**Format**: JSON (pretty-printed)
**Purpose**: Experiment metadata for reproducibility

**生成元**: Python CLI
**形式**: JSON（整形済み）
**目的**: 再現性のための実験メタデータ

Contains all information needed to reproduce the experiment:

- Run identification (`run_id`, timestamps, exit code)
- Command invocation (`executable_path`, `argv`, `cwd`)
- Input file paths and metadata (absolute paths for unambiguous identification)
- Options (`symmetric` mode and resolution basis for `auto` mode)
- Output summary (`num_records_written`)

**Reproducibility contract**: `run.json` provides the minimal evidence trail to verify that a `raw.jsonl` was produced under specific input conditions. Absolute paths are intentionally included to eliminate ambiguity on the machine where the run was executed.

実験を再現するために必要なすべての情報を含む：

- 実行の識別（`run_id`、タイムスタンプ、終了コード）
- コマンド呼び出し（`executable_path`, `argv`, `cwd`）
- 入力ファイルのパスとメタデータ（曖昧さのない識別のための絶対パス）
- オプション（`symmetric` モードと `auto` モードの解決根拠）
- 出力サマリー（`num_records_written`）

**再現性の契約**: `run.json` は、特定の入力条件下で `raw.jsonl` が生成されたことを検証するための最小限の証跡を提供します。実行されたマシン上での曖昧性を排除するため、絶対パスが意図的に含まれています。

---

## Usage / 使用方法

### Basic Execution

```bash
# From repository root (PYTHONPATH must be set)
cd /path/to/RotationalUnfolding
PYTHONPATH=python python -m rotational_unfolding run --poly data/polyhedra/archimedean/s05
```

### Arguments

- `--poly data/polyhedra/CLASS/NAME`: Path to polyhedron data directory (e.g., `data/polyhedra/archimedean/s05`) **[required]**
- `--symmetric auto|on|off`: Symmetry pruning mode (default: `auto`)

### Output Directory Structure

```
output/polyhedra/
├── archimedean/
│   ├── s01/
│   │   ├── raw.jsonl
│   │   └── run.json
│   ├── s05/
│   │   ├── raw.jsonl
│   │   └── run.json
│   └── ...
└── platonic/
    ├── r01/
    │   ├── raw.jsonl
    │   └── run.json
    └── ...
```

**Output path convention**: `output/polyhedra/<class>/<name>/`

This path is deterministic, cwd-independent, and overwritten on re-execution.

**出力パス規約**: `output/polyhedra/<class>/<name>/`

このパスは決定的で、cwd 非依存であり、再実行時に上書きされます。

---

## Design Decisions / 設計判断

### Why JSONL for raw output?

- Streaming-friendly: Records can be processed one at a time
- Append-safe: New records can be added without rewriting the file
- Language-agnostic: Easy to parse in any language

### なぜ raw 出力に JSONL を使うのか？

- ストリーミング対応: レコードを1つずつ処理可能
- 追記安全: ファイルを書き直さずに新しいレコードを追加可能
- 言語非依存: あらゆる言語で解析が容易

### Why separate run.json?

- Metadata should not pollute the data stream
- Reproducibility information is independent of algorithmic results
- Phase 2+ can read `run.json` to understand provenance without parsing `raw.jsonl`
- `run_id` serves as metadata only (not used for directory naming)

### なぜ run.json を分離するのか？

- メタデータはデータストリームを汚染すべきでない
- 再現性情報はアルゴリズム結果から独立している
- Phase 2 以降は `raw.jsonl` を解析せずに `run.json` を読んで出所を理解できる
- `run_id` はメタデータとしてのみ機能する（ディレクトリ命名には使用されない）

### Why Python CLI instead of pure C++?

- Path resolution and directory management are easier in Python
- Experiment metadata generation requires file inspection
- Future post-processing will be in Python (noniso, draw, exact)

### なぜ純粋な C++ ではなく Python CLI なのか？

- パス解決とディレクトリ管理は Python で簡単
- 実験メタデータ生成にはファイル検査が必要
- 将来の後処理は Python で行われる予定（noniso, draw, exact）

---

## Limitations and Known Issues / 制限と既知の問題

### Phase 1 Guarantees

Phase 1 provides the following guarantees:

1. **Deterministic output paths**: Same polyhedron always writes to the same location.
2. **Complete enumeration**: All candidate unfoldings found by the algorithm are recorded in `raw.jsonl`.
3. **Traceable provenance**: `run.json` contains sufficient information to verify input conditions.
4. **Numeric consistency**: Floating-point values are rounded deterministically (6 decimal places, half away from zero).

### Phase 1 の保証

Phase 1 は以下を保証します：

1. **決定的な出力パス**: 同じ多面体は常に同じ場所に書き込まれます。
2. **完全な列挙**: アルゴリズムが見つけたすべての候補展開図が `raw.jsonl` に記録されます。
3. **追跡可能な出所**: `run.json` は入力条件を検証するのに十分な情報を含みます。
4. **数値の一貫性**: 浮動小数点値は決定的に丸められます（小数点以下6桁、0から遠ざかる方向）。

### Phase 1 Does NOT Guarantee

1. **No deduplication**: Isomorphic unfoldings appear multiple times in `raw.jsonl`.
2. **Approximate overlap only**: The C++ core uses circumradius proximity, not exact polygon intersection.
3. **Single polyhedron per invocation**: Batch processing requires scripting or manual iteration.
4. **No result validation**: `raw.jsonl` is trusted to be correct if the C++ core exits with code 0.

### Phase 1 が保証しないこと

1. **重複除去なし**: 同型な展開図が `raw.jsonl` に複数回出現します。
2. **近似的な重なりのみ**: C++ コアは外接円の近接性を使用し、厳密な多角形交差は行いません。
3. **呼び出しごとに単一の多面体**: バッチ処理にはスクリプトまたは手動反復が必要です。
4. **結果の検証なし**: C++ コアが終了コード 0 で終了すれば `raw.jsonl` は正しいと信頼されます。

### Intentional Design Choices (Not Bugs)

The following behaviors are intentional and part of the Phase 1 specification:

- **Overwrite on re-run**: Re-executing the same polyhedron replaces the previous output. This is correct behavior for Phase 1, where the latest run is considered authoritative.
- **No timestamp-based directories**: Output paths are based on polyhedron identity, not execution time. The `run_id` in `run.json` provides temporal information when needed.
- **Absolute paths in run.json**: Absolute paths are included intentionally to eliminate ambiguity on the machine where the run was executed. This prioritizes reproducibility verification over portability.
- **No automatic backup**: Previous outputs are not preserved. If historical runs are important, users must manually copy output directories before re-running.

### 意図的な設計選択（バグではない）

以下の挙動は意図的であり、Phase 1 仕様の一部です：

- **再実行時の上書き**: 同じ多面体を再実行すると前の出力を置き換えます。これは Phase 1 の正しい挙動であり、最新の実行が権威的とみなされます。
- **タイムスタンプベースのディレクトリなし**: 出力パスは実行時刻ではなく多面体の同一性に基づきます。必要に応じて `run.json` 内の `run_id` が時間情報を提供します。
- **run.json 内の絶対パス**: 実行されたマシン上での曖昧性を排除するため、絶対パスが意図的に含まれています。これは移植性よりも再現性検証を優先します。
- **自動バックアップなし**: 以前の出力は保存されません。過去の実行が重要な場合、ユーザーは再実行前に出力ディレクトリを手動でコピーする必要があります。

---

## Transition to Phase 2 / Phase 2 への移行

**Phase 1 Output Contract**: `raw.jsonl` + `run.json` serve as the stable interface for all downstream processing.

**Phase 1 出力契約**: `raw.jsonl` + `run.json` はすべての下流処理のための安定したインターフェースとして機能します。

Phase 1 output will serve as **input** for Phase 2 processing:

- **Nonisomorphic filtering** (Phase 2): Read `raw.jsonl`, apply canonical form normalization, output `noniso.jsonl`
- **Exact overlap detection** (Phase 2): Read `noniso.jsonl` or `raw.jsonl`, perform precise geometric checks, output `exact.jsonl`
- **Drawing** (Phase 2): Read `exact.jsonl` or `noniso.jsonl`, generate SVG files

Phase 1 の出力は Phase 2 処理の**入力**として機能します：

- **同型除去**（Phase 2）: `raw.jsonl` を読み込み、正規形正規化を適用、`noniso.jsonl` を出力
- **厳密重なり判定**（Phase 2）: `noniso.jsonl` または `raw.jsonl` を読み込み、精密な幾何チェックを実行、`exact.jsonl` を出力
- **描画**（Phase 2）: `exact.jsonl` または `noniso.jsonl` を読み込み、SVG ファイルを生成

**Phase boundary contract**: Phase 1 does not prescribe the implementation of Phase 2. The only guaranteed contract is:

1. `raw.jsonl` adheres to the schema defined in this document (schema_version: 1, record_type: "partial_unfolding")
2. `run.json` provides sufficient provenance information to identify input conditions
3. Output paths follow the `output/polyhedra/<class>/<name>/` convention

Phase 2 implementations may read these files from the canonical output location or consume them via other mechanisms, as long as the data contract is respected.

**Phase 境界契約**: Phase 1 は Phase 2 の実装を規定しません。保証される唯一の契約は：

1. `raw.jsonl` は本文書で定義されたスキーマに従う（schema_version: 1, record_type: "partial_unfolding"）
2. `run.json` は入力条件を識別するのに十分な出所情報を提供する
3. 出力パスは `output/polyhedra/<class>/<name>/` 規約に従う

Phase 2 の実装は、データ契約が尊重される限り、正規出力場所からこれらのファイルを読み込むか、他のメカニズムを介してそれらを消費することができます。

---

## References / 参考資料

### Specification and Implementation

- **Input format specification**: `tools/convert_legacy_input.py` (schema implementation)
- **C++ core implementation**: `cpp/src/main.cpp` and `cpp/include/`
- **Python CLI implementation**: `python/rotational_unfolding/`
- **Canonical output location**: `output/polyhedra/<class>/<name>/`

### 仕様と実装

- **入力形式仕様**: `tools/convert_legacy_input.py`（スキーマ実装）
- **C++ コア実装**: `cpp/src/main.cpp` および `cpp/include/`
- **Python CLI 実装**: `python/rotational_unfolding/`
- **正規出力場所**: `output/polyhedra/<class>/<name>/`

---

**Document Status**: This document describes the **frozen specification** of Phase 1 as of 2026-02-07. The input/output contract defined here is stable and serves as the foundation for all subsequent phases. Phase 2 and beyond may extend functionality but must respect the Phase 1 data contract.

**文書ステータス**: この文書は 2026-02-07 時点での Phase 1 の**凍結された仕様**を記述します。ここで定義される入出力契約は安定しており、すべての後続フェーズの基盤として機能します。Phase 2 以降は機能を拡張する可能性がありますが、Phase 1 のデータ契約を尊重する必要があります。
