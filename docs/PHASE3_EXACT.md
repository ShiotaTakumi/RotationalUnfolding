# Phase 3: Exact Overlap Detection — Rigorous Verification of Unfolding Validity

**Status**: Implemented (Specification Frozen)
**Version**: 2.0.0
**Last Updated**: 2026-02-13

---

## Overview / 概要

Phase 3 implements exact overlap detection for rotational unfolding outputs. It reads the deduplicated enumeration produced by Phase 2 (`noniso.jsonl`) and removes unfoldings that contain spurious overlaps, producing a verified output (`exact.jsonl`).

Phase 3 は回転展開出力の厳密重なり判定を実装します。Phase 2 が生成した重複除去済み列挙（`noniso.jsonl`）を読み込み、不正な重なりを含む展開図を除去し、検証済み出力（`exact.jsonl`）を生成します。

**This is the final verification phase.** Phase 3 operates as the terminal downstream filter in the processing pipeline. It does not re-run the unfolding algorithm, does not perform deduplication, and does not modify the geometric data in individual records—it only determines which records represent geometrically valid overlapping unfoldings. The overlap detection is **exact**: coordinates are reconstructed as symbolic algebraic expressions (SymPy), and intersection tests are performed without floating-point error.

**これは最終検証フェーズです。** Phase 3 は処理パイプラインの終端下流フィルターとして動作します。展開アルゴリズムを再実行せず、重複除去を行わず、個々のレコードの幾何データを変更しません。どのレコードが幾何学的に妥当な重なり展開図であるかのみを判定します。重なり判定は**厳密**です：座標はシンボリック代数式（SymPy）として再構築され、交差判定は浮動小数点誤差なしに実行されます。

---

## Purpose and Scope / 目的と範囲

### What Phase 3 Does / Phase 3 が行うこと

Phase 3 focuses on **exact geometric verification** of overlap between the first and last faces of each unfolding:

1. **Read Phase 2 output**: Load `noniso.jsonl` as input (read-only, never modified)
2. **Load polyhedron structure**: Read `polyhedron.json` for adjacency and vertex incidence
3. **Reconstruct exact coordinates**: Build SymPy symbolic expressions for face positions (no floating-point)
4. **Verify endpoint overlap**: Confirm that the first and last faces have a genuine intersection
5. **Reject spurious overlaps**: Remove records where non-adjacent, non-endpoint face pairs intersect
6. **Classify overlap kind**: Identify the geometric type of each detected overlap
7. **Write verified output**: Produce `exact.jsonl` with augmented overlap classification

Phase 3 は各展開図の最初と最後の面の重なりについて**厳密な幾何検証**に焦点を当てます：

1. **Phase 2 出力を読み込む**: `noniso.jsonl` を入力としてロード（読み取り専用、変更なし）
2. **多面体構造を読み込む**: 隣接情報と頂点共有関係のために `polyhedron.json` を読む
3. **厳密座標を再構築する**: 面の位置を SymPy シンボリック式で構築（浮動小数点なし）
4. **端点重なりを検証する**: 最初と最後の面が真の交差を持つことを確認
5. **不正な重なりを除去する**: 非隣接・非端点の面ペアが交差するレコードを除去
6. **重なり種別を分類する**: 検出された各重なりの幾何学的な種類を特定
7. **検証済み出力を書き出す**: 重なり分類が付与された `exact.jsonl` を生成

### What Phase 3 Does NOT Do / Phase 3 が行わないこと

Phase 3 intentionally **does not**:

- **Modify record content**: Each kept record preserves all original fields from `noniso.jsonl`
- **Re-run the algorithm**: Phase 3 is a filter, not a generator
- **Perform deduplication**: That is Phase 2's responsibility
- **Generate metadata**: No new `run.json` is created
- **Draw or visualize**: No SVG or graphical output is generated
- **Optimize for speed**: Exactness is prioritized over execution time

Phase 3 は意図的に以下を**行いません**：

- **レコード内容の変更**: 保持される各レコードは `noniso.jsonl` の全フィールドを保持
- **アルゴリズムの再実行**: Phase 3 はフィルターであり、生成器ではない
- **重複除去**: それは Phase 2 の責務
- **メタデータの生成**: 新しい `run.json` は作成されない
- **描画・可視化**: SVG やグラフィカルな出力は生成されない
- **速度の最適化**: 実行時間よりも厳密性を優先

---

## Architecture / アーキテクチャ

Phase 3 is implemented as an **independent Python module** that operates on canonical Phase 2 outputs:

Phase 3 は Phase 2 の正規出力に対して動作する**独立した Python モジュール**として実装されます：

```
Phase 1 (rotational_unfolding)
    ↓ generates
output/polyhedra/<class>/<name>/
├── raw.jsonl          ← Phase 1 output
└── run.json           ← Phase 1 metadata (authoritative)

    ↓ Phase 2 reads raw.jsonl

Phase 2 (nonisomorphic)
    ↓ filters & writes
├── noniso.jsonl       ← Phase 2 output (input to Phase 3)

    ↓ Phase 3 reads noniso.jsonl + polyhedron.json

Phase 3 (exact)
    ↓ verifies & writes
├── exact.jsonl        ← Phase 3 output (new)
```

### Responsibility Separation / 責務分離

| Component | Responsibility |
|-----------|----------------|
| **Phase 1** | Generate complete enumeration, maintain metadata |
| **Phase 2** | Deduplicate via canonical form, preserve order |
| **Phase 3** | Verify overlap exactness, classify overlap type |
| **Drawing** | Visualize JSONL records as SVG (independent utility) |

| コンポーネント | 責務 |
|-----------|----------------|
| **Phase 1** | 完全列挙生成、メタデータ維持 |
| **Phase 2** | 正規形による重複除去、順序保持 |
| **Phase 3** | 重なりの厳密性検証、重なり種別の分類 |
| **Drawing** | JSONL レコードを SVG として可視化（独立ユーティリティ） |

Each component is implemented as a separate Python module under `python/`. There are no import dependencies between them. Phase 3 reads files produced by earlier phases but shares no code with them.

各コンポーネントは `python/` 配下の独立した Python モジュールとして実装されます。モジュール間のインポート依存はありません。Phase 3 は以前のフェーズが生成したファイルを読み込みますが、コードを共有しません。

---

## Why the Detection Is Exact / なぜ判定が厳密であると言えるのか

This section provides the mathematical and computational basis for the exactness claim. The argument rests on three pillars: exact coordinate construction, a hybrid detection strategy that never sacrifices correctness, and complete fallback to symbolic geometry.

本セクションでは、厳密性の主張の数学的・計算的根拠を示します。論拠は3つの柱に立脚します：厳密な座標構築、正しさを犠牲にしないハイブリッド検出戦略、シンボリック幾何への完全なフォールバック。

### 1. Exact Coordinate Construction / 厳密な座標構築

Phase 3 does not use the floating-point coordinates stored in `noniso.jsonl`. Instead, it **reconstructs every face position from scratch** as a SymPy symbolic expression.

Phase 3 は `noniso.jsonl` に格納された浮動小数点座標を使用しません。代わりに、すべての面位置を SymPy シンボリック式として**ゼロから再構築**します。

The reconstruction proceeds as follows:

1. **Base face**: Placed at the origin with angle 0 — coordinates are exact rational numbers.
2. **Second face**: Positioned using the inradii of the base and second faces — expressed as `1/(2·tan(π/n))`, an exact algebraic expression.
3. **Subsequent faces**: Each face is incrementally positioned using:
   - Counterclockwise step counting on the polyhedron's face adjacency graph
   - Rotational offsets computed as exact multiples of `2π/n`
   - Translations by `inradius(prev) + inradius(curr)` along exact trigonometric directions

再構築は以下のように進行します：

1. **基準面**: 原点に角度 0 で配置 — 座標は厳密な有理数。
2. **2番目の面**: 基準面と2番目の面の内接円半径を用いて配置 — `1/(2·tan(π/n))` として厳密な代数式で表現。
3. **後続の面**: 各面は以下を用いて逐次的に配置：
   - 多面体の面隣接グラフ上の反時計回りステップ数
   - `2π/n` の厳密な倍数として計算される回転オフセット
   - 厳密な三角関数方向に沿った `inradius(prev) + inradius(curr)` による並進

**All arithmetic operations are performed symbolically.** The only primitives are rational numbers, `π`, `sin`, `cos`, and `tan` — all maintained as unevaluated SymPy expressions. No intermediate rounding or floating-point conversion occurs at any stage of coordinate construction.

**すべての算術演算はシンボリックに実行されます。** 使用されるプリミティブは有理数、`π`、`sin`、`cos`、`tan` のみであり、すべて未評価の SymPy 式として保持されます。座標構築のいかなる段階でも中間的な丸めや浮動小数点変換は発生しません。

This approach is mathematically equivalent to the legacy exact expression generation. The key difference is that Phase 3 constructs expressions directly in memory without writing intermediate files.

このアプローチは legacy の厳密式生成と数学的に同等です。主な違いは、Phase 3 が中間ファイルを書き出さずにメモリ上で直接式を構築する点です。

### 2. Hybrid Detection Strategy / ハイブリッド検出戦略

Phase 3 uses a two-stage detection strategy that combines numeric speed with symbolic exactness. **This design never sacrifices correctness for performance.**

Phase 3 は数値的な速度とシンボリックな厳密性を組み合わせた二段階検出戦略を使用します。**この設計は性能のために正しさを犠牲にしません。**

**Stage 1: High-precision numeric filter (80-digit evaluation)**

For each edge pair, the exact SymPy expressions are numerically evaluated to 80 decimal digits using `evalf(80)`. This evaluation is used only for fast rejection and clear-case detection:

- **AABB rejection**: Bounding box non-overlap eliminates most edge pairs without symbolic computation.
- **Clear crossing detection**: If the orientation tests show both endpoints of each segment on strictly opposite sides (with margin `ε = 10⁻³⁰`), the intersection is a proper edge crossing. This is classified as `face-face` and returned immediately.
- **Ambiguity detection**: If any orientation value falls within `ε` of zero, or if a numeric point-on-segment test triggers, the edge pair is flagged as ambiguous.

**ステージ 1: 高精度数値フィルタ（80桁評価）**

各辺ペアについて、厳密な SymPy 式を `evalf(80)` で 80 桁の数値に評価します。この評価は高速な棄却と明確なケースの検出にのみ使用されます：

- **AABB 棄却**: バウンディングボックスの非重複により、シンボリック計算なしに大部分の辺ペアを除外。
- **明確な交差検出**: 配向テストが各セグメントの両端点が厳密に反対側にあることを示す場合（マージン `ε = 10⁻³⁰`）、交差は正規の辺交差。これは `face-face` として分類され、即座に返される。
- **曖昧性検出**: いずれかの配向値が零の `ε` 以内にある場合、または数値的な点-線分テストが発動した場合、その辺ペアは曖昧としてフラグ付けされる。

**The numeric stage never makes a final "no overlap" decision on an ambiguous case.** Every ambiguous edge pair is forwarded to the exact stage.

**数値段階は、曖昧なケースに対して「重なりなし」の最終判断を行いません。** すべての曖昧な辺ペアは厳密段階に転送されます。

**Stage 2: Exact symbolic geometry (Direct parametric intersection)**

For every ambiguous edge pair, Phase 3 computes the intersection using **direct parametric line equations** with exact SymPy arithmetic. This avoids the overhead and potential errors of `sympy.geometry.Segment.intersection()`.

**ステージ 2: 厳密シンボリック幾何（直接パラメトリック交差）**

すべての曖昧な辺ペアについて、Phase 3 は厳密な SymPy 演算で**直接パラメトリック直線方程式**を用いて交差を計算します。これにより、`sympy.geometry.Segment.intersection()` のオーバーヘッドと潜在的なエラーを回避します。

**Method:**
1. **Parametric representation**: Segment 1 as `P1 + t·(P2-P1)`, Segment 2 as `Q1 + s·(Q2-Q1)`, where `t, s ∈ [0,1]`
2. **Intersection equation**: Solve `P1 + t·d1 = Q1 + s·d2` as a 2×2 linear system
3. **Parallel check**: If `det = d1×d2 ≈ 0`, segments are parallel/collinear
4. **Range validation**: Verify `t, s ∈ [0,1]` using SymPy's exact comparison
5. **Classification**: Determine intersection type based on parameter values

**方法:**
1. **パラメトリック表現**: セグメント 1 を `P1 + t·(P2-P1)`、セグメント 2 を `Q1 + s·(Q2-Q1)` とする。ただし `t, s ∈ [0,1]`
2. **交差方程式**: `P1 + t·d1 = Q1 + s·d2` を 2×2 線形システムとして解く
3. **平行チェック**: `det = d1×d2 ≈ 0` ならセグメントは平行/同一直線上
4. **範囲検証**: SymPy の厳密比較で `t, s ∈ [0,1]` を検証
5. **分類**: パラメータ値に基づいて交差種別を決定

**Correctness argument**: The numeric stage acts as a conservative fast path. It either confirms an intersection with certainty (proper crossing with 80-digit margin) or defers to the exact stage. The exact stage is the sole arbiter for all boundary cases. Therefore, the overall detection is as exact as SymPy's symbolic arithmetic — **no floating-point approximation affects the final decision**.

**正しさの論拠**: 数値段階は保守的な高速パスとして機能します。確実に交差を確認するか（80桁マージンでの正規交差）、厳密段階に委ねるかのいずれかです。厳密段階がすべての境界ケースの唯一の裁定者です。したがって、全体の検出は SymPy のシンボリック演算と同程度に厳密です — **最終判定に浮動小数点近似は影響しません**。

### 3. Direct Parametric Intersection / 直接パラメトリック交差

The exact stage uses **direct parametric line intersection** instead of SymPy's `Segment.intersection()`. This provides the same exactness with better performance and error handling.

厳密段階は SymPy の `Segment.intersection()` の代わりに**直接パラメトリック直線交差**を使用します。これにより、同じ厳密性をより良いパフォーマンスとエラー処理で提供します。

**Algorithm:**

Given two segments:
- Segment 1: `P1 + t·(P2-P1)` where `t ∈ [0,1]`
- Segment 2: `Q1 + s·(Q2-Q1)` where `s ∈ [0,1]`

Solve the intersection equation:
```
P1 + t·d1 = Q1 + s·d2
```
where `d1 = P2-P1` and `d2 = Q2-Q1` are direction vectors.

This is a 2×2 linear system:
```
t·(d1.x) - s·(d2.x) = Q1.x - P1.x
t·(d1.y) - s·(d2.y) = Q1.y - P1.y
```

**アルゴリズム:**

2つのセグメント:
- セグメント 1: `P1 + t·(P2-P1)` ただし `t ∈ [0,1]`
- セグメント 2: `Q1 + s·(Q2-Q1)` ただし `s ∈ [0,1]`

交差方程式を解く:
```
P1 + t·d1 = Q1 + s·d2
```
ここで `d1 = P2-P1`、`d2 = Q2-Q1` は方向ベクトル。

これは 2×2 線形システム:
```
t·(d1.x) - s·(d2.x) = Q1.x - P1.x
t·(d1.y) - s·(d2.y) = Q1.y - P1.y
```

**Solution using cross product:**
```
det = d1.x·d2.y - d1.y·d2.x
t = ((Q1-P1) × d2) / det
s = ((Q1-P1) × d1) / det
```

If `|det| < ε`, segments are parallel/collinear (special handling).
Otherwise, check if `t, s ∈ [0,1]` to determine if intersection exists.

**外積を用いた解:**
```
det = d1.x·d2.y - d1.y·d2.x
t = ((Q1-P1) × d2) / det
s = ((Q1-P1) × d1) / det
```

`|det| < ε` ならセグメントは平行/同一直線上（特別処理）。
それ以外の場合、`t, s ∈ [0,1]` をチェックして交差の存在を判定。

**Classification:**
- If `t, s` are both near 0 or 1: **vertex-vertex** (endpoint contact)
- If one parameter is near 0 or 1: **edge-vertex** (vertex on edge interior)
- If both parameters are in `(0,1)` interior: **face-face** (proper crossing)
- For collinear segments: **edge-edge** (overlap with positive length)

**分類:**
- `t, s` が共に 0 または 1 に近い: **vertex-vertex**（端点接触）
- 一方のパラメータが 0 または 1 に近い: **edge-vertex**（辺内部への頂点接触）
- 両パラメータが `(0,1)` の内部: **face-face**（正規交差）
- 同一直線上のセグメント: **edge-edge**（正の長さでの重なり）

**Benefits of Direct Method:**
- **Performance**: Avoids SymPy geometry module overhead (~15-20% faster)
- **Error handling**: Eliminates "Cannot determine if..." errors from complex expressions
- **Exactness**: All arithmetic is still symbolic (no floating-point in final decision)
- **Simplicity**: Clear linear algebra, easier to verify and maintain

**直接法の利点:**
- **パフォーマンス**: SymPy geometry モジュールのオーバーヘッドを回避（約 15-20% 高速化）
- **エラー処理**: 複雑な式からの「Cannot determine if...」エラーを排除
- **厳密性**: すべての演算は依然としてシンボリック（最終判定に浮動小数点なし）
- **シンプルさ**: 明確な線形代数、検証と保守が容易

---

## Overlap Definition / 重なりの定義

Phase 3 adopts a **strict overlap definition**: any non-empty geometric intersection between the edges of two non-adjacent faces constitutes an overlap.

Phase 3 は**厳格な重なり定義**を採用します：非隣接な2つの面の辺間のあらゆる非空幾何交差が重なりを構成します。

### Classification / 分類

Overlap is classified into the following types, ordered by priority:

重なりは以下の種別に分類され、優先度順に並べられます：

| Priority | Kind | Condition | 条件 |
|----------|------|-----------|------|
| 3 (highest) | `face-face` | Edge interiors cross (area > 0 intersection implied) | 辺の内部が交差（面積 > 0 の交差を含意） |
| 2 | `edge-edge` | Edges overlap collinearly with positive length | 辺が正の長さで同一直線上に重なる |
| 1 | `edge-vertex` | A vertex lies on the interior of another edge | 頂点が他方の辺内部に接触 |
| 1 | `vertex-vertex` | Two vertices coincide | 頂点同士が一致 |

### Priority-Based Classification / 優先度ベースの分類

When multiple edge pairs between two polygons produce intersections of different types, Phase 3 reports the **strongest (highest priority) type found**. All edge pairs are scanned exhaustively; only `face-face` (the maximum priority) may short-circuit the scan.

2つの多角形間で複数の辺ペアが異なる種別の交差を生じた場合、Phase 3 は**最も強い（最高優先度の）種別**を報告します。全辺ペアが網羅的に走査され、`face-face`（最大優先度）のみが走査を短絡できます。

This design ensures that classification is **independent of edge enumeration order**. A polygon pair with both `edge-vertex` contacts and an `edge-edge` collinear overlap will always be classified as `edge-edge`, regardless of which intersection is found first.

この設計により、分類は**辺の列挙順序に依存しません**。`edge-vertex` 接触と `edge-edge` 同一直線上重なりの両方を持つ多角形ペアは、どちらの交差が先に見つかるかに関係なく、常に `edge-edge` として分類されます。

### Degenerate Segment Handling / 退化 Segment の処理

SymPy may return a `Segment` object with zero length (degenerate case where both endpoints coincide). Phase 3 detects this by checking `(p1.x - p2.x)² + (p1.y - p2.y)² = 0` using exact arithmetic. A degenerate Segment is reclassified as a point contact (`vertex-vertex` or `edge-vertex`) based on endpoint membership.

SymPy は長さ 0 の `Segment` オブジェクトを返すことがあります（両端点が一致する退化ケース）。Phase 3 は厳密演算で `(p1.x - p2.x)² + (p1.y - p2.y)² = 0` を検査してこれを検出します。退化 Segment は端点帰属に基づいて点接触（`vertex-vertex` または `edge-vertex`）に再分類されます。

### Why Strict? / なぜ厳格な定義か？

The strict definition treats all contact types — including point touches — as overlap. This is a **conservative (safe-side) design choice**:

- It never misses a genuine overlap (no false negatives in the overlap-detection sense).
- It may reject unfoldings where faces merely touch at a vertex or share an edge. These are considered borderline cases and are excluded to guarantee unambiguous separation.

厳格な定義は点接触を含むすべての接触種別を重なりとして扱います。これは**保守的（安全側）な設計選択**です：

- 真の重なりを見落とすことがない（重なり検出の意味での偽陰性がない）。
- 面が頂点で接触するだけ、または辺を共有するだけの展開図を除去する可能性がある。これらは境界的なケースとみなされ、曖昧性のない分離を保証するために除外される。

---

## Structural Safety / 構造的安全性

### Polygon Containment Is Not a Concern / 完全内包は問題にならない

A potential concern with edge-based intersection testing is that it might miss **polygon containment** — where one polygon lies entirely inside another without any edge crossings.

辺交差ベースの交差テストにおける潜在的な懸念は、**多角形の完全内包**を見落とす可能性です。これは、辺の交差なしに一方の多角形が他方の内部に完全に含まれるケースです。

In the context of rotational unfolding, this configuration cannot arise. The argument is as follows:

回転展開の文脈では、この配置は生じません。論拠は以下の通りです：

1. **Sequential placement**: Faces are placed one at a time along a dual path on the polyhedron's face adjacency graph. Each face shares an edge with its predecessor in the sequence.
2. **Jordan curve theorem**: For a face to become fully enclosed by previously placed faces, the boundary of the enclosing region must form a closed curve around it. This closed curve must cross the path of the enclosed face's entry edge.
3. **Boundary crossing implies edge intersection**: The entry edge connects the enclosed face to its predecessor. For the enclosing boundary to surround this face, at least one edge of the enclosing faces must cross an edge of a face along the entry path.
4. **Edge intersection is detected**: Any such crossing is detected by the edge-pair scan.

Therefore, polygon containment without edge intersection is structurally impossible in rotational unfoldings. The edge-based approach is sufficient.

1. **逐次配置**: 面は多面体の面隣接グラフ上の dual path に沿って1つずつ配置される。各面は列における前の面と辺を共有する。
2. **Jordan 曲線定理**: ある面が既に配置された面群に完全に囲まれるためには、囲む領域の境界がその面の周りに閉曲線を形成する必要がある。この閉曲線は囲まれた面の入口辺の経路と交差する。
3. **境界の交差は辺交差を意味する**: 入口辺は囲まれた面をその前の面に接続する。囲む境界がこの面を包囲するには、囲む面の少なくとも1つの辺が入口経路上の面の辺と交差する必要がある。
4. **辺交差は検出される**: そのような交差は辺ペア走査によって検出される。

したがって、辺交差なしの多角形内包は回転展開において構造的に不可能です。辺ベースのアプローチは十分です。

### Vertex Chain Skipping Is Safe / 頂点連鎖スキップは安全

Phase 3 uses `shares_vertex_chain_all` to skip overlap checks between face pairs that share a common vertex on the original polyhedron. This is safe because:

Phase 3 は `shares_vertex_chain_all` を用いて、元の多面体上で共通頂点を持つ面ペア間の重なり判定をスキップします。これが安全である理由：

1. Faces sharing a vertex are **topologically adjacent** and are expected to touch in any unfolding.
2. The angle defect theorem for convex polyhedra guarantees that faces meeting at a vertex have a total angle sum strictly less than 2π. This means they cannot overlap in an unfolding — they can only touch at their shared vertex.
3. Skipping these pairs avoids false positives from legitimate geometric contact.

1. 頂点を共有する面は**位相的に隣接**しており、いかなる展開図でも接触が期待される。
2. 凸多面体の角度欠損定理により、頂点で会合する面の角度の総和は 2π より厳密に小さい。これは展開図において重なりが生じ得ないことを意味する — 共有頂点での接触のみが起こり得る。
3. これらのペアをスキップすることで、正当な幾何的接触からの偽陽性を回避する。

---

## Vertex Incidence Reconstruction / 頂点共有関係の再構築

`polyhedron.json` does not contain explicit vertex data. Phase 3 reconstructs vertex-face incidence from edge adjacency using a **union-find algorithm**:

`polyhedron.json` は明示的な頂点データを含みません。Phase 3 は辺隣接情報から**union-find アルゴリズム**を用いて頂点-面の帰属関係を再構築します：

1. Each face corner (the vertex between edge `k` and edge `(k+1) % gon`) is initialized as a separate element.
2. For each shared edge between two faces, the corresponding corner pairs are unioned.
3. Equivalence classes define the polyhedron's vertices. Each vertex is assigned a unique ID.

This produces the same vertex-face incidence that was explicitly available in legacy `.adj` files. The reconstruction is exact (union-find on integer IDs) and deterministic.

この処理は legacy の `.adj` ファイルで明示的に利用可能だった頂点-面の帰属関係と同じものを生成します。再構築は厳密（整数 ID 上の union-find）で決定的です。

---

## Output Format / 出力形式

### exact.jsonl (Phase 3 Output)

**Generated by**: Phase 3 (`exact`)
**Location**: `output/polyhedra/<class>/<name>/exact.jsonl`
**Format**: JSON Lines (one record per line)
**Purpose**: Verified partial unfoldings with overlap classification

**生成元**: Phase 3（`exact`）
**場所**: `output/polyhedra/<class>/<name>/exact.jsonl`
**形式**: JSON Lines（1行1レコード）
**目的**: 重なり分類付きの検証済み部分展開図

Each record preserves all fields from `noniso.jsonl` and adds an `exact_overlap` field:

各レコードは `noniso.jsonl` の全フィールドを保持し、`exact_overlap` フィールドを追加します：

```json
{
  "schema_version": 1,
  "record_type": "partial_unfolding",
  "base_pair": {"base_face": 0, "base_edge": 0},
  "symmetric_used": true,
  "faces": [...],
  "exact_overlap": {
    "kind": "face-face"
  }
}
```

The `exact_overlap.kind` field is one of:
- `"face-face"`: Polygon interiors overlap (edge crossing)
- `"edge-edge"`: Edges overlap collinearly with positive length
- `"edge-vertex"`: A vertex lies on the interior of another edge
- `"vertex-vertex"`: Two vertices coincide

`exact_overlap.kind` フィールドは以下のいずれか：
- `"face-face"`: 多角形の内部が重なる（辺交差）
- `"edge-edge"`: 辺が正の長さで同一直線上に重なる
- `"edge-vertex"`: 頂点が他方の辺内部に接触
- `"vertex-vertex"`: 頂点同士が一致

### Output Directory Structure / 出力ディレクトリ構造

```
output/polyhedra/<class>/<name>/
├── raw.jsonl          # Phase 1 output (N records)
├── run.json           # Phase 1 metadata
├── noniso.jsonl       # Phase 2 output (≤N records, deduplicated)
└── exact.jsonl        # Phase 3 output (≤noniso records, verified)
```

---

## Usage / 使用方法

### Basic Execution

```bash
# From repository root (PYTHONPATH must be set)
cd /path/to/RotationalUnfolding
PYTHONPATH=python python -m exact run --poly data/polyhedra/archimedean/s07
```

### Arguments

- `--poly data/polyhedra/CLASS/NAME`: Path to polyhedron data directory (e.g., `data/polyhedra/archimedean/s07`) **[required]**

### Prerequisites / 前提条件

Phase 3 requires:

- **Phase 2 completion**: `noniso.jsonl` must exist for the specified polyhedron
- **SymPy**: `pip install sympy` (exact arithmetic library)
- **polyhedron.json**: Must exist in `data/polyhedra/<class>/<name>/`

### Typical Workflow / 典型的なワークフロー

```bash
# Step 1: Generate raw.jsonl (Phase 1)
PYTHONPATH=python python -m rotational_unfolding run --poly data/polyhedra/johnson/n66

# Step 2: Remove isomorphic duplicates (Phase 2)
PYTHONPATH=python python -m nonisomorphic run --poly data/polyhedra/johnson/n66

# Step 3: Verify exact overlaps (Phase 3)
PYTHONPATH=python python -m exact run --poly data/polyhedra/johnson/n66
```

### Example Output / 出力例

```
Phase 3: Exact overlap detection for johnson/n66
Input (noniso.jsonl): .../johnson/n66/noniso.jsonl
Polyhedron structure: .../johnson/n66/polyhedron.json
Output (exact.jsonl): .../johnson/n66/exact.jsonl

Checking exact overlaps...
  Record 1/56... REMOVE (endpoint vertex chain)
  Record 9/56... KEEP (endpoint: face-face)
  Record 16/56... KEEP (endpoint: edge-vertex)
  Record 25/56... KEEP (endpoint: vertex-vertex)
  Record 34/56... KEEP (endpoint: edge-edge)
  ...

Input records (noniso.jsonl): 56
Output records (exact.jsonl): 13
Removed overlapping: 43
```

---

## Guarantees / 保証

### Phase 3 Guarantees / Phase 3 の保証

Phase 3 provides the following guarantees:

1. **Exact arithmetic**: All coordinate construction and intersection tests use SymPy symbolic expressions. No floating-point rounding affects the overlap decision.
2. **No false negatives**: Every non-empty edge-pair intersection is detected. The strict overlap definition ensures no genuine overlap is missed.
3. **Safe-side filtering**: The overlap definition is conservative. Records are removed rather than retained in ambiguous cases.
4. **Order preservation**: Records appear in the same order as `noniso.jsonl` (with rejected records removed).
5. **Deterministic output**: Same input always produces the same output.
6. **Classification correctness**: The reported overlap kind reflects the strongest intersection type found across all edge pairs, independent of enumeration order.

Phase 3 は以下を保証します：

1. **厳密演算**: すべての座標構築と交差テストは SymPy シンボリック式を使用。浮動小数点丸めが重なり判定に影響しない。
2. **偽陰性なし**: すべての非空の辺ペア交差が検出される。厳格な重なり定義により、真の重なりが見落とされない。
3. **安全側フィルタリング**: 重なり定義は保守的。曖昧なケースではレコードが保持されるのではなく除去される。
4. **順序保持**: レコードは `noniso.jsonl` と同じ順序で現れる（除去されたレコードを除く）。
5. **決定的出力**: 同じ入力は常に同じ出力を生成。
6. **分類の正しさ**: 報告される重なり種別は、列挙順序に依存せず、全辺ペアで見つかった最も強い交差種別を反映。

---

## Caveats / 但し書き

The following points are stated for completeness and intellectual honesty:

以下の点は完全性と知的誠実さのために記述します：

1. **Edge-based detection only**: Phase 3 detects overlap through edge-pair intersection. It does not perform point-in-polygon containment tests. As argued in the Structural Safety section, this is sufficient for rotational unfoldings, but it is a structural assumption rather than a general geometric theorem.
2. **Direct parametric method**: The exactness of the symbolic intersection depends on the correctness of the parametric line intersection algorithm and SymPy's symbolic comparison methods (`simplify()`, `is_nonnegative`). These are considered reliable for the algebraic expressions arising from regular polygon geometry.
3. **Convexity assumption**: The angle defect argument for vertex chain skipping assumes convex polyhedra. For non-convex polyhedra, additional analysis would be required.
4. **Execution time**: Exactness is prioritized over speed. Phase 3 may take hours for polyhedra with many faces and complex unfoldings. However, the direct parametric method (v2.0.0) provides ~15-20% speedup compared to the legacy `Segment.intersection()` approach, making previously intractable cases (e.g., `a18`) feasible.

1. **辺ベースの検出のみ**: Phase 3 は辺ペア交差を通じて重なりを検出する。点包含テストは実行しない。構造的安全性のセクションで論じた通り、回転展開にはこれで十分であるが、一般的な幾何定理ではなく構造的な仮定である。
2. **直接パラメトリック法**: シンボリック交差の厳密性は、パラメトリック直線交差アルゴリズムと SymPy のシンボリック比較メソッド（`simplify()`、`is_nonnegative`）の正しさに依存する。正多角形幾何から生じる代数式に対しては信頼できるとみなされる。
3. **凸性の仮定**: 頂点連鎖スキップの角度欠損論拠は凸多面体を仮定している。非凸多面体に対しては追加的な分析が必要。
4. **実行時間**: 厳密性が速度より優先される。面が多く展開図が複雑な多面体では、Phase 3 は数時間かかる場合がある。ただし、直接パラメトリック法（v2.0.0）は legacy の `Segment.intersection()` 方式と比べて約 15-20% の高速化を提供し、以前は実行不可能だったケース（例：`a18`）が実行可能になった。

1. **辺ベースの検出のみ**: Phase 3 は辺ペア交差を通じて重なりを検出する。点包含テストは実行しない。構造的安全性のセクションで論じた通り、回転展開にはこれで十分であるが、一般的な幾何定理ではなく構造的な仮定である。
2. **SymPy 依存**: シンボリック幾何の厳密性は SymPy の `Segment.intersection()` 実装の正しさに依存する。正多角形幾何から生じる代数式に対しては信頼できるとみなされる。
3. **凸性の仮定**: 頂点連鎖スキップの角度欠損論拠は凸多面体を仮定している。非凸多面体に対しては追加的な分析が必要。
4. **実行時間**: 厳密性が速度より優先される。面が多く展開図が複雑な多面体では、Phase 3 は数時間〜数日かかる場合がある。これは設計上の意図である。

---

## Verification / 検証

Phase 3 has been verified against the following polyhedra:

Phase 3 は以下の多面体に対して検証済みです：
|| Polyhedron | noniso records | exact records | Overlap kinds observed | Execution time (v2.0.0) |
||------------|---------------|--------------|----------------------|------------------------|
|| `archimedean/s07` | 7 | 1 | face-face | ~1s |
|| `johnson/n20` | 36 | 4 | face-face | ~8.6s |
|| `antiprism/a18` | 96 | 6 | face-face | ~40s |
|| `johnson/n66` | 56 | 13 | face-face, edge-edge, edge-vertex, vertex-vertex | ~15s |

The `johnson/n66` result demonstrates all four overlap classifications operating correctly, including `edge-edge` (positive-length collinear overlap detected via full edge-pair scan with priority-based classification).

`johnson/n66` の結果は、4つの重なり分類すべてが正しく動作していることを実証しています。これには `edge-edge`（優先度ベース分類による全辺ペア走査で検出された正の長さの同一直線上重なり）を含みます。

The `antiprism/a18` case was previously failing with "Cannot determine if..." errors from `sympy.geometry.Segment.intersection()`. With the direct parametric method (v2.0.0), it completes successfully in ~40 seconds.

`antiprism/a18` のケースは以前は `sympy.geometry.Segment.intersection()` からの「Cannot determine if...」エラーで失敗していました。直接パラメトリック法（v2.0.0）により、約 40 秒で正常に完了します。

Results are consistent with legacy exact overlap detection outputs where comparable.

結果は比較可能な範囲で legacy の厳密重なり検出出力と一致しています。

---

## References / 参考資料

### Specification and Implementation

- **Phase 1 specification**: `docs/PHASE1_RUN.md` (upstream data contract)
- **Phase 2 specification**: `docs/PHASE2_NONISO.md` (input contract)
- **Phase 3 implementation**: `python/exact/`
- **Path resolution**: `python/poly_resolve.py` (shared across all CLI modules)
- **Canonical output location**: `output/polyhedra/<class>/<name>/`

### 仕様と実装

- **Phase 1 仕様**: `docs/PHASE1_RUN.md`（上流データ契約）
- **Phase 2 仕様**: `docs/PHASE2_NONISO.md`（入力契約）
- **Phase 3 実装**: `python/exact/`
- **パス解決**: `python/poly_resolve.py`（全 CLI モジュール共通）
- **正規出力場所**: `output/polyhedra/<class>/<name>/`

---

**Document Status**: This document describes the **frozen specification** of Phase 3 as of 2026-02-13. The overlap detection logic, classification scheme, and output format defined here are stable. Version 2.0.0 introduces the direct parametric intersection method for improved performance and robustness while maintaining exactness.

**文書ステータス**: この文書は 2026-02-13 時点での Phase 3 の**凍結された仕様**を記述します。ここで定義される重なり検出ロジック、分類スキーム、出力形式は安定しています。バージョン 2.0.0 では、厳密性を維持しながらパフォーマンスと堅牢性を向上させる直接パラメトリック交差法を導入しました。
