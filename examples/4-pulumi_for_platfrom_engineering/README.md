# Example 4: Pulumi for Platform Engineering — Google ADK Agent-to-Agent (A2A) on GCP

This example showcases the power of **Platform Engineering with Pulumi**: how platform teams can abstract hundreds of lines of complex cloud infrastructure (Cloud Run, least-privilege IAM, Vertex AI, and CI/CD) into reusable, strongly typed Python components.

---

## The Platform Engineering Vision

In traditional IaC, application and AI engineers often struggle with infrastructure boilerplate:
- Configuring IAM service accounts, OAuth tokens, and least-privilege role bindings.
- Enabling underlying cloud APIs and configuring container registries.
- Wiring internal microservice URLs and security policies.
- Setting up CI/CD build triggers and deployment permissions.

With **Pulumi Component Resources** (`pulumi.ComponentResource`), the platform team creates an internal developer platform (IDP) library. As demonstrated in `__main__.py`, application developers deploy a production-grade, secure multi-agent AI system in **under 30 lines of code**:

```python
# 1. Platform Foundation
foundation = PlatformFoundation("adk-platform")

# 2. Private Specialist Agent
specialist_agent = A2AAgent(
    "specialist",
    A2AAgentArgs(agent_name="specialist", role="domain-analyzer", allow_unauthenticated=False),
)

# 3. Public Orchestrator Agent (automatically wired to Specialist via A2A)
orchestrator_agent = A2AAgent(
    "orchestrator",
    A2AAgentArgs(
        agent_name="orchestrator",
        role="task-coordinator",
        allow_unauthenticated=True,
        peer_agents=[specialist_agent],  # Encapsulates A2A OIDC IAM and env vars!
    ),
)

# 4. CI/CD Pipeline
cicd = AgentCiCdPipeline(
    "adk-cicd",
    AgentCiCdPipelineArgs(
        repo_owner="Indavelopers",
        repo_name="devfestmodena26-pulumi",
        artifact_registry_repo=foundation.artifact_registry.name,
        agents=[orchestrator_agent, specialist_agent],
    ),
)
```

---

## Architecture Overview

```
                      +---------------------------------------+
                      |           GitHub Repository           |
                      |    (git push origin main)             |
                      +-------------------+-------------------+
                                          | Webhook
                                          v
                      +-------------------+-------------------+
                      |      Google Cloud Build Trigger       |
                      |       (cloudbuild.yaml)               |
                      +---------+--------------------+--------+
                                |                    |
          Build & Push Images   |                    | Deploy Revisions
                                v                    v
   +----------------------------+--+     +-----------+-------------+
   | Artifact Registry Repository  |     |  Cloud Run Services     |
   | (Docker format: adk-agents)   |     +-----------+-------------+
   +-------------------------------+                 |
                                                     |
       +---------------------------------------------+---------------------------------------------+
       |                                                                                           |
       v                                                                                           v
+------------------------------------+                                     +------------------------------------+
|  Orchestrator Agent (Cloud Run)    | --- Authenticated A2A via OIDC ---> |  Specialist Agent (Cloud Run)      |
|  - Ingress: Public (allUsers)      |     (roles/run.invoker)             |  - Ingress: Private / Internal     |
|  - SA: sa-orchestrator             |                                     |  - SA: sa-specialist               |
|  - Vertex AI: roles/aiplatform.user|                                     |  - Vertex AI: roles/aiplatform.user|
+------------------+-----------------+                                     +------------------+-----------------+
                   |                                                                          |
                   +-----------------------------------+--------------------------------------+
                                                       |
                                                       v
                                  +--------------------+---------------------+
                                  |         Vertex AI Agent Platform         |
                                  |                                          |
                                  |  - Gemini 1.5 / 2.0 Foundation Models    |
                                  |  - Session Service (Short-Term Dialogue) |
                                  |  - Memory Bank (Long-Term Preferences)   |
                                  +------------------------------------------+
```

### 1. Agent Development Kit (ADK) & Agent-to-Agent (A2A) Protocol
- **ADK**: Google's open-source SDK for building modular multi-agent systems.
- **A2A Protocol**: Open communication standard where agents discover capabilities via Agent Cards (`/.well-known/agent.json`) and collaborate over secure HTTP.
- **OIDC Authentication**: The Orchestrator's Service Account is granted `roles/run.invoker` on the Specialist Agent's Cloud Run service, ensuring all inter-agent traffic is cryptographically signed and authenticated with Google ID tokens.

### 2. Vertex AI Agent Platform Session & Memory Service
Instead of manual object storage dumps (GCS), agents connect directly to Google's managed Agent Platform memory services:
- **Session Service** (`VertexAiSessionService`): Tracks conversational turns, intermediate tool calls, and execution events within active sessions.
- **Memory Bank Service** (`VertexAiMemoryBankService`): Extracts semantic knowledge and user preferences across multiple sessions using Gemini.
- Both agents receive `roles/aiplatform.user` on their dedicated Service Accounts to access these endpoints securely.

### 3. Automated CI/CD with Google Cloud Build
- **Cloud Build Trigger** (`gcp.cloudbuild.Trigger`): Automatically builds container images from the GitHub repository on every push to `main`.
- **Least-Privilege Security**: A dedicated Cloud Build service account (`sa-cloudbuild-cicd`) is strictly granted:
  - `roles/run.admin` to manage Cloud Run deployments.
  - `roles/iam.serviceAccountUser` strictly on the agent service accounts.
  - `roles/artifactregistry.writer` on the Docker repository.

---

## Directory Structure

```
examples/4-pulumi_for_platfrom_engineering/
├── Pulumi.yaml                 # Pulumi project configuration (Python runtime)
├── requirements.txt            # Python dependencies (pulumi, pulumi-gcp)
├── .gitignore                  # Virtualenv and state ignore patterns
├── cloudbuild.yaml             # Cloud Build CI/CD pipeline definition
├── __main__.py                 # Developer consumption layer (clean & minimal)
├── components/
│   ├── __init__.py             # Package exports
│   ├── platform_foundation.py  # Shared APIs & Artifact Registry
│   ├── a2a_agent.py            # A2AAgent ComponentResource
│   └── ci_cd_pipeline.py       # AgentCiCdPipeline ComponentResource
└── README.md                   # This documentation
```

---

## Getting Started

### 1. Set Up Python Virtual Environment

```bash
cd examples/4-pulumi_for_platfrom_engineering
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Initialize Stack and Configure GCP

```bash
pulumi stack init dev

# Configure target GCP project and region
pulumi config set gcp:project <YOUR_GCP_PROJECT_ID>
pulumi config set gcp:region europe-west4

# (Optional) Configure GitHub repository for Cloud Build trigger
pulumi config set github_owner <YOUR_GITHUB_ORG_OR_USER>
pulumi config set github_repo <YOUR_GITHUB_REPO>
```

### 3. Preview and Deploy Infrastructure

```bash
# Preview proposed infrastructure changes
pulumi preview

# Deploy to Google Cloud
pulumi up
```

### 4. Stack Outputs

Once deployed, Pulumi outputs the live endpoints:
- `orchestrator_url`: Public HTTPS entrypoint for the Orchestrator Agent.
- `specialist_url`: Authenticated HTTPS endpoint for the Specialist Agent.
- `artifact_registry_url`: Docker repository URL for ADK images.
- `cloudbuild_trigger_name`: Automated Cloud Build trigger name.
- `cloudbuild_sa_email`: Dedicated CI/CD Service Account email.
