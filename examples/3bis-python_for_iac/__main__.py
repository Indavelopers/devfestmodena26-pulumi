"""Demonstrating the Top 5 Advantages of Python for IaC with Pulumi on GCP."""

import csv
import os
import requests
import pulumi # type: ignore
import pulumi_gcp as gcp # type: ignore

# ---------------------------------------------------------------------
# ADVANTAGE 4: Object-Oriented Abstraction (Custom ComponentResource Class)
# Encapsulates Network, Subnet, and Firewall creation into a reusable component.
# ---------------------------------------------------------------------
class SecureGcpNetwork(pulumi.ComponentResource):
    def __init__(self, name: str, csv_rules_path: str, opts=None):
        super().__init__("custom:gcp:SecureGcpNetwork", name, None, opts)
        
        # GCP Resource 1: Custom VPC Network
        self.network = gcp.compute.Network(
            f"{name}-vpc",
            auto_create_subnetworks=False,
            opts=pulumi.ResourceOptions(parent=self)
        )
        
        # GCP Resource 2: Subnetwork for VMs
        self.subnet = gcp.compute.Subnetwork(
            f"{name}-subnet",
            network=self.network.id,
            ip_cidr_range="10.0.1.0/24",
            region="europe-west4",
            opts=pulumi.ResourceOptions(parent=self)
        )
        
        # ---------------------------------------------------------------------
        # ADVANTAGE 2: Dynamic HTTP API Requests
        # Fetch deployer's public IP at runtime to restrict firewall rules.
        # ---------------------------------------------------------------------
        try:
            ip_resp = requests.get("https://api.ipify.org?format=json", timeout=5)
            ip_resp.raise_for_status()
            office_ip = f"{ip_resp.json()['ip']}/32"
        except requests.RequestException as e:
            pulumi.log.warn(f"Failed to fetch public IP: {e}. Falling back to default CIDR.")
            office_ip = "192.168.1.0/24"
        
        # ---------------------------------------------------------------------
        # ADVANTAGE 3: External Data Processing & Try/Except Validation
        # Read rules from CSV, validate headers & port bounds (1-65535).
        # ---------------------------------------------------------------------
        try:
            with open(csv_rules_path, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                
                # Header schema validation
                required_headers = {"rule_name", "port"}
                fieldnames = set(reader.fieldnames or [])
                if not required_headers.issubset(fieldnames):
                    missing = required_headers - fieldnames
                    raise KeyError(f"CSV missing required columns: {missing}")
                
                for row_idx, row in enumerate(reader, start=1):
                    rule_name = (row.get("rule_name") or "").strip()
                    port_str = (row.get("port") or "").strip()
                    
                    if not rule_name or not port_str:
                        pulumi.log.warn(f"Row {row_idx}: Skipping empty rule entry.")
                        continue
                    
                    # Port range validation
                    try:
                        port_num = int(port_str)
                        if not (1 <= port_num <= 65535):
                            raise ValueError(f"Port {port_num} is out of valid range (1-65535).")
                    except ValueError as ve:
                        pulumi.log.error(f"Row {row_idx} Firewall Error: {ve}")
                        continue
                    
                    # GCP Resource 3: Firewall Rules
                    gcp.compute.Firewall(
                        f"{name}-fw-{rule_name}",
                        network=self.network.name,
                        allows=[{"protocol": "tcp", "ports": [str(port_num)]}],
                        source_ranges=[office_ip],
                        opts=pulumi.ResourceOptions(parent=self)
                    )

        except FileNotFoundError:
            pulumi.log.error(f"Firewall CSV rules file not found: '{csv_rules_path}'")
            raise
        except KeyError as ke:
            pulumi.log.error(f"CSV Header Schema Error: {ke}")
            raise
        except Exception as err:
            pulumi.log.error(f"Unexpected error parsing CSV file: {err}")
            raise

        self.register_outputs({
            "network_name": self.network.name,
            "subnet_id": self.subnet.id
        })


# Path to the CSV file relative to this script
csv_path = os.path.join(os.path.dirname(__file__), "firewall_rules.csv")

# 1. Instantiate Network Component
network_sandbox = SecureGcpNetwork("dev-sandbox", csv_rules_path=csv_path)

# ---------------------------------------------------------------------
# 2. ADVANTAGE 1: Native Control Flow (if/else) and for loop
# ---------------------------------------------------------------------
stack = pulumi.get_stack()
machine_type = "e2-standard-4" if stack == "prod" else "e2-micro"

# 3. Native Python FOR LOOP: Create 3 Compute Engine VMs inside the VPC/Subnet
instances = []
vm_roles = ["web-frontend", "api-backend", "worker-node"]

for index, role in enumerate(vm_roles):
    vm = gcp.compute.Instance(
        f"dev-vm-{role}",
        name=f"dev-vm-{role}",
        machine_type=machine_type,
        zone="europe-west4-a",
        boot_disk=gcp.compute.InstanceBootDiskArgs(
            initialize_params=gcp.compute.InstanceBootDiskInitializeParamsArgs(
                image="debian-cloud/debian-13",
                size=10,
            )
        ),
        network_interfaces=[gcp.compute.InstanceNetworkInterfaceArgs(
            subnetwork=network_sandbox.subnet.id
        )],
        metadata={"instance-index": str(index)},
        labels={
            "role": role,
            "environment": stack,
            "managed_by": "pulumi"
        }
    )
    instances.append(vm)

# Export stack outputs
pulumi.export("network_name", network_sandbox.network.name)
pulumi.export("instance_names", [vm.name for vm in instances])
