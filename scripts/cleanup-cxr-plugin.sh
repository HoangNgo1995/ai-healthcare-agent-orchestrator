#!/bin/bash
# Script to clean up CxrReportGen plugin files when migrating to GPT-4o Vision
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

set -e

echo "=========================================="
echo "CxrReportGen Plugin Cleanup Script"
echo "=========================================="
echo ""

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Project root: $PROJECT_ROOT"
echo ""

# Remove the plugin file
PLUGIN_FILE="$PROJECT_ROOT/src/scenarios/default/tools/cxr_report_gen.py"
if [ -f "$PLUGIN_FILE" ]; then
    echo "✅ Removing cxr_report_gen.py..."
    rm "$PLUGIN_FILE"
    echo "   Deleted: $PLUGIN_FILE"
else
    echo "⚠️  Plugin file not found (already removed?): $PLUGIN_FILE"
fi

# Remove test notebook
NOTEBOOK_FILE="$PROJECT_ROOT/notebooks/tests/cxr_report_gen.ipynb"
if [ -f "$NOTEBOOK_FILE" ]; then
    echo "✅ Removing cxr_report_gen.ipynb..."
    rm "$NOTEBOOK_FILE"
    echo "   Deleted: $NOTEBOOK_FILE"
else
    echo "⚠️  Test notebook not found (already removed?): $NOTEBOOK_FILE"
fi

echo ""
echo "=========================================="
echo "Cleanup Complete!"
echo "=========================================="
echo ""
echo "Next steps to fully migrate to GPT-4o Vision:"
echo ""
echo "1. Comment out HLS model deployment in infra/main.bicep:"
echo "   // module m_hlsModel 'modules/hlsModel.bicep' = {"
echo "   //   ..."
echo "   // }"
echo ""
echo "2. Update the outputs in infra/main.bicep:"
echo "   var outHlsModelEndpoints = []  // was: m_hlsModel.outputs.modelEndpoints"
echo ""
echo "3. Deploy changes to remove GPU resources:"
echo "   azd up"
echo ""
echo "4. Verify the new radiology_vision plugin is working:"
echo "   jupyter notebook notebooks/tests/radiology_vision.ipynb"
echo ""
echo "Estimated monthly savings: $2,000-3,000 USD"
echo "=========================================="
