# Drawing Utility

Visualization utility for `raw.jsonl` records.

This is a **verification utility**, not a Phase output.

## Usage

```bash
python reorg/python/drawing/draw_raw_jsonl.py \
    --input <path/to/raw.jsonl> \
    --outdir <output/directory>
```

## Example

```bash
# Draw SVG files for archimedean/s07
python reorg/python/drawing/draw_raw_jsonl.py \
    --input reorg/output/polyhedra/archimedean/s07/raw.jsonl \
    --outdir reorg/output/polyhedra/archimedean/s07/draw/raw
```

## Output

- One SVG file per record in `raw.jsonl`
- Filename: `000000.svg`, `000001.svg`, ... (0-based index, zero-padded)
- SVG files are suitable for visual inspection and verification

## Dependencies

Standard library only (no additional dependencies required).
