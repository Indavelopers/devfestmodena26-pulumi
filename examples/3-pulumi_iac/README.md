# GCP Infrastructure Provisioning via Pulumi (Python)

This directory contains a Pulumi Python project translating the Terraform infrastructure defined in `examples/2-terraform` (and the bash script in `examples/1-bash_scripts`.

## Resources Created

1. **Custom Mode VPC Network**: `custom-vpc` (routing mode: regional)
2. **Subnet**: `custom-subnet` (`10.0.1.0/24`) in the target region
3. **Firewall Rules**:
   - `custom-vpc-allow-ssh`: Allows SSH (port 22) from `0.0.0.0/0`
   - `custom-vpc-allow-internal`: Allows internal TCP/UDP/ICMP traffic within `10.0.1.0/24`
   - `custom-vpc-allow-icmp`: Allows ICMP ping from `0.0.0.0/0`
4. **3 VM Instances**: `vm-instance-1`, `vm-instance-2`, `vm-instance-3` (`e2-micro`, Debian 12, with ephemeral public IPs)
5. **GCS Storage Bucket**: `<PROJECT_ID>-infra-bucket` with uniform bucket-level access enabled

## Usage

### 1. Initialize Stack & Install Dependencies

```bash
# Create and activate virtual environment (if not already done)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Initialize a new Pulumi stack (e.g. dev)
pulumi stack init dev
```

### 2. Configure GCP Settings

```bash
# Set your GCP Project ID
pulumi config set gcp:project YOUR_GCP_PROJECT_ID

# Set Region (defaults to europe-west1 if omitted)
pulumi config set gcp:region europe-west1

# Set Zone (optional, defaults to <region>-a)
pulumi config set gcp:zone europe-west1-a
```

### 3. Deploy Infrastructure

```bash
# Preview changes
pulumi preview

# Deploy resources
pulumi up
```

### 4. Teardown

```bash
pulumi destroy
```
