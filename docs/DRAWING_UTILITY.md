# Drawing Utility — Visualization for JSONL Outputs

**Status**: Verification utility (not a Phase component)
**Version**: 0.1.0
**Last Updated**: 2026-02-07

---

## Overview / 概要

The drawing utility is an **independent verification tool** for visualizing JSONL outputs produced by rotational unfolding phases. It converts each JSONL record into an individual SVG file for visual inspection, debugging, and human verification purposes.

描画ユーティリティは、回転展開フェーズが生成する JSONL 出力を可視化するための**独立した検証ツール**です。各 JSONL レコードを個別の SVG ファイルに変換し、視覚的な検査、デバッグ、人間による検証を目的とします。

**This is NOT a Phase component.** The drawing utility operates independently across Phase 1 (raw), Phase 2 (noniso), and Phase 3 (exact) outputs. It does not modify or produce canonical research outputs.

**これは Phase コンポーネントではありません。** 描画ユーティリティは Phase 1（raw）、Phase 2（noniso）、Phase 3（exact）の出力に対して独立して動作します。正規の研究成果物を変更・生成することはありません。

---

## Purpose and Scope / 目的と範囲

### What the Drawing Utility Does / 描画ユーティリティが行うこと

The drawing utility provides:

1. **Visual verification**: Convert JSONL records to SVG for human inspection
2. **Debugging support**: Identify geometric issues or anomalies visually
3. **One-to-one correspondence**: Each SVG file maps to exactly one JSONL record
4. **Deterministic output**: Same JSONL input always produces the same SVG output

描画ユーティリティは以下を提供します：

1. **視覚的検証**: JSONL レコードを SVG に変換して人間による検査を可能にする
2. **デバッグ支援**: 幾何的な問題や異常を視覚的に識別する
3. **一対一対応**: 各 SVG ファイルは正確に1つの JSONL レコードに対応する
4. **決定的な出力**: 同じ JSONL 入力は常に同じ SVG 出力を生成する

### What the Drawing Utility Does NOT Do / 描画ユーティリティが行わないこと

The drawing utility intentionally **does not**:

- **Produce research outputs**: SVG files are verification artifacts, not canonical results
- **Modify JSONL data**: The utility reads JSONL files but never writes or modifies them
- **Belong to any Phase**: It operates independently of Phase 1, 2, and 3
- **Guarantee correctness**: It visualizes data as-is without validation or filtering

描画ユーティリティは意図的に以下を**行いません**：

- **研究成果物の生成**: SVG ファイルは検証用生成物であり、正規の結果ではない
- **JSONL データの変更**: ユーティリティは JSONL ファイルを読み込むが、書き込みや変更は行わない
- **特定 Phase への所属**: Phase 1, 2, 3 から独立して動作する
- **正しさの保証**: データをそのまま可視化するが、検証やフィルタリングは行わない

---

## Input and Output / 入力と出力

### Input: JSONL Files (Canonical Outputs from Phases)

The drawing utility reads JSONL files produced by rotational unfolding phases:

- **raw.jsonl** (Phase 1): Raw partial unfoldings
- **noniso.jsonl** (Phase 2): Nonisomorphic unfoldings
- **exact.jsonl** (Phase 3): Exact overlap-checked unfoldings

The JSONL file is the **authoritative source**. The drawing utility does not interpret, filter, or validate the data—it visualizes records as they appear in the JSONL file.

描画ユーティリティは、回転展開フェーズが生成する JSONL ファイルを読み込みます：

- **raw.jsonl**（Phase 1）: 生の部分展開図
- **noniso.jsonl**（Phase 2）: 非同型展開図
- **exact.jsonl**（Phase 3）: 厳密重なり判定済み展開図

JSONL ファイルが**権威的なソース**です。描画ユーティリティはデータを解釈、フィルタリング、検証せず、JSONL ファイルに現れるレコードをそのまま可視化します。

### Output: SVG Files (Verification Artifacts)

For each record in the JSONL file, the utility generates one SVG file:

- **One-to-one mapping**: SVG file `N` corresponds to JSONL line `N` (0-based indexing)
- **Deterministic naming**: Filename is the 0-based line number, zero-padded based on total record count
- **Self-contained**: Each SVG file is independent and can be viewed in isolation

JSONL ファイルの各レコードに対して、ユーティリティは1つの SVG ファイルを生成します：

- **一対一対応**: SVG ファイル `N` は JSONL の行 `N`（0-based インデックス）に対応
- **決定的な命名**: ファイル名は 0-based 行番号を、総レコード数に基づいてゼロ埋めしたもの
- **自己完結**: 各 SVG ファイルは独立しており、単体で表示可能

---

## Directory Structure / ディレクトリ構造

The drawing utility outputs SVG files to a subdirectory alongside the source JSONL file:

```
output/polyhedra/<class>/<name>/
├── raw.jsonl          # Phase 1 canonical output
├── run.json           # Phase 1 metadata
└── draw/              # Drawing utility output (verification artifacts)
    └── raw/
        ├── 0.svg
        ├── 1.svg
        ├── 2.svg
        └── ...
```

Including Phase 2 output:

```
output/polyhedra/<class>/<name>/
├── raw.jsonl          # Phase 1 output
├── noniso.jsonl       # Phase 2 output
├── exact.jsonl        # Phase 3 output
└── draw/
    ├── raw/           # Visualization of raw.jsonl
    │   ├── 0.svg
    │   └── ...
    ├── noniso/        # Visualization of noniso.jsonl
    │   ├── 0.svg
    │   └── ...
    └── exact/         # Visualization of exact.jsonl
        ├── 0.svg
        └── ...
```

The `draw/` directory is **Git-ignored** (`.gitignore` rule: `output/**/draw/`). SVG files are regenerable from JSONL files and are not committed to the repository.

`draw/` ディレクトリは **Git 管理から除外**されています（`.gitignore` ルール: `output/**/draw/`）。SVG ファイルは JSONL ファイルから再生成可能であり、リポジトリにはコミットされません。

---

## File Naming Convention / ファイル命名規則

### Specification

SVG filenames are constructed as follows:

1. Read the total number of records `N` in the JSONL file
2. Compute zero-padding width: `W = len(str(N-1))`
3. For each record at 0-based index `i`, generate filename: `str(i).zfill(W) + ".svg"`

### ファイル命名仕様

SVG ファイル名は以下のように構成されます：

1. JSONL ファイルの総レコード数 `N` を読み込む
2. ゼロ埋め桁数を計算: `W = len(str(N-1))`
3. 0-based インデックス `i` の各レコードに対して、ファイル名を生成: `str(i).zfill(W) + ".svg"`

### Examples

| Total records | Last index | Padding width | Filenames |
|---------------|-----------|---------------|-----------|
| 6             | 5         | 1             | `0.svg`, `1.svg`, ..., `5.svg` |
| 123           | 122       | 3             | `000.svg`, `001.svg`, ..., `122.svg` |
| 810           | 809       | 3             | `000.svg`, `001.svg`, ..., `809.svg` |

### Design Rationale

This naming scheme ensures:

- **Machine-readable correspondence**: SVG filename directly maps to JSONL line number
- **Natural sorting**: Files sort correctly in filesystem listings
- **Minimal naming**: No metadata (base_face, base_edge, etc.) is encoded in filenames
- **JSONL is the authority**: All metadata is retrieved from the JSONL file, not from SVG filenames

この命名スキームにより以下が保証されます：

- **機械可読な対応関係**: SVG ファイル名は直接 JSONL の行番号に対応
- **自然なソート**: ファイルシステムのリストで正しくソートされる
- **最小命名**: メタデータ（base_face, base_edge 等）はファイル名に含めない
- **JSONL が権威**: すべてのメタデータは SVG ファイル名ではなく JSONL ファイルから取得

---

## Usage / 使用方法

### Command

```bash
PYTHONPATH=python python -m drawing run --type <type> --poly data/polyhedra/<class>/<name> [--no-labels]
```

### Arguments

- `--type`: Output type to visualize
  - `raw`: Phase 1 output (raw.jsonl)
  - `noniso`: Phase 2 output (noniso.jsonl)
  - `exact`: Phase 3 output (exact.jsonl)
- `--poly`: Path to polyhedron data directory (e.g., `data/polyhedra/archimedean/s07`)
- `--no-labels`: Optional. Hide face and edge labels (draw polygons only). Default: labels displayed.

### Examples

```bash
# Visualize raw output for archimedean/s07
PYTHONPATH=python python -m drawing run --type raw --poly data/polyhedra/archimedean/s07

# Visualize nonisomorphic output for archimedean/s07
PYTHONPATH=python python -m drawing run --type noniso --poly data/polyhedra/archimedean/s07

# Visualize raw output for johnson/n20
PYTHONPATH=python python -m drawing run --type raw --poly data/polyhedra/johnson/n20

# Visualize nonisomorphic output for johnson/n20
PYTHONPATH=python python -m drawing run --type noniso --poly data/polyhedra/johnson/n20

# Visualize raw output for platonic/r01
PYTHONPATH=python python -m drawing run --type raw --poly data/polyhedra/platonic/r01

# Visualize exact output for archimedean/s07
PYTHONPATH=python python -m drawing run --type exact --poly data/polyhedra/archimedean/s07

# Visualize exact output for johnson/n66
PYTHONPATH=python python -m drawing run --type exact --poly data/polyhedra/johnson/n66

# Visualize exact output without labels (polygons only)
PYTHONPATH=python python -m drawing run --type exact --poly data/polyhedra/johnson/n66 --no-labels

# Visualize raw output without labels
PYTHONPATH=python python -m drawing run --type raw --poly data/polyhedra/archimedean/s07 --no-labels
```

### Execution Model

The drawing utility operates in a **cwd-independent** manner:

1. Resolves paths relative to the repository root
2. Reads JSONL from: `output/polyhedra/<class>/<name>/<type>.jsonl`
3. Writes SVG to: `output/polyhedra/<class>/<name>/draw/<type>/`
4. Overwrites existing SVG files on re-execution

描画ユーティリティは **cwd 非依存**で動作します：

1. リポジトリルートを基準にパスを解決
2. JSONL を読み込み: `output/polyhedra/<class>/<name>/<type>.jsonl`
3. SVG を書き込み: `output/polyhedra/<class>/<name>/draw/<type>/`
4. 再実行時に既存の SVG ファイルを上書き

---

## SVG Specification / SVG 仕様

### Visual Elements

Each SVG file visualizes a single partial unfolding record with:

- **Polygons**: Black stroke, no fill
- **Face IDs**: Black text at face center
- **Edge IDs**: Red text on shared edges (not on base face)
- **ViewBox**: Automatically computed to fit all vertices with 5% margin

**Label visibility by `--no-labels` option:**

| Option | Polygons | Face IDs | Edge IDs |
|--------|----------|----------|----------|
| (default) | Displayed | Displayed | Displayed |
| `--no-labels` | Displayed | **Hidden** | **Hidden** |

Label visibility is controlled by the `--no-labels` option and applies uniformly to all types (`raw`, `noniso`, `exact`). By default, all labels are displayed. When `--no-labels` is specified, face and edge labels are suppressed and only polygon outlines are drawn. The JSONL record remains the authoritative source for all label information.

### 視覚要素

各 SVG ファイルは1つの部分展開図レコードを以下で可視化します：

- **多角形**: 黒枠、塗りなし
- **面番号**: 中心に黒字
- **辺番号**: 共有辺上に赤字（ベース面は除く）
- **ViewBox**: 全頂点を包含するよう 5% マージン付きで自動計算

**`--no-labels` オプションによるラベル表示：**

| オプション | 多角形 | 面番号 | 辺番号 |
|------------|--------|--------|--------|
| （デフォルト） | 表示 | 表示 | 表示 |
| `--no-labels` | 表示 | **非表示** | **非表示** |

ラベル表示は `--no-labels` オプションで制御され、すべての type（`raw`、`noniso`、`exact`）に対して統一的に適用されます。デフォルトではすべてのラベルが表示されます。`--no-labels` を指定すると面番号と辺番号が非表示となり、多角形のアウトラインのみが描画されます。すべてのラベル情報は JSONL レコードが権威的ソースとして保持します。

### Fixed Properties (for Consistency)

The following properties are fixed to ensure visual consistency across all SVG files:

- **Coordinate system**: JSONL `x, y` coordinates as-is (no transformation)
- **Angle interpretation**: `angle_deg` as edge normal direction
- **Scale**: Regular polygon edge length = 1, circumradius-based
- **Font size**: 0.2% of viewBox smallest dimension (scales with drawing size)

### 固定特性（一貫性のため）

すべての SVG ファイルで視覚的一貫性を保証するため、以下の特性は固定されています：

- **座標系**: JSONL の `x, y` 座標をそのまま使用（変換なし）
- **角度解釈**: `angle_deg` を辺法線の向きとして使用
- **スケール**: 正多角形の辺長=1、circumradius ベース
- **フォントサイズ**: viewBox 最小次元の 0.2%（描画サイズに応じてスケール）

---

## Guarantees / 保証

The drawing utility provides the following guarantees:

1. **One-to-one correspondence**: SVG file `N` always corresponds to JSONL line `N` (0-based)
2. **Deterministic output**: Same JSONL input produces identical SVG files
3. **No data modification**: The utility never modifies or writes JSONL files
4. **Visual faithfulness**: Coordinates and angles are rendered exactly as specified in JSONL

描画ユーティリティは以下を保証します：

1. **一対一対応**: SVG ファイル `N` は常に JSONL の行 `N`（0-based）に対応
2. **決定的な出力**: 同じ JSONL 入力は同一の SVG ファイルを生成
3. **データ変更なし**: ユーティリティは JSONL ファイルを変更・書き込みしない
4. **視覚的忠実性**: 座標と角度は JSONL で指定された通りに正確にレンダリング

---

## Non-Guarantees / 非保証

The drawing utility does NOT guarantee:

1. **No correctness validation**: The utility visualizes JSONL as-is without verifying correctness
2. **No publication-quality output**: SVG files are for debugging, not for papers or presentations
3. **No metadata preservation**: Only geometric data is rendered; metadata is not displayed
4. **No backward compatibility**: Future versions may change SVG styling or layout

描画ユーティリティは以下を保証しません：

1. **正しさの検証なし**: ユーティリティは JSONL をそのまま可視化し、正しさを検証しない
2. **論文品質の出力なし**: SVG ファイルはデバッグ用であり、論文やプレゼンテーション用ではない
3. **メタデータ保存なし**: 幾何データのみがレンダリングされ、メタデータは表示されない
4. **後方互換性なし**: 将来のバージョンは SVG のスタイルやレイアウトを変更する可能性がある

---

## Verification Workflow / 検証ワークフロー

### Typical Usage Pattern

1. **Generate JSONL**: Run Phase 1 to produce `raw.jsonl`
2. **Visualize**: Use the drawing utility to generate SVG files
3. **Inspect visually**: Open SVG files in a browser or viewer to check for issues
4. **Cross-reference**: If an issue is found, locate the corresponding JSONL record by filename
5. **Regenerate if needed**: Re-run the drawing utility to update SVG files after JSONL changes

### 典型的な使用パターン

1. **JSONL を生成**: Phase 1 を実行して `raw.jsonl` を生成
2. **可視化**: 描画ユーティリティを使用して SVG ファイルを生成
3. **視覚的検査**: ブラウザやビューアで SVG ファイルを開き、問題をチェック
4. **相互参照**: 問題が見つかった場合、ファイル名で対応する JSONL レコードを特定
5. **必要に応じて再生成**: JSONL 変更後、描画ユーティリティを再実行して SVG を更新

### Example: Full Pipeline with Drawing at Each Stage

```bash
# Phase 1: Generate raw unfoldings
PYTHONPATH=python python -m rotational_unfolding run --poly data/polyhedra/johnson/n20

# Draw raw output (with labels)
PYTHONPATH=python python -m drawing run --type raw --poly data/polyhedra/johnson/n20

# Phase 2: Remove isomorphic duplicates
PYTHONPATH=python python -m nonisomorphic run --poly data/polyhedra/johnson/n20

# Draw noniso output (with labels)
PYTHONPATH=python python -m drawing run --type noniso --poly data/polyhedra/johnson/n20

# Phase 3: Exact overlap verification
PYTHONPATH=python python -m exact run --poly data/polyhedra/johnson/n20

# Draw exact output (shape only, no labels)
PYTHONPATH=python python -m drawing run --type exact --poly data/polyhedra/johnson/n20
```

### Example: Debugging a Specific Record

```bash
# Step 1: Generate raw.jsonl (Phase 1)
PYTHONPATH=python python -m rotational_unfolding run --poly data/polyhedra/archimedean/s07

# Step 2: Generate SVG files (drawing utility)
PYTHONPATH=python python -m drawing run --type raw --poly data/polyhedra/archimedean/s07

# Step 3: Open SVG file 5 (corresponds to JSONL line 5, 0-based)
open output/polyhedra/archimedean/s07/draw/raw/5.svg

# Step 4: If issue found, inspect JSONL line 5 (the 6th line)
sed -n '6p' output/polyhedra/archimedean/s07/raw.jsonl | jq .
```

---

## Important Notes / 重要な注意事項

### SVG Files Are NOT Research Outputs

**The SVG files produced by the drawing utility are verification artifacts, not canonical research results.**

- They are **Git-ignored** and not committed to the repository
- They are **regenerable** from JSONL files at any time
- They are **not authoritative** for any scientific claim or publication

**描画ユーティリティが生成する SVG ファイルは検証用生成物であり、正規の研究結果ではありません。**

- **Git 管理から除外**されており、リポジトリにコミットされない
- JSONL ファイルからいつでも**再生成可能**
- 科学的主張や出版物に対して**権威的ではない**

### JSONL Is the Authority

All scientific conclusions must be based on JSONL files, not SVG files. The drawing utility is a convenience tool for human inspection, but it does not add or validate any information beyond what is present in the JSONL file.

すべての科学的結論は SVG ファイルではなく JSONL ファイルに基づく必要があります。描画ユーティリティは人間による検査のための便利ツールですが、JSONL ファイルに存在する情報を超えて追加・検証することはありません。

### Overwrite Behavior

Re-running the drawing utility for the same polyhedron will **overwrite** existing SVG files. This is intentional behavior, as SVG files are always regenerable from the JSONL source.

同じ多面体に対して描画ユーティリティを再実行すると、既存の SVG ファイルが**上書き**されます。これは意図的な挙動であり、SVG ファイルは JSONL ソースから常に再生成可能です。

---

## Dependencies / 依存関係

The drawing utility uses only the Python standard library. No additional dependencies are required.

描画ユーティリティは Python 標準ライブラリのみを使用します。追加の依存関係は不要です。

---

**Document Status**: This document describes the drawing utility as an independent verification tool. It is not part of Phase 1, 2, or 3 specifications. The utility may be extended or modified independently of Phase implementations.

**文書ステータス**: この文書は独立した検証ツールとしての描画ユーティリティを記述します。これは Phase 1, 2, 3 の仕様の一部ではありません。ユーティリティは Phase 実装から独立して拡張または変更される可能性があります。
