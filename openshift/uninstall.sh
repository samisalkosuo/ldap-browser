#!/bin/bash

# Uninstall script for LDAP Browser on OpenShift
# Deletes YAML files in reverse order based on their numeric prefix

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Uninstalling LDAP Browser from OpenShift..."
echo "===================================================="
echo ""

# Get all YAML files starting with numbers, sorted numerically in reverse
mapfile -t YAML_FILES < <(find "$SCRIPT_DIR" -maxdepth 1 -type f -name '[0-9][0-9]-*.yaml' | sort -Vr)

if [ ${#YAML_FILES[@]} -eq 0 ]; then
    echo "Error: No YAML files found matching pattern [0-9][0-9]-*.yaml"
    exit 1
fi

# Delete each YAML file in reverse order
for yaml_file in "${YAML_FILES[@]}"; do
    filename=$(basename "$yaml_file")
    echo "Deleting resources from $filename..."
    oc delete -f "$yaml_file" --ignore-not-found=true
    
    if [ $? -eq 0 ]; then
        echo "✓ Successfully deleted resources from $filename"
    else
        echo "✗ Failed to delete resources from $filename"
        exit 1
    fi
    echo ""
done

echo "===================================================="
echo "Uninstallation complete!"
echo ""
echo "To verify removal, run:"
echo "  oc get all -n ldap-browser"
echo "  oc get namespace ldap-browser"

# Made with Bob
