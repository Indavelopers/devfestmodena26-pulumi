terraform {
  required_version = ">= 1.5.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

locals {
  zone = coalesce(var.zone, "${var.region}-a")
}

# 1. Custom mode VPC network
resource "google_compute_network" "custom_vpc" {
  name                    = "custom-vpc"
  auto_create_subnetworks = false
  routing_mode            = "REGIONAL"
}

# 2. Subnet
resource "google_compute_subnetwork" "custom_subnet" {
  name          = "custom-subnet"
  ip_cidr_range = "10.0.1.0/24"
  region        = var.region
  network       = google_compute_network.custom_vpc.id
}

# 3. Firewall Rules
resource "google_compute_firewall" "allow_ssh" {
  name        = "${google_compute_network.custom_vpc.name}-allow-ssh"
  network     = google_compute_network.custom_vpc.name
  description = "Allow SSH access from anywhere"

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }

  source_ranges = ["0.0.0.0/0"]
}

resource "google_compute_firewall" "allow_internal" {
  name        = "${google_compute_network.custom_vpc.name}-allow-internal"
  network     = google_compute_network.custom_vpc.name
  description = "Allow internal traffic within the subnet"

  allow {
    protocol = "tcp"
  }
  allow {
    protocol = "udp"
  }
  allow {
    protocol = "icmp"
  }

  source_ranges = [google_compute_subnetwork.custom_subnet.ip_cidr_range]
}

resource "google_compute_firewall" "allow_icmp" {
  name        = "${google_compute_network.custom_vpc.name}-allow-icmp"
  network     = google_compute_network.custom_vpc.name
  description = "Allow ICMP ping from anywhere"

  allow {
    protocol = "icmp"
  }

  source_ranges = ["0.0.0.0/0"]
}

# 4. 3 VM Instances
resource "google_compute_instance" "vm_instance_1" {
  name         = "vm-instance-1"
  machine_type = "e2-micro"
  zone         = local.zone

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-12"
    }
  }

  network_interface {
    subnetwork = google_compute_subnetwork.custom_subnet.id
    access_config {
      // Ephemeral external IP
    }
  }
}

resource "google_compute_instance" "vm_instance_2" {
  name         = "vm-instance-2"
  machine_type = "e2-micro"
  zone         = local.zone

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-12"
    }
  }

  network_interface {
    subnetwork = google_compute_subnetwork.custom_subnet.id
    access_config {
      // Ephemeral external IP
    }
  }
}

resource "google_compute_instance" "vm_instance_3" {
  name         = "vm-instance-3"
  machine_type = "e2-micro"
  zone         = local.zone

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-12"
    }
  }

  network_interface {
    subnetwork = google_compute_subnetwork.custom_subnet.id
    access_config {
      // Ephemeral external IP
    }
  }
}

# 5. GCS Storage Bucket
resource "google_storage_bucket" "infra_bucket" {
  name                        = "${var.project_id}-infra-bucket"
  location                    = var.region
  uniform_bucket_level_access = true
  force_destroy               = true
}
