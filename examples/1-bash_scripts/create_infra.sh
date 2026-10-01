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

# Resource configuration parameters
VPC_NAME="custom-vpc"
SUBNET_NAME="custom-subnet"
SUBNET_CIDR="10.0.1.0/24"
BUCKET_NAME="${PROJECT_ID}-infra-bucket"

echo "=================================================="
echo " Starting Infrastructure Creation via gcloud CLI "
echo "=================================================="
echo " Project ID : ${PROJECT_ID}"
echo " Region     : ${REGION}"
echo " Zone       : ${ZONE}"
echo "=================================================="

# 1. Create a custom mode VPC network
echo "--> Creating Custom Mode VPC network: ${VPC_NAME}..."
gcloud compute networks create "${VPC_NAME}" \
    --project="${PROJECT_ID}" \
    --subnet-mode=custom \
    --bgp-routing-mode=regional

# 2. Create a Subnet in the specified region
echo "--> Creating Subnet: ${SUBNET_NAME} (${SUBNET_CIDR}) in ${REGION}..."
gcloud compute networks subnets create "${SUBNET_NAME}" \
    --project="${PROJECT_ID}" \
    --network="${VPC_NAME}" \
    --region="${REGION}" \
    --range="${SUBNET_CIDR}"

# 3. Create proposed Firewall Rules
echo "--> Creating Firewall Rule: allow-ssh..."
gcloud compute firewall-rules create "${VPC_NAME}-allow-ssh" \
    --project="${PROJECT_ID}" \
    --network="${VPC_NAME}" \
    --allow=tcp:22 \
    --source-ranges="0.0.0.0/0" \
    --description="Allow SSH access from anywhere"

echo "--> Creating Firewall Rule: allow-internal..."
gcloud compute firewall-rules create "${VPC_NAME}-allow-internal" \
    --project="${PROJECT_ID}" \
    --network="${VPC_NAME}" \
    --allow=tcp,udp,icmp \
    --source-ranges="${SUBNET_CIDR}" \
    --description="Allow internal traffic within the subnet"

echo "--> Creating Firewall Rule: allow-icmp..."
gcloud compute firewall-rules create "${VPC_NAME}-allow-icmp" \
    --project="${PROJECT_ID}" \
    --network="${VPC_NAME}" \
    --allow=icmp \
    --source-ranges="0.0.0.0/0" \
    --description="Allow ICMP ping from anywhere"

# 4. Create 3 VM Instances
echo "--> Creating 3 VM instances (vm-instance-1, vm-instance-2, vm-instance-3) in ${ZONE}..."
gcloud compute instances create vm-instance-1 vm-instance-2 vm-instance-3 \
    --project="${PROJECT_ID}" \
    --zone="${ZONE}" \
    --machine-type="e2-micro" \
    --subnet="${SUBNET_NAME}" \
    --image-family="debian-12" \
    --image-project="debian-cloud"

# 5. Create a Google Cloud Storage Bucket
echo "--> Creating GCS Bucket: gs://${BUCKET_NAME} in ${REGION}..."
gcloud storage buckets create "gs://${BUCKET_NAME}" \
    --project="${PROJECT_ID}" \
    --location="${REGION}" \
    --uniform-bucket-level-access

echo "=================================================="
echo " Infrastructure Creation Completed Successfully! "
echo "=================================================="
