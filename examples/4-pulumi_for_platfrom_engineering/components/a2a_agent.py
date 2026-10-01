from dataclasses import dataclass, field
from typing import Optional, List, Dict
import pulumi
import pulumi_gcp as gcp


@dataclass
class A2AAgentArgs:
    """Inputs for the A2AAgent component."""
    agent_name: str
    role: str
    image: str = "us-docker.pkg.dev/cloudrun/container/hello:latest"
    memory_limit: str = "512Mi"
    cpu_limit: str = "1"
    allow_unauthenticated: bool = False
    env_vars: Dict[str, pulumi.Input[str]] = field(default_factory=dict)
    peer_agents: List["A2AAgent"] = field(default_factory=list)


class A2AAgent(pulumi.ComponentResource):
    """
    Platform Engineering Component for Google ADK Agent-to-Agent (A2A).

    Encapsulates:
    1. Dedicated least-privilege IAM Service Account.
    2. Vertex AI Agent Platform IAM permissions:
       - roles/aiplatform.user (Gemini models, Session Service, Memory Bank Service).
       - roles/logging.logWriter & roles/monitoring.metricWriter.
    3. Agent Platform Session & Memory Service environment variables.
    4. Authenticated Agent-to-Agent (A2A) authorization:
       - Automatically grants roles/run.invoker on peer agents.
       - Automatically injects PEER_<NAME>_URL into the agent's environment.
    5. Cloud Run (v2) serverless microservice.
    """

    def __init__(
        self,
        name: str,
        args: A2AAgentArgs,
        opts: Optional[pulumi.ResourceOptions] = None,
    ):
        super().__init__("pkg:platform:A2AAgent", name, None, opts)

        child_opts = pulumi.ResourceOptions(parent=self)
        project = gcp.config.project
        region = gcp.config.region or "europe-west4"

        clean_name = args.agent_name.replace("_", "-").lower()

        # 1. Dedicated Service Account
        self.service_account = gcp.serviceaccount.Account(
            f"{name}-sa",
            account_id=f"sa-{clean_name}",
            display_name=f"Service Account for {args.agent_name} ({args.role})",
            opts=child_opts,
        )

        sa_member = pulumi.Output.concat("serviceAccount:", self.service_account.email)

        # 2. Least-Privilege IAM: Vertex AI / Agent Platform access
        # Grants access to Gemini models, Session Service, and Memory Bank Service
        self.vertex_iam = gcp.projects.IAMMember(
            f"{name}-iam-aiplatform",
            project=project,
            role="roles/aiplatform.user",
            member=sa_member,
            opts=child_opts,
        )

        # Observability IAM (Logs and Metrics)
        self.logging_iam = gcp.projects.IAMMember(
            f"{name}-iam-logging",
            project=project,
            role="roles/logging.logWriter",
            member=sa_member,
            opts=child_opts,
        )

        self.monitoring_iam = gcp.projects.IAMMember(
            f"{name}-iam-monitoring",
            project=project,
            role="roles/monitoring.metricWriter",
            member=sa_member,
            opts=child_opts,
        )

        # 3. Environment Variables (including Vertex AI Agent Platform Session & Memory Service)
        env_list = [
            gcp.cloudrunv2.ServiceTemplateContainerEnvArgs(name="AGENT_NAME", value=args.agent_name),
            gcp.cloudrunv2.ServiceTemplateContainerEnvArgs(name="AGENT_ROLE", value=args.role),
            # Vertex AI & Gemini configuration
            gcp.cloudrunv2.ServiceTemplateContainerEnvArgs(name="GOOGLE_GENAI_USE_VERTEXAI", value="true"),
            gcp.cloudrunv2.ServiceTemplateContainerEnvArgs(name="GOOGLE_CLOUD_PROJECT", value=project),
            gcp.cloudrunv2.ServiceTemplateContainerEnvArgs(name="GOOGLE_CLOUD_LOCATION", value=region),
            # Vertex AI Agent Platform Session & Memory Service enablement
            gcp.cloudrunv2.ServiceTemplateContainerEnvArgs(name="AGENT_PLATFORM_SESSION_SERVICE", value="true"),
            gcp.cloudrunv2.ServiceTemplateContainerEnvArgs(name="AGENT_PLATFORM_MEMORY_BANK", value="true"),
        ]

        # Add custom developer-defined environment variables
        for k, v in args.env_vars.items():
            env_list.append(gcp.cloudrunv2.ServiceTemplateContainerEnvArgs(name=k, value=v))

        # 4. Agent-to-Agent (A2A) Peer Wiring
        # For each peer agent, grant roles/run.invoker to this agent's SA and inject the peer's URL
        self.peer_invoker_bindings = []
        for peer in args.peer_agents:
            peer_clean_name = peer.agent_name.replace("-", "_").upper()
            env_list.append(
                gcp.cloudrunv2.ServiceTemplateContainerEnvArgs(
                    name=f"PEER_{peer_clean_name}_URL",
                    value=peer.service_url,
                )
            )

            # Grant roles/run.invoker on peer Cloud Run service to this agent's Service Account
            binding = gcp.cloudrunv2.ServiceIamMember(
                f"{name}-invoker-on-{peer.agent_name}",
                name=peer.service.name,
                location=region,
                role="roles/run.invoker",
                member=sa_member,
                opts=child_opts,
            )
            self.peer_invoker_bindings.append(binding)

        # 5. Cloud Run (v2) Microservice
        self.service = gcp.cloudrunv2.Service(
            f"{name}-service",
            name=f"agent-{clean_name}",
            location=region,
            template=gcp.cloudrunv2.ServiceTemplateArgs(
                service_account=self.service_account.email,
                containers=[
                    gcp.cloudrunv2.ServiceTemplateContainerArgs(
                        image=args.image,
                        resources=gcp.cloudrunv2.ServiceTemplateContainerResourcesArgs(
                            limits={
                                "memory": args.memory_limit,
                                "cpu": args.cpu_limit,
                            }
                        ),
                        envs=env_list,
                    )
                ],
            ),
            opts=child_opts,
        )

        self.service_url = self.service.uri
        self.agent_name = args.agent_name
        self.agent_role = args.role

        # 6. Public Ingress Access (if enabled, e.g. for Orchestrator Agent)
        if args.allow_unauthenticated:
            self.public_invoker = gcp.cloudrunv2.ServiceIamMember(
                f"{name}-public-invoker",
                name=self.service.name,
                location=region,
                role="roles/run.invoker",
                member="allUsers",
                opts=child_opts,
            )

        self.register_outputs({
            "agent_name": self.agent_name,
            "agent_role": self.agent_role,
            "service_name": self.service.name,
            "service_url": self.service_url,
            "service_account_email": self.service_account.email,
        })
