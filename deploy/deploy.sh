#!/bin/bash

set -e

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
CHART_DIR="${SCRIPT_DIR}/f5-ai-security"
VALUES_FILE="${SCRIPT_DIR}/f5-ai-security-values.yaml"
EXAMPLE_FILE="${SCRIPT_DIR}/f5-ai-security-values.yaml.example"

# Check if values file exists, if not copy from example
if [ ! -f "${VALUES_FILE}" ]; then
    echo "Values file not found. Copying from example..."
    cp "${EXAMPLE_FILE}" "${VALUES_FILE}"
    echo "Created ${VALUES_FILE}"
    echo "Please edit this file to configure your deployment (API keys, model selection, etc.)"
    echo ""
fi

# Check if at least one model is enabled
echo "Checking if at least one model is enabled..."
MODEL_ENABLED=$(grep -A 1 "enabled:" "${VALUES_FILE}" | grep -c "enabled: true" || true)

if [ "$MODEL_ENABLED" -eq 0 ]; then
    echo "ERROR: No models are enabled in ${VALUES_FILE}"
    echo "Please enable at least one model under global.models by setting 'enabled: true'"
    echo "Example models available:"
    echo "  - llama-3-2-1b-instruct"
    echo "  - llama-3-1-8b-instruct"
    echo "  - llama-3-2-3b-instruct"
    echo "  - llama-3-3-70b-instruct"
    exit 1
fi

echo "Found ${MODEL_ENABLED} enabled model(s)"

echo "Updating Helm dependencies..."
helm dependency update "${CHART_DIR}"

echo "Creating OpenShift project f5-ai-security..."
oc new-project f5-ai-security || echo "Project already exists, continuing..."

echo "Installing f5-ai-security Helm chart with custom values..."
helm install f5-ai-security "${CHART_DIR}" -f "${VALUES_FILE}" -n f5-ai-security

echo "Deployment complete!"