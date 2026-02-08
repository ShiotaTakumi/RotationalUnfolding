# Drawing Utility

Visualization utility for rotational unfolding JSONL outputs.

This is a **verification utility**, not a Phase output.

## Usage

```bash
PYTHONPATH=reorg/python python -m drawing run --type <type> --poly polyhedra/<class>/<name>
```

### Arguments

- `--type`: Output type to visualize
  - `raw`: Phase 1 output (raw.jsonl)
  - `noniso`: Phase 2 output (noniso.jsonl)
  - `exact`: Phase 3 output (exact.jsonl) — labels hidden
- `--poly`: Polyhedron path (e.g., `polyhedra/archimedean/s07`)

## Examples

```bash
# Draw SVG files for raw output of archimedean/s07
PYTHONPATH=reorg/python python -m drawing run --type raw --poly polyhedra/archimedean/s07

# Draw SVG files for noniso output of johnson/n20
PYTHONPATH=reorg/python python -m drawing run --type noniso --poly polyhedra/johnson/n20

# Draw SVG files for exact output (no labels)
PYTHONPATH=reorg/python python -m drawing run --type exact --poly polyhedra/johnson/n66
```

## Output

- Input JSONL: `reorg/output/polyhedra/<class>/<name>/<type>.jsonl`
- Output directory: `reorg/output/polyhedra/<class>/<name>/draw/<type>/`
- One SVG file per record in JSONL
- SVG files are for visual inspection and verification

## Dependencies

Standard library only (no additional dependencies required).
