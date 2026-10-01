# GCP Infrastructure Provisioning via Terraform

This directory contains Terraform code to provision the same GCP infrastructure as in `examples/1-bash_scripts/create_infra.sh`

## Resources Created

1. **Custom Mode VPC Network**: `custom-vpc` (subnet mode: custom)
2. **Subnet**: `custom-subnet` (`10.0.1.0/24`) in the target region
3. **Firewall Rules**:
   - `custom-vpc-allow-ssh`: Allows SSH (port 22) from `0.0.0.0/0`
   - `custom-vpc-allow-internal`: Allows internal TCP/UDP/ICMP traffic within `10.0.1.0/24`
   - `custom-vpc-allow-icmp`: Allows ICMP ping from `0.0.0.0/0`
4. **3 VM Instances**: `vm-instance-1`, `vm-instance-2`, `vm-instance-3` (`e2-micro`, Debian 12)
5. **GCS Storage Bucket**: `<PROJECT_ID>-infra-bucket` with uniform bucket-level access enabled

## Usage

### 1. Configure Variables

Copy `terraform.tfvars.example` to `terraform.tfvars` and set your project ID:

```bash
cp terraform.tfvars.example terraform.tfvars
```

Or pass variables via command-line flags or environment variables:

```bash
export TF_VAR_project_id="your-gcp-project-id"
export TF_VAR_region="europe-west1"
```

### 2. Initialize Terraform

```bash
terraform init
```

### 3. Plan & Apply

```bash
terraform plan
terraform apply
```

### 4. Teardown

```bash
terraform destroy
```
