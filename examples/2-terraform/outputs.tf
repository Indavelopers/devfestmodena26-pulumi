output "network_name" {
  description = "The name of the VPC network"
  value       = google_compute_network.custom_vpc.name
}

output "subnetwork_name" {
  description = "The name of the subnetwork"
  value       = google_compute_subnetwork.custom_subnet.name
}

output "vm_instances" {
  description = "List of created VM instance names"
  value = [
    google_compute_instance.vm_instance_1.name,
    google_compute_instance.vm_instance_2.name,
    google_compute_instance.vm_instance_3.name
  ]
}

output "bucket_name" {
  description = "The name of the GCS bucket"
  value       = google_storage_bucket.infra_bucket.name
}

output "bucket_url" {
  description = "The URL of the GCS bucket"
  value       = google_storage_bucket.infra_bucket.url
}
