#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status,
# treat unset variables as an error, and fail pipelines on first error.
set -euo pipefail

# Check for required arguments
if [ "$#" -ne 2 ]; then
    echo "Error: Missing required arguments."
    echo "Usage: $0 <PROJECT_ID> <REGION>"
    echo "Example: $0 my-gcp-project europe-west1"
    exit 1
fi

PROJECT_ID="$1"
REGION="$2"
ZONE="${REGION}-a"

VPC_NAME="custom-vpc"
SUBNET_NAME="custom-subnet"
BUCKET_NAME="${PROJECT_ID}-infra-bucket"

echo "=================================================="
echo " Starting Infrastructure Cleanup via gcloud CLI  "
echo "=================================================="
echo " Project ID : ${PROJECT_ID}"
echo " Region     : ${REGION}"
echo " Zone       : ${ZONE}"
echo "=================================================="

# 1. Delete GCS Bucket
echo "--> Deleting GCS Bucket: gs://${BUCKET_NAME}..."
gcloud storage rm --recursive "gs://${BUCKET_NAME}" --project="${PROJECT_ID}" || true

# 2. Delete VM Instances
echo "--> Deleting VM instances (vm-instance-1, vm-instance-2, vm-instance-3)..."
gcloud compute instances delete vm-instance-1 vm-instance-2 vm-instance-3 \
    --project="${PROJECT_ID}" \
    --zone="${ZONE}" \
    --quiet || true

# 3. Delete Firewall Rules
echo "--> Deleting Firewall Rules..."
gcloud compute firewall-rules delete \
    "${VPC_NAME}-allow-ssh" \
    "${VPC_NAME}-allow-internal" \
    "${VPC_NAME}-allow-icmp" \
    --project="${PROJECT_ID}" \
    --quiet || true

# 4. Delete Subnet
echo "--> Deleting Subnet: ${SUBNET_NAME}..."
gcloud compute networks subnets delete "${SUBNET_NAME}" \
    --project="${PROJECT_ID}" \
    --region="${REGION}" \
    --quiet || true

# 5. Delete Custom Mode VPC Network
echo "--> Deleting Custom Mode VPC network: ${VPC_NAME}..."
gcloud compute networks delete "${VPC_NAME}" \
    --project="${PROJECT_ID}" \
    --quiet || true

echo "=================================================="
echo " Infrastructure Cleanup Completed Successfully!  "
echo "=================================================="
