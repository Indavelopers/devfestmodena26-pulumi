from dataclasses import dataclass
from typing import Optional, List
import pulumi
import pulumi_gcp as gcp


@dataclass
class PlatformFoundationArgs:
    """Inputs for the PlatformFoundation component."""
    repository_id: Optional[str] = "adk-agents"
    description: Optional[str] = "Artifact Registry for ADK agent container images"
    services: Optional[List[str]] = None


class PlatformFoundation(pulumi.ComponentResource):
    """
    Platform Engineering Foundation Component.

    Provisions shared platform infrastructure:
    - Enables required GCP APIs (Vertex AI / Agent Platform, Cloud Run, Artifact Registry, Cloud Build).
    - Creates Artifact Registry repository for containerized ADK agents.
    """

    def __init__(
        self,
        name: str,
        args: Optional[PlatformFoundationArgs] = None,
        opts: Optional[pulumi.ResourceOptions] = None,
    ):
        super().__init__("pkg:platform:PlatformFoundation", name, None, opts)

        args = args or PlatformFoundationArgs()
        child_opts = pulumi.ResourceOptions(parent=self)

        required_services = args.services or [
            "aiplatform.googleapis.com",      # Vertex AI, Gemini, Agent Platform Session & Memory Service
            "run.googleapis.com",             # Cloud Run v2 for containerized agents
            "artifactregistry.googleapis.com", # Artifact Registry for ADK Docker images
            "cloudbuild.googleapis.com",      # Cloud Build for CI/CD automation
        ]

        # 1. Enable GCP Services
        self.services = []
        for service_name in required_services:
            clean_name = service_name.replace(".", "-")
            srv = gcp.projects.Service(
                f"{name}-svc-{clean_name}",
                service=service_name,
                disable_on_destroy=False,
                opts=child_opts,
            )
            self.services.append(srv)

        # 2. Artifact Registry for ADK Docker images
        repo_opts = pulumi.ResourceOptions(parent=self, depends_on=self.services)
        self.artifact_registry = gcp.artifactregistry.Repository(
            f"{name}-repo",
            repository_id=args.repository_id,
            description=args.description,
            format="DOCKER",
            opts=repo_opts,
        )

        project = gcp.config.project
        region = gcp.config.region or "europe-west4"

        self.repository_url = pulumi.Output.concat(
            region, "-docker.pkg.dev/", project, "/", self.artifact_registry.repository_id
        )

        self.register_outputs({
            "repository_name": self.artifact_registry.name,
            "repository_url": self.repository_url,
        })
