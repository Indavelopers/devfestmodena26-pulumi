# GCP Infrastructure Provisioning via Bash & gcloud CLI

This directory contains shell scripts to provision GCP infrastructure using the `gcloud` CLI.

## Resources Created

1. **Custom Mode VPC Network**: `custom-vpc` (subnet mode: custom)
2. **Subnet**: `custom-subnet` (`10.0.1.0/24`) in the specified region
3. **Firewall Rules**:
   - `custom-vpc-allow-ssh`: Allows SSH (port 22) from anywhere (`0.0.0.0/0`)
   - `custom-vpc-allow-internal`: Allows internal TCP/UDP/ICMP traffic within `10.0.1.0/24`
   - `custom-vpc-allow-icmp`: Allows ICMP ping from anywhere (`0.0.0.0/0`)
4. **3 VM Instances**: `vm-instance-1`, `vm-instance-2`, `vm-instance-3` (`e2-micro`, Debian 12)
5. **GCS Storage Bucket**: `<PROJECT_ID>-infra-bucket` with uniform bucket-level access enabled

## Usage

### Prerequisites

- GCP account with billing enabled
- `gcloud` CLI installed and authenticated (`gcloud auth login`)

### Provision Infrastructure

```bash
./create_infra.sh <PROJECT_ID> <REGION>
```

Example:

```bash
./create_infra.sh my-gcp-project-id europe-west1
```

### Clean Up Infrastructure

```bash
./destroy_infra.sh <PROJECT_ID> <REGION>
```
