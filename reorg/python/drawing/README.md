# Drawing Utility

Visualization utility for rotational unfolding JSONL outputs.

This is a **verification utility**, not a Phase output.

## Usage

```bash
PYTHONPATH=reorg/python python -m drawing run --type <type> --poly polyhedra/<class>/<name> [--no-labels]
```

### Arguments

- `--type`: Output type to visualize
  - `raw`: Phase 1 output (raw.jsonl)
  - `noniso`: Phase 2 output (noniso.jsonl)
  - `exact`: Phase 3 output (exact.jsonl)
- `--poly`: Polyhedron path (e.g., `polyhedra/archimedean/s07`)
- `--no-labels`: Hide face and edge labels (draw polygons only). Default: labels displayed.

## Examples

```bash
# Draw SVG files for raw output (with labels, default)
PYTHONPATH=reorg/python python -m drawing run --type raw --poly polyhedra/archimedean/s07

# Draw SVG files for noniso output (with labels, default)
PYTHONPATH=reorg/python python -m drawing run --type noniso --poly polyhedra/johnson/n20

# Draw SVG files for exact output (with labels, default)
PYTHONPATH=reorg/python python -m drawing run --type exact --poly polyhedra/johnson/n66

# Draw SVG files without labels (polygons only)
PYTHONPATH=reorg/python python -m drawing run --type exact --poly polyhedra/johnson/n66 --no-labels
```

## Output

- Input JSONL: `reorg/output/polyhedra/<class>/<name>/<type>.jsonl`
- Output directory: `reorg/output/polyhedra/<class>/<name>/draw/<type>/`
- One SVG file per record in JSONL
- SVG files are for visual inspection and verification

## Dependencies

Standard library only (no additional dependencies required).
