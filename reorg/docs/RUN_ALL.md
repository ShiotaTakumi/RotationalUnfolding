# run_all — Full Pipeline Execution in a Single Command

**Status**: Implemented (Specification Frozen)
**Version**: 1.0.0
**Last Updated**: 2026-02-07

---

## Overview / 概要

`run_all` is a researcher-oriented utility that executes the entire rotational unfolding pipeline—from raw enumeration to exact overlap verification and visualization—with a single command and a single argument.

`run_all` は研究者向けユーティリティであり、回転展開パイプライン全体（生列挙から厳密重なり検証・可視化まで）を、1 つのコマンドと 1 つの引数で実行します。

**This is an orchestrator, not a processing module.** `run_all` does not implement any algorithm. It invokes Phase 1, Phase 2, Phase 3, and the drawing utility as independent subprocesses, in a fixed order. Each phase runs its own CLI exactly as if the researcher had typed the command manually.

**これはオーケストレーターであり、処理モジュールではありません。** `run_all` はアルゴリズムを一切実装しません。Phase 1、Phase 2、Phase 3、drawing ユーティリティを独立したサブプロセスとして固定順序で呼び出します。各フェーズは、研究者が手動でコマンドを入力した場合とまったく同じ CLI を実行します。

---

## Purpose and Motivation / 目的と動機

### Why run_all Exists / なぜ run_all が必要か

The rotational unfolding pipeline consists of four independent stages. Running them manually requires four separate commands with identical `--poly` arguments. This is:

- **Error-prone**: A typo in one command produces inconsistent outputs across phases.
- **Tedious**: Researchers must wait for each phase to finish before starting the next.
- **Undocumented by default**: Without a single entry point, reproducing a full run requires knowledge of all four commands.

`run_all` eliminates these issues. It provides:

- **One command, one argument**: `--poly polyhedra/CLASS/NAME` is the only input.
- **Reproducibility by invocation**: A single shell command fully reproduces the pipeline.
- **Fail-fast behavior**: If any phase fails, execution stops immediately.

回転展開パイプラインは 4 つの独立した段階で構成されています。手動実行には、同じ `--poly` 引数を持つ 4 つの個別コマンドが必要です。これは：

- **ミスを誘発する**: 1 つのコマンドのタイプミスがフェーズ間で不整合な出力を生む
- **煩雑である**: 各フェーズの完了を待ってから次を開始する必要がある
- **再現手順が暗黙知になる**: 単一のエントリポイントなしに完全な実行を再現するには、4 つのコマンドすべての知識が必要

`run_all` はこれらの問題を排除します：

- **1 コマンド、1 引数**: `--poly polyhedra/CLASS/NAME` が唯一の入力
- **呼び出しによる再現性**: 単一のシェルコマンドでパイプライン全体を再現可能
- **即時停止**: いずれかのフェーズが失敗した場合、実行は即座に停止

### What run_all Automates / run_all が自動化する範囲

| Step | Module | Output |
|------|--------|--------|
| Phase 1 | `rotational_unfolding` | `raw.jsonl`, `run.json` |
| Phase 2 | `nonisomorphic` | `noniso.jsonl` |
| Phase 3 | `exact` | `exact.jsonl` |
| Drawing | `drawing` (exact only) | `draw/exact/*.svg` |

Drawing is executed for `exact` output only. `raw` and `noniso` visualizations are not included in the automated pipeline. Researchers who need those visualizations invoke the `drawing` utility separately.

Drawing は `exact` 出力に対してのみ実行されます。`raw` および `noniso` の可視化は自動パイプラインに含まれません。それらの可視化が必要な研究者は `drawing` ユーティリティを個別に呼び出します。

---

## Usage / 使用方法

### Command / コマンド

```bash
PYTHONPATH=reorg/python python -m run_all --poly polyhedra/<class>/<name>
```

### Examples / 実行例

```bash
# Archimedean solid s07
PYTHONPATH=reorg/python python -m run_all --poly polyhedra/archimedean/s07

# Johnson solid n20
PYTHONPATH=reorg/python python -m run_all --poly polyhedra/johnson/n20

# Johnson solid n66
PYTHONPATH=reorg/python python -m run_all --poly polyhedra/johnson/n66
```

### Arguments / 引数

| Argument | Required | Description |
|----------|----------|-------------|
| `--poly polyhedra/CLASS/NAME` | Yes | Polyhedron path. `polyhedra` is a fixed prefix. `CLASS` is the polyhedron family (e.g., `archimedean`, `johnson`). `NAME` is the specific polyhedron (e.g., `s07`, `n20`). Shell Tab completion is supported. |

The `--poly` argument is the only input. There are no optional flags.

`--poly` 引数が唯一の入力です。オプションフラグはありません。

---

## Execution Order / 実行順序

`run_all` executes exactly four steps, in this fixed order. The order is not configurable.

`run_all` は正確に 4 つのステップを、この固定順序で実行します。順序は変更できません。

### Step 1: Phase 1 — Rotational Unfolding / 回転展開

```
[run_all] Phase 1: rotational_unfolding
```

Invokes:

```bash
python -m rotational_unfolding run --poly polyhedra/<class>/<name>
```

- Calls the C++ binary to enumerate all rotational unfoldings.
- Produces `raw.jsonl` (complete enumeration) and `run.json` (execution metadata).
- Overwrites existing files.

### Step 2: Phase 2 — Nonisomorphic Filtering / 非同型フィルタリング

```
[run_all] Phase 2: nonisomorphic
```

Invokes:

```bash
python -m nonisomorphic run --poly polyhedra/<class>/<name>
```

- Reads `raw.jsonl` (read-only).
- Removes geometrically equivalent unfoldings.
- Produces `noniso.jsonl`.
- Overwrites existing files.

### Step 3: Phase 3 — Exact Overlap Detection / 厳密重なり判定

```
[run_all] Phase 3: exact
```

Invokes:

```bash
python -m exact run --poly polyhedra/<class>/<name>
```

- Reads `noniso.jsonl` (read-only).
- Performs exact overlap verification using SymPy symbolic computation.
- Produces `exact.jsonl` with overlap classification.
- Overwrites existing files.

### Step 4: Drawing — Exact Visualization / 厳密結果の描画

```
[run_all] Drawing: exact
```

Invokes:

```bash
python -m drawing run --type exact --poly polyhedra/<class>/<name>
```

- Reads `exact.jsonl` (read-only).
- Generates one SVG file per record.
- Outputs to `draw/exact/`.
- Overwrites existing files.

---

## Output Directory Structure / 出力ディレクトリ構造

After a complete `run_all` execution, the output directory has the following structure:

`run_all` の完全な実行後、出力ディレクトリは以下の構造になります：

```
reorg/output/polyhedra/<class>/<name>/
├── raw.jsonl           # Phase 1: complete enumeration / 完全列挙
├── run.json            # Phase 1: execution metadata / 実行メタデータ
├── noniso.jsonl        # Phase 2: deduplicated records / 重複除去済みレコード
├── exact.jsonl         # Phase 3: verified records with overlap classification / 検証済みレコード（重なり分類付き）
└── draw/
    └── exact/          # Drawing: SVG visualization of exact.jsonl / exact.jsonl の SVG 可視化
        ├── 0.svg
        ├── 1.svg
        └── ...
```

### File Relationships / ファイル間の関係

```
raw.jsonl (Phase 1)
  │  complete enumeration / 完全列挙
  ▼
noniso.jsonl (Phase 2)
  │  deduplicated subset / 重複除去済み部分集合
  ▼
exact.jsonl (Phase 3)
  │  overlap-verified subset / 重なり検証済み部分集合
  ▼
draw/exact/*.svg (Drawing)
     visual confirmation / 目視確認
```

Each downstream output is a strict subset of its input. Record content is never modified—only filtered (Phase 2, Phase 3) or visualized (Drawing).

各下流出力は入力の厳密な部分集合です。レコード内容は変更されず、フィルタリング（Phase 2・Phase 3）または可視化（Drawing）のみが行われます。

---

## Guarantees / 保証事項

### Pipeline Integrity / パイプラインの整合性

- **Each phase is invoked as an independent subprocess.** `run_all` does not import or call any phase's internal functions. Each phase runs its own CLI entry point.
- **No data is generated by `run_all` itself.** All JSONL files, `run.json`, and SVG files are produced by their respective phases.
- **Existing outputs are overwritten.** Each phase overwrites its own output file if it already exists. This is the intended behavior.
- **Failure stops the pipeline.** If any phase exits with a non-zero status, `run_all` terminates immediately. Subsequent phases are not executed.
- **Order is deterministic.** Phase 1 → Phase 2 → Phase 3 → Drawing. Always.

- **各フェーズは独立したサブプロセスとして呼び出される。** `run_all` はいかなるフェーズの内部関数もインポート・呼び出ししない。各フェーズは自身の CLI エントリポイントを実行する。
- **`run_all` 自体はデータを生成しない。** すべての JSONL ファイル、`run.json`、SVG ファイルはそれぞれのフェーズが生成する。
- **既存の出力は上書きされる。** 各フェーズは自身の出力ファイルが既に存在する場合、上書きする。これは意図された動作である。
- **失敗はパイプラインを停止する。** いずれかのフェーズがゼロ以外のステータスで終了した場合、`run_all` は即座に終了する。後続フェーズは実行されない。
- **順序は決定論的である。** Phase 1 → Phase 2 → Phase 3 → Drawing。常に。

### Architectural Separation / アーキテクチャ的分離

- **Phase 1, Phase 2, Phase 3, and Drawing are independent modules.** `run_all` does not create coupling between them.
- **Each phase's code is untouched.** `run_all` exists in `reorg/python/run_all/` and does not modify any file in `rotational_unfolding/`, `nonisomorphic/`, `exact/`, or `drawing/`.
- **Drawing is a verification utility, not a pipeline artifact.** SVG files in `draw/exact/` are for visual confirmation. They are not research outputs and are not referenced by any downstream process.

- **Phase 1・Phase 2・Phase 3・Drawing は独立したモジュールである。** `run_all` はそれらの間の結合を生み出さない。
- **各フェーズのコードは変更されない。** `run_all` は `reorg/python/run_all/` に存在し、`rotational_unfolding/`・`nonisomorphic/`・`exact/`・`drawing/` 内のいかなるファイルも変更しない。
- **Drawing は検証用ユーティリティであり、パイプライン成果物ではない。** `draw/exact/` 内の SVG ファイルは目視確認用である。研究成果物ではなく、いかなる下流プロセスからも参照されない。

---

## Non-Guarantees / 非保証事項

- **Execution time is not bounded.** Phase 3 uses SymPy symbolic computation, which prioritizes exactness over speed. For complex polyhedra, Phase 3 alone may take hours.
- **Partial outputs from failed runs are not cleaned up.** If Phase 3 fails, Phase 1 and Phase 2 outputs remain in the output directory. This is by design—earlier phases' outputs are valid and reusable.
- **Overlap definition is strict.** Phase 3 treats all geometric contacts (including point-point, point-edge) as overlaps. This is the "strict" definition. `run_all` does not provide an option to change this.

- **実行時間は保証されない。** Phase 3 は SymPy のシンボリック計算を使用し、速度よりも厳密性を優先する。複雑な多面体では、Phase 3 だけで数時間かかることがある。
- **失敗した実行の部分出力はクリーンアップされない。** Phase 3 が失敗した場合、Phase 1 と Phase 2 の出力はディレクトリに残る。これは設計上の意図であり、前段フェーズの出力は有効かつ再利用可能である。
- **重なり定義は strict である。** Phase 3 はすべての幾何的接触（点–点、点–辺を含む）を重なりとみなす。これは "strict" 定義である。`run_all` はこの定義を変更するオプションを提供しない。

---

## Use Cases / 想定ユースケース

### Full Pipeline Execution / パイプライン一括実行

A researcher studying a specific polyhedron runs the entire pipeline from scratch:

特定の多面体を研究する際に、パイプライン全体をゼロから実行する：

```bash
PYTHONPATH=reorg/python python -m run_all --poly polyhedra/johnson/n66
```

This produces all outputs (`raw.jsonl`, `run.json`, `noniso.jsonl`, `exact.jsonl`, `draw/exact/*.svg`) in a single invocation. The researcher can immediately inspect the SVG files to visually confirm the verified unfoldings.

これにより、すべての出力（`raw.jsonl`、`run.json`、`noniso.jsonl`、`exact.jsonl`、`draw/exact/*.svg`）が単一の呼び出しで生成されます。研究者は SVG ファイルを即座に確認し、検証済み展開図を目視で確認できます。

### Reproducibility / 再現性

For paper artifacts or shared experiments, the full pipeline is reproducible with a single command:

論文アーティファクトや共有実験において、パイプライン全体が単一のコマンドで再現可能です：

```bash
# Reproduce the complete result for archimedean s07
PYTHONPATH=reorg/python python -m run_all --poly polyhedra/archimedean/s07
```

The command is self-contained. No prior state, configuration files, or intermediate outputs are required.

コマンドは自己完結しています。事前の状態、設定ファイル、中間出力は不要です。

### Visual Inspection of Exact Results / Exact 結果の目視確認

After execution, the `draw/exact/` directory contains one SVG per verified unfolding. These SVGs render polygon outlines only (no face or edge labels), providing clean visual confirmation of the final results.

実行後、`draw/exact/` ディレクトリに検証済み展開図ごとの SVG が格納されます。これらの SVG は多角形のアウトラインのみ（面ラベル・辺ラベルなし）を描画し、最終結果のクリーンな目視確認を提供します。

---

## Log Output / ログ出力

`run_all` prints step markers to stdout before each phase. All subprocess output (stdout and stderr) is passed through without suppression.

`run_all` は各フェーズの前にステップマーカーを stdout に出力します。すべてのサブプロセス出力（stdout・stderr）は抑制されずにそのまま表示されます。

```
[run_all] Pipeline start: archimedean/s07
[run_all] Python: /path/to/python

[run_all] Phase 1: rotational_unfolding
... (Phase 1 output) ...

[run_all] Phase 2: nonisomorphic
... (Phase 2 output) ...

[run_all] Phase 3: exact
... (Phase 3 output) ...

[run_all] Drawing: exact
... (Drawing output) ...

[run_all] All steps completed for: archimedean/s07
```

On failure, the pipeline terminates with an error message indicating which step failed:

失敗時、パイプラインはどのステップで失敗したかを示すエラーメッセージと共に終了します：

```
[run_all] FAILED at: Phase 3: exact (exit code 1)
```

---

## Module Location / モジュール配置

```
reorg/python/run_all/
├── __init__.py
└── __main__.py
```

`run_all` is a standalone package. It has no dependencies on Phase 1, Phase 2, Phase 3, or Drawing at the Python import level. All invocations are via `subprocess.run()`.

`run_all` は独立したパッケージです。Python import レベルで Phase 1・Phase 2・Phase 3・Drawing への依存はありません。すべての呼び出しは `subprocess.run()` 経由です。
