"""
DevFest Modena 2026: From dev to Platform Engineer with Pulumi IaC
Example 4: Platform Engineering Abstractions for Google ADK Agent-to-Agent (A2A) on GCP
"""

import pulumi
from components import (
    PlatformFoundation,
    PlatformFoundationArgs,
    A2AAgent,
    A2AAgentArgs,
    AgentCiCdPipeline,
    AgentCiCdPipelineArgs,
)

# Configuration
config = pulumi.Config()
repo_owner = config.get("github_owner") or "Indavelopers"
repo_name = config.get("github_repo") or "devfestmodena26-pulumi"

# ==============================================================================
# 1. Platform Foundation: APIs & Artifact Registry
# ==============================================================================
foundation = PlatformFoundation("adk-platform")

# ==============================================================================
# 2. Specialist Agent (Private Sub-Agent)
# Configured with Vertex AI Agent Platform Session & Memory Service
# ==============================================================================
specialist_agent = A2AAgent(
    "specialist",
    A2AAgentArgs(
        agent_name="specialist",
        role="domain-analyzer",
        allow_unauthenticated=False,  # Private: requires authenticated A2A invocation
    ),
    opts=pulumi.ResourceOptions(depends_on=foundation.services),
)

# ==============================================================================
# 3. Orchestrator Agent (Public Gateway / Host Agent)
# Automatically granted roles/run.invoker on specialist_agent and injected PEER_SPECIALIST_URL
# ==============================================================================
orchestrator_agent = A2AAgent(
    "orchestrator",
    A2AAgentArgs(
        agent_name="orchestrator",
        role="task-coordinator",
        allow_unauthenticated=True,  # Public entrypoint for user interaction
        peer_agents=[specialist_agent],  # Encapsulates Agent-to-Agent (A2A) authorization
    ),
    opts=pulumi.ResourceOptions(depends_on=foundation.services),
)

# ==============================================================================
# 4. CI/CD Pipeline (GitHub Push -> Cloud Build -> Cloud Run)
# ==============================================================================
cicd_pipeline = AgentCiCdPipeline(
    "adk-cicd",
    AgentCiCdPipelineArgs(
        repo_owner=repo_owner,
        repo_name=repo_name,
        artifact_registry_repo=foundation.artifact_registry.name,
        agents=[orchestrator_agent, specialist_agent],
    ),
    opts=pulumi.ResourceOptions(depends_on=foundation.services),
)

# ==============================================================================
# 5. Stack Outputs
# ==============================================================================
pulumi.export("orchestrator_url", orchestrator_agent.service_url)
pulumi.export("specialist_url", specialist_agent.service_url)
pulumi.export("artifact_registry_url", foundation.repository_url)
pulumi.export("cloudbuild_trigger_name", cicd_pipeline.trigger.name)
pulumi.export("cloudbuild_sa_email", cicd_pipeline.build_sa.email)
