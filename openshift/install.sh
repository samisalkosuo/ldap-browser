#!/bin/bash

# Install script for LDAP Browser on OpenShift
# Applies YAML files in order based on their numeric prefix

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Installing LDAP Browser to OpenShift..."
echo "================================================"
echo ""

# Get all YAML files starting with numbers, sorted numerically
mapfile -t YAML_FILES < <(find "$SCRIPT_DIR" -maxdepth 1 -type f -name '[0-9][0-9]-*.yaml' | sort -V)

if [ ${#YAML_FILES[@]} -eq 0 ]; then
    echo "Error: No YAML files found matching pattern [0-9][0-9]-*.yaml"
    exit 1
fi

# Apply each YAML file in order
for yaml_file in "${YAML_FILES[@]}"; do
    filename=$(basename "$yaml_file")
    echo "Applying $filename..."
    oc apply -f "$yaml_file"
    
    if [ $? -eq 0 ]; then
        echo "✓ Successfully applied $filename"
    else
        echo "✗ Failed to apply $filename"
        exit 1
    fi
    echo ""
done

echo "================================================"
echo "Installation complete!"
echo ""
echo "To check the deployment status, run:"
echo "  oc get all -n ldap-browser"
echo ""
echo "To view logs, run:"
echo "  oc logs -f deployment/ldap-browser -n ldap-browser"

# Made with Bob
