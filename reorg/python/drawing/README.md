# Drawing Utility

Visualization utility for rotational unfolding JSONL outputs.

This is a **verification utility**, not a Phase output.

## Usage

```bash
PYTHONPATH=reorg/python python -m drawing run --type <type> --poly <class>/<name>
```

### Arguments

- `--type`: Output type to visualize
  - `raw`: Phase 1 output (raw.jsonl)
  - `noniso`: Phase 2 output (noniso.jsonl) - Not yet implemented
  - `exact`: Phase 3 output (exact.jsonl) - Not yet implemented
- `--poly`: Polyhedron identifier in `CLASS/NAME` format (e.g., `archimedean/s07`)

## Examples

```bash
# Draw SVG files for raw output of archimedean/s07
PYTHONPATH=reorg/python python -m drawing run --type raw --poly archimedean/s07

# Draw SVG files for raw output of johnson/n20
PYTHONPATH=reorg/python python -m drawing run --type raw --poly johnson/n20

# Future: Draw noniso output (not yet implemented)
PYTHONPATH=reorg/python python -m drawing run --type noniso --poly platonic/r01
```

## Output

- Input JSONL: `reorg/output/polyhedra/<class>/<name>/<type>.jsonl`
- Output directory: `reorg/output/polyhedra/<class>/<name>/draw/<type>/`
- One SVG file per record in JSONL
- Filename: `000000.svg`, `000001.svg`, ... (6-digit zero-padded, 0-based index)
- SVG files are suitable for visual inspection and verification

## Dependencies

Standard library only (no additional dependencies required).
