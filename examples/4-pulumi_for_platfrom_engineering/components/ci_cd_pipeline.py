from dataclasses import dataclass, field
from typing import Optional, List
import pulumi
import pulumi_gcp as gcp
from .a2a_agent import A2AAgent


@dataclass
class AgentCiCdPipelineArgs:
    """Inputs for the AgentCiCdPipeline component."""
    repo_owner: str
    repo_name: str
    artifact_registry_repo: pulumi.Input[str]
    agents: List[A2AAgent]
    branch_pattern: str = "^main$"
    build_config_file: str = "examples/4-pulumi_for_platfrom_engineering/cloudbuild.yaml"


class AgentCiCdPipeline(pulumi.ComponentResource):
    """
    Platform Engineering CI/CD Pipeline Component.

    Automates building and deploying ADK agents from GitHub to Cloud Run:
    1. Dedicated Cloud Build Service Account with least-privilege IAM.
    2. Cloud Run admin permissions to roll out new container revisions.
    3. IAM ServiceAccountUser permissions strictly on the agent SAs.
    4. Artifact Registry writer permissions for Docker push.
    5. Cloud Build Trigger listening for GitHub repository push events.
    """

    def __init__(
        self,
        name: str,
        args: AgentCiCdPipelineArgs,
        opts: Optional[pulumi.ResourceOptions] = None,
    ):
        super().__init__("pkg:platform:AgentCiCdPipeline", name, None, opts)

        child_opts = pulumi.ResourceOptions(parent=self)
        project = gcp.config.project
        region = gcp.config.region or "europe-west4"

        # 1. Dedicated Cloud Build Service Account
        self.build_sa = gcp.serviceaccount.Account(
            f"{name}-cb-sa",
            account_id="sa-cloudbuild-cicd",
            display_name="Cloud Build CI/CD Service Account for ADK Agents",
            opts=child_opts,
        )

        cb_sa_member = pulumi.Output.concat("serviceAccount:", self.build_sa.email)

        # 2. Grant Cloud Run Admin on Project
        self.run_admin_iam = gcp.projects.IAMMember(
            f"{name}-cb-run-admin",
            project=project,
            role="roles/run.admin",
            member=cb_sa_member,
            opts=child_opts,
        )

        # 3. Grant ServiceAccountUser strictly on each Agent's Service Account
        self.sa_user_bindings = []
        for idx, agent in enumerate(args.agents):
            binding = gcp.serviceaccount.IAMMember(
                f"{name}-cb-sa-user-{idx}",
                service_account_id=agent.service_account.name,
                role="roles/iam.serviceAccountUser",
                member=cb_sa_member,
                opts=child_opts,
            )
            self.sa_user_bindings.append(binding)

        # 4. Grant Artifact Registry Writer permissions
        self.ar_writer_iam = gcp.artifactregistry.RepositoryIamMember(
            f"{name}-cb-ar-writer",
            repository=args.artifact_registry_repo,
            location=region,
            role="roles/artifactregistry.writer",
            member=cb_sa_member,
            opts=child_opts,
        )

        # 5. Grant Cloud Build Log Writer
        self.logging_iam = gcp.projects.IAMMember(
            f"{name}-cb-logging",
            project=project,
            role="roles/logging.logWriter",
            member=cb_sa_member,
            opts=child_opts,
        )

        # 6. Cloud Build Trigger (GitHub push)
        agent_names = [a.agent_name for a in args.agents]
        orchestrator_svc = f"agent-{agent_names[0].replace('_', '-').lower()}" if len(agent_names) > 0 else ""
        specialist_svc = f"agent-{agent_names[1].replace('_', '-').lower()}" if len(agent_names) > 1 else ""

        self.trigger = gcp.cloudbuild.Trigger(
            f"{name}-github-trigger",
            name="adk-agents-cicd-trigger",
            description="Automated CI/CD for ADK agents from GitHub",
            location=region,
            service_account=self.build_sa.id,
            github=gcp.cloudbuild.TriggerGithubArgs(
                owner=args.repo_owner,
                name=args.repo_name,
                push=gcp.cloudbuild.TriggerGithubPushArgs(
                    branch=args.branch_pattern,
                ),
            ),
            filename=args.build_config_file,
            substitutions={
                "_REGION": region,
                "_ARTIFACT_REPO": args.artifact_registry_repo,
                "_ORCHESTRATOR_SVC": orchestrator_svc,
                "_SPECIALIST_SVC": specialist_svc,
            },
            opts=child_opts,
        )

        self.register_outputs({
            "cloudbuild_sa_email": self.build_sa.email,
            "trigger_name": self.trigger.name,
            "trigger_id": self.trigger.trigger_id,
        })
