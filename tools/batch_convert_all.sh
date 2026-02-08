#!/bin/bash
# ============================================================================
# batch_convert_all.sh
# ============================================================================
#
# Converts all legacy polyhedron data (.adj + .base) to JSON format.
# すべての legacy 多面体データ (.adj + .base) を JSON 形式に変換する。
#
# Usage:
#   bash batch_convert_all.sh
#
# ============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
CONVERTER="$SCRIPT_DIR/convert_legacy_input.py"

LEGACY_POLY_DIR="$REPO_ROOT/polyhedron"
OUTPUT_BASE_DIR="$REPO_ROOT/data/polyhedra"

# Statistics
TOTAL_SUCCESS=0
TOTAL_FAILED=0

echo "========================================"
echo "Batch conversion: legacy -> JSON"
echo "========================================"
echo ""

# Process each class
for CLASS_DIR in "$LEGACY_POLY_DIR"/*; do
    if [ ! -d "$CLASS_DIR" ]; then
        continue
    fi
    
    CLASS_NAME=$(basename "$CLASS_DIR")
    ADJACENT_DIR="$CLASS_DIR/adjacent"
    BASE_DIR="$CLASS_DIR/base"
    
    if [ ! -d "$ADJACENT_DIR" ] || [ ! -d "$BASE_DIR" ]; then
        echo "Warning: Skipping $CLASS_NAME (missing adjacent or base directory)"
        continue
    fi
    
    echo "Processing class: $CLASS_NAME"
    
    CLASS_SUCCESS=0
    CLASS_FAILED=0
    
    # Process each .adj file
    for ADJ_FILE in "$ADJACENT_DIR"/*.adj; do
        if [ ! -f "$ADJ_FILE" ]; then
            continue
        fi
        
        POLY_NAME=$(basename "$ADJ_FILE" .adj)
        BASE_FILE="$BASE_DIR/${POLY_NAME}.base"
        
        if [ ! -f "$BASE_FILE" ]; then
            echo "  ERROR: Missing base file for $POLY_NAME"
            CLASS_FAILED=$((CLASS_FAILED + 1))
            continue
        fi
        
        OUTPUT_DIR="$OUTPUT_BASE_DIR/$CLASS_NAME/$POLY_NAME"
        
        # Run the converter
        if python3 "$CONVERTER" "$ADJ_FILE" "$BASE_FILE" "$OUTPUT_DIR" > /dev/null 2>&1; then
            CLASS_SUCCESS=$((CLASS_SUCCESS + 1))
        else
            echo "  ERROR: Conversion failed for $POLY_NAME"
            CLASS_FAILED=$((CLASS_FAILED + 1))
        fi
    done
    
    echo "  -> Converted: $CLASS_SUCCESS, Failed: $CLASS_FAILED"
    echo ""
    
    TOTAL_SUCCESS=$((TOTAL_SUCCESS + CLASS_SUCCESS))
    TOTAL_FAILED=$((TOTAL_FAILED + CLASS_FAILED))
done

echo "========================================"
echo "Summary"
echo "========================================"
echo "Total converted: $TOTAL_SUCCESS"
echo "Total failed: $TOTAL_FAILED"
echo ""
echo "Done."
