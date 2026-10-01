# DevFest Modena 2026: "From dev to Platform Engineer with Pulumi IaC"

## About the speaker

- Marcos Manuel Ortega - Indavelopers
- Consultant, architect & trainer - 14 years of experience
- Google Cloud, data/Gemini, Pulumi, finOps
- [Google Developer Expert in Google Cloud](https://drive.google.com/file/d/1SSB5_mPqR6RmTjyXCkndzRCLp9PTgHEf/view?usp=sharing)
- Google Cloud Authorized Trainer
- Google Cloud certified x11
- Former community organizer: Club Python Almería, GDG Almería, GDG Cloud Español, DataBeers ALM, Hacklab Almería, etc.
- Contact:
  - Email: <info@indavelopers.com>
  - LinkedIn: [linkedin.com/in/marcosmanuelortega](https://www.linkedin.com/in/marcosmanuelortega/)
  - GitHub: [github.com/Indavelopers](https://github.com/Indavelopers)
- Made with ❤️ from Almería, Spain

## About the session

- **Link to this repo:** <https://github.com/Indavelopers/devfestmodena26-pulumi> / **Search on GH for DevFest Modena 2026 Pulumi**
- Session URL: <https://devfest.modena.it/en/2026/sessions/from-dev-to-platform-engineer-with-pulumi-iac/>
- DevFest Modena 2026: <https://devfest.modena.it/en/>

### Title and description

"From dev to Platform Engineer with Pulumi IaC"

Why keep managing your cloud infrastructure with rigid HCL when you can use the power of Python?

Traditional Infrastructure as Code (IaC) tools forced us developers to use domain-specific languages that lack the ecosystem, tooling and best practices we love.

Let’s see how Pulumi and its supported programming languages bridge the gap between dev or devOps to Platform Engineering without language switching, while discussing how recent Terraform changes make now maybe the perfect time to adopt a truly code-first, open-source approach.

This session is a dive into IaC and Pulumi + Python, the OSS tool that treats infrastructure as a first-class code citizen, not just a config file. We’ll deploy and manage a Google Cloud environment, demonstrating how Python’s great ecosystem allows better abstraction, loop management and testing than HCL or YAML.

No slides, no agents YOLOing? Just 30’ of hands-on, live, real coding on a dark theme terminal.

Audience: Cloud architects & engineers, devOps, devs looking to grow into platform engineers before AI takes our jobs and dooms us all maybe :O?

## Session contents

The repository is organized into hands-on examples progressing from raw scripts to high-level Platform Engineering abstractions:

- [`examples/1-bash_scripts`](examples/1-bash_scripts/): Imperative infrastructure with `gcloud` CLI bash scripts (VPC, subnet, firewall, VMs, bucket).
- [`examples/2-terraform`](examples/2-terraform/): Traditional declarative HCL with Terraform.
- [`examples/3-pulumi_iac`](examples/3-pulumi_iac/): Translating HCL into pythonic Pulumi IaC with dynamic loops, typing, and standard packages.
- [`examples/4-pulumi_for_platfrom_engineering`](examples/4-pulumi_for_platfrom_engineering/): Platform Engineering abstractions (`ComponentResource`) deploying a Google ADK Agent-to-Agent (A2A) platform on GCP with Vertex AI Agent Platform Session & Memory Service, and automated GitHub CI/CD with Cloud Build.
- [`examples/5-migrating_tf_to_pulumi`](examples/5-migrating_tf_to_pulumi/): Migrating from Terraform to Pulumi YAML via `pulumi convert` without copying or linking files.

### Main ideas

1. Platform engineering as a career step up after agentic AI takes our coding jobs and dooms us all.
2. Platform engineering is mainly done via IaC.
3. New alternatives for IaC available: Python vs HCL, Pulumi vs Terraform.

### Index

1. Platform engineering via Bash scripts?
2. Short intro to IaC: declarative vs imperative, reusable templates, parallelism, dependencies, reproducibility, auditable, composable blocks, gitOps
3. Terraform example & shortcomings.
4. Pulumi IaC Python runtime: pythonic code, modules, best practices.
5. Pulumi IaC for platform engineering (Google ADK A2A + Vertex AI Agent Platform + Cloud Build CI/CD).
6. Migrating from TF to Pulumi (Terraform to Pulumi YAML).

## License

CC BY 4.0 (see `LICENSE.md`).

## Extra

- <https://github.com/Indavelopers/pyconpt26-pulumi>: PyConPT'26 session about Pulumi IaC + Python.
- <https://github.com/Indavelopers/pycones25-pulumi>: PyConES'25 session about Pulumi IaC + Python.
- <https://github.com/Indavelopers/gcp-training-projects>: Demo project and how-to guide to use Pulumi as an IaC (Infrastructure as Code) tool for creating GCP sandbox projects with starting resources for demos, workshops, trainings, etc.

## TO-DOs

- x
