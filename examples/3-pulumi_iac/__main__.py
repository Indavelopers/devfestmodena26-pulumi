"""Pulumi program to deploy GCP infrastructure matching Terraform configuration."""

import pulumi
from pulumi_gcp import compute, storage

# Configuration
config = pulumi.Config()
gcp_config = pulumi.Config("gcp")

project_id = gcp_config.get("project") or config.require("project_id")
region = gcp_config.get("region") or config.get("region") or "europe-west1"
zone = gcp_config.get("zone") or config.get("zone") or f"{region}-a"

# 1. Custom mode VPC network
custom_vpc = compute.Network(
    "custom-vpc",
    name="custom-vpc",
    auto_create_subnetworks=False,
    routing_mode="REGIONAL",
)

# 2. Subnet
custom_subnet = compute.Subnetwork(
    "custom-subnet",
    name="custom-subnet",
    ip_cidr_range="10.0.1.0/24",
    region=region,
    network=custom_vpc.id,
)

# 3. Firewall Rules
allow_ssh = compute.Firewall(
    "custom-vpc-allow-ssh",
    name=custom_vpc.name.apply(lambda name: f"{name}-allow-ssh"),
    network=custom_vpc.name,
    description="Allow SSH access from anywhere",
    allows=[
        compute.FirewallAllowArgs(
            protocol="tcp",
            ports=["22"],
        )
    ],
    source_ranges=["0.0.0.0/0"],
)

allow_internal = compute.Firewall(
    "custom-vpc-allow-internal",
    name=custom_vpc.name.apply(lambda name: f"{name}-allow-internal"),
    network=custom_vpc.name,
    description="Allow internal traffic within the subnet",
    allows=[
        compute.FirewallAllowArgs(protocol="tcp"),
        compute.FirewallAllowArgs(protocol="udp"),
        compute.FirewallAllowArgs(protocol="icmp"),
    ],
    source_ranges=[custom_subnet.ip_cidr_range],
)

allow_icmp = compute.Firewall(
    "custom-vpc-allow-icmp",
    name=custom_vpc.name.apply(lambda name: f"{name}-allow-icmp"),
    network=custom_vpc.name,
    description="Allow ICMP ping from anywhere",
    allows=[
        compute.FirewallAllowArgs(protocol="icmp"),
    ],
    source_ranges=["0.0.0.0/0"],
)

# 4. 3 VM Instances
vm_instances = []
for i in range(1, 4):
    instance_name = f"vm-instance-{i}"
    instance = compute.Instance(
        instance_name,
        name=instance_name,
        machine_type="e2-micro",
        zone=zone,
        boot_disk=compute.InstanceBootDiskArgs(
            initialize_params=compute.InstanceBootDiskInitializeParamsArgs(
                image="debian-cloud/debian-12",
            ),
        ),
        network_interfaces=[
            compute.InstanceNetworkInterfaceArgs(
                subnetwork=custom_subnet.id,
                access_configs=[compute.InstanceNetworkInterfaceAccessConfigArgs()],
            )
        ],
    )
    vm_instances.append(instance)

# 5. GCS Storage Bucket
bucket_name = f"{project_id}-infra-bucket"
infra_bucket = storage.Bucket(
    "infra-bucket",
    name=bucket_name,
    location=region,
    uniform_bucket_level_access=True,
    force_destroy=True,
)

# Outputs
pulumi.export("network_name", custom_vpc.name)
pulumi.export("subnetwork_name", custom_subnet.name)
pulumi.export("vm_instances", [vm.name for vm in vm_instances])
pulumi.export("bucket_name", infra_bucket.name)
pulumi.export("bucket_url", infra_bucket.url)
