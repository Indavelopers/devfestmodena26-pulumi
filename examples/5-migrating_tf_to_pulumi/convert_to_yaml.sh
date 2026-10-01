#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_DIR="${SCRIPT_DIR}/../2-terraform"
TARGET_DIR="${SCRIPT_DIR}"

echo "================================================================="
echo " Converting Terraform (examples/2-terraform) to Pulumi YAML      "
echo "================================================================="
echo " Source directory : ${SOURCE_DIR}"
echo " Target directory : ${TARGET_DIR}"
echo "================================================================="

pulumi convert \
    --from terraform \
    --cwd "${SOURCE_DIR}" \
    --language yaml \
    --out "${TARGET_DIR}"

echo "Post-processing generated Pulumi YAML for clean GCP stack configuration..."

# 1. Update project name in Pulumi.yaml
cat << 'EOF' > "${TARGET_DIR}/Pulumi.yaml"
name: migrating-tf-to-pulumi
runtime: yaml
description: Migrating Terraform to Pulumi YAML
EOF

# 2. Update Main.yaml to use modern config and bind project/region to gcp provider config
python3 -c "
with open('${TARGET_DIR}/Main.yaml') as f:
    content = f.read()

# Replace deprecated configuration block with modern config for zone
if 'configuration:' in content:
    idx_start = content.find('configuration:')
    idx_end = content.find('resources:')
    modern_config = 'config:\n  zone:\n    type: string\n    default: \"\"\n'
    content = content[:idx_start] + modern_config + content[idx_end:]

# Bind project and region variables to gcp:project and gcp:region
if 'variables:' in content and 'project: \${gcp:project}' not in content:
    content = content.replace('variables:\n', 'variables:\n  project: \${gcp:project}\n  region: \${gcp:region}\n')

with open('${TARGET_DIR}/Main.yaml', 'w') as f:
    f.write(content)
"

echo ""
echo "================================================================="
echo " Conversion Completed Successfully!                              "
echo " Check generated Pulumi.yaml and Main.yaml in ${TARGET_DIR}      "
echo "================================================================="
