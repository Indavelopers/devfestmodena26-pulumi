# Migrating from Terraform to Pulumi: Converting to Pulumi YAML

This directory demonstrates converting existing Terraform configurations into **Pulumi YAML** directly using the `pulumi convert` CLI.

## Key Takeaway: No Copying or Linking Required

You do **not** need to copy code or create symlinks between directories. Pulumi provides built-in source and target flags:

```bash
pulumi convert \
    --from terraform \
    --cwd ../2-terraform \
    --language yaml \
    --out .
```

- `--cwd`: Directs Pulumi to read the Terraform files from the source directory (`../2-terraform`).
- `--out`: Directs Pulumi to write the generated Pulumi project in the target directory (`.`).
- `--language yaml`: Emits clean, declarative Pulumi YAML.

## Automated Conversion Script

Run the included helper script:

```bash
./convert_to_yaml.sh
```

This generates:

- `Pulumi.yaml`: The project definition metadata and runtime specification.
- `Main.yaml`: The converted declarative resources (VPC, Subnet, Firewall rules, 3 Compute Instances, and Storage Bucket).

## Running and Previewing

Configure standard GCP project settings and preview:

```bash
# Initialize stack (if not already initialized)
pulumi stack select dev || pulumi stack init dev

# Configure standard GCP provider settings
pulumi config set gcp:project <YOUR_GCP_PROJECT_ID>
pulumi config set gcp:region europe-west4

# Run preview
pulumi preview
```

> [!NOTE]
> `Main.yaml` automatically maps the `${project}` and `${region}` variables to `${gcp:project}` and `${gcp:region}`, so you only ever need to configure the standard GCP provider values.

## Why Pulumi YAML in Platform Engineering?

1. **Gentle Onboarding & Lingua Franca**:
   - Pulumi YAML lets teams transitioning from Terraform/Ansible/Kubernetes YAML write declarative infrastructure without having to learn a full programming language immediately.
2. **Deterministic & Declarative**:
   - Clean, readable infrastructure syntax with zero build or compilation steps.
3. **The Graduation Path to Python**:
   - Pulumi YAML is intentionally strictly declarative (no native loops or complex branching).
   - As platform teams scale and need reusable abstractions (**Component Resources**), dynamic sizing, or policy enforcement, they can graduate directly to **Pulumi Python** (`examples/3-pulumi_iac`) without changing tools.
