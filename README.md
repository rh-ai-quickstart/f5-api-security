<!-- omit from toc -->
# Securing Model Inference with F5 Distributed Cloud API Security

<!-- omit from toc -->
## Table of contents

<!-- TOC depthFrom:2 depthTo:3 -->
- [Detailed description](#detailed-description)
  - [Architecture diagrams](#architecture-diagrams)
- [Requirements](#requirements)
  - [Minimum hardware requirements](#minimum-hardware-requirements)
  - [Minimum software requirements](#minimum-software-requirements)
  - [Required user permissions](#required-user-permissions)
- [Deploy](#deploy)
  - [Prerequisites](#prerequisites)
  - [Supported Models](#supported-models)
- [Deploying the Quickstart Baseline (Step 1)](#deploying-the-quickstart-baseline-step-1)
  - [Installation Steps](#installation-steps)
    - [1. Login to OpenShift](#1-login-to-openshift)
    - [2. Clone the Repository](#2-clone-the-repository)
    - [3. Navigate to Deployment Directory](#3-navigate-to-deployment-directory)
    - [4. Configure and Deploy](#4-configure-and-deploy)
  - [Post-Deployment Verification (Optional)](#post-deployment-verification-optional)
  - [Check Deployed Models (LlamaStack Endpoint)](#check-deployed-models-llamastack-endpoint)
    - [Test Chat Completion (LlamaStack Endpoint)](#test-chat-completion-llamastack-endpoint)
    - [Test Chat Completion (Secured vLLM Endpoint)](#test-chat-completion-secured-vllm-endpoint)
    - [Summary](#summary)
- [Next Steps: Deploying and Securing (Steps 2 \& 3)](#next-steps-deploying-and-securing-steps-2--3)
  - [Step 2: Deploy F5 Distributed Cloud](#step-2-deploy-f5-distributed-cloud)
  - [Step 3: Configure and Run Use Cases for F5 Distributed Cloud](#step-3-configure-and-run-use-cases-for-f5-distributed-cloud)
- [Delete](#delete)
- [References](#references)
- [Technical details](#technical-details)
- [Tags](#tags)

<!-- /TOC -->


## Detailed description

This QuickStart shows how to protect AI inference endpoints on Red Hat OpenShift AI using F5 Distributed Cloud (XC) Web App & API Protection (WAAP) + API Security. You’ll deploy a KServe/vLLM model service in OpenShift AI, front it with an F5 XC HTTP Load Balancer, and enforce API discovery, OpenAPI schema validation, rate limiting, bot defense, and sensitive-data controls—without changing your ML workflow. OpenShift AI’s single-model serving is KServe-based (recommended for LLMs), and KServe’s HuggingFace/vLLM runtime exposes OpenAI-compatible endpoints, which we’ll secure via F5 XC

Key Components

- **Red Hat OpenShift AI** – Unified MLOps platform for developing and inference models at scale
- **F5 Distributed Cloud API Security** – Provides LLM-aware threat detection, schema validation, and sensitive data redaction
- **Chat Assistant** – AI-powered chat interface 
- **Direct Mode RAG** – Retrieval-Augmented Generation without agent complexity
- **Integration Blueprint** – Demonstrates secure model inference across hybrid environments


## Quick Start

### Prerequisites
- OpenShift cluster with RHOAI installed
- Helm CLI installed
- `oc` CLI logged into OpenShift

### Deploy

1. **Clone the repository**:
```bash
git clone https://github.com/rh-ai-quickstart/F5-API-Security.git
cd F5-API-Security/deploy/helm
```

2. **Deploy the application**:
```bash
make install NAMESPACE=<namespace>
```

3. **Access and configure**:
```bash
# Get the route URL
oc get route -n <namespace>

# Open the application URL in your browser
# Configure LLM settings via the web UI:
# • XC URL: Set your chat completions endpoint
# • Model ID: Specify the model to use  
# • API Key: Add authentication if required
```

## Document Management

Documents can be uploaded directly through the UI:

### 📄 Supported Formats
- **PDF Documents**: Upload security policies, manuals, and reports
- **Text Files**: Plain text documents

Navigate to **Settings → Vector Databases** to create vector databases and upload documents.

### Architecture diagrams
![RAG System Architecture](docs/images/rag-architecture_F5XC.png)

| Layer/Component | Technology | Purpose/Description |
|-----------------|------------|---------------------|
| **Orchestration** | OpenShift AI | Container orchestration and GPU acceleration |
| **Framework** | LLaMA Stack | Standardizes core building blocks and simplifies AI application development |
| **UI Layer** | Streamlit | User-friendly chatbot interface for chat-based interaction |
| **LLM** | Llama-3.2-3B-Instruct | Generates contextual responses based on retrieved documents |
| **Embedding** | all-MiniLM-L6-v2 | Converts text to vector embeddings |
| **Vector DB** | PostgreSQL + PGVector | Stores embeddings and enables semantic search |
| **Retrieval** | Vector Search | Retrieves relevant documents based on query similarity |
| **Storage** | S3 Bucket | Document source for enterprise content |



## Requirements


### Minimum hardware requirements 

<!-- CONTRIBUTOR TODO: add minimum hardware requirements

*Section is required.* 

Be as specific as possible. DON'T say "GPU". Be specific.

List minimum hardware requirements.

--> 

### Minimum software requirements

- OpenShift Client CLI - [oc](https://docs.redhat.com/en/documentation/openshift_container_platform/4.18/html/cli_tools/openshift-cli-oc#installing-openshift-cli)
- OpenShift Cluster 4.18+
- OpenShift AI
- Helm CLI - helm


### Required user permissions

- Regular user permission for default deployment
- Cluster admin required for *advanced* configurations


## Deploy

*The instructions below will deploy this quickstart to your OpenShift environment.*

*Please see the [local deployments](#local-deployment) section for additional deployment options.* 

### Prerequisites
- [huggingface-cli](https://huggingface.co/docs/huggingface_hub/guides/cli) (optional)
- [Hugging Face Token](https://huggingface.co/settings/tokens)
- Access to [Meta Llama](https://huggingface.co/meta-llama/Llama-3.2-3B-Instruct/) model
- Access to [Meta Llama Guard](https://huggingface.co/meta-llama/Llama-Guard-3-8B/) model
- Some of the example scripts use `jq` a JSON parsing utility which you can acquire via `brew install jq`

### Supported Models

| Function    | Model Name                             | Hardware    | AWS
|-------------|----------------------------------------|-------------|-------------
| Embedding   | `all-MiniLM-L6-v2`                     | CPU/GPU/HPU |
| Generation  | `meta-llama/Llama-3.2-3B-Instruct`     | L4/HPU      | g6.2xlarge
| Generation  | `meta-llama/Llama-3.1-8B-Instruct`     | L4/HPU      | g6.2xlarge
| Generation  | `meta-llama/Meta-Llama-3-70B-Instruct` | A100 x2/HPU | p4d.24xlarge
| Safety      | `meta-llama/Llama-Guard-3-8B`          | L4/HPU      | g6.2xlarge

Note: the 70B model is NOT required for initial testing of this example. The safety/shield model `Llama-Guard-3-8B` is also optional.

## Deploying the Quickstart Baseline (Step 1)
The instructions below will deploy the core AI stack (pgvector, llm-service, llama-stack) to your OpenShift environment.

### Installation Steps

#### 1. Login to OpenShift

Log in to your OpenShift cluster using your token and API endpoint:

```bash
oc login --token=<your_sha256_token> --server=<cluster-api-endpoint>
```

> Example: The observed deployment logged into `https://api.gpu-ai.bd.f5.com:6443` using a specific token and used project `z-ji` initially.

---

#### 2. Clone the Repository

Clone the F5-API-Security repository:

```bash
git clone https://github.com/rh-ai-quickstart/F5-API-Security
```

> The repository was cloned into the local directory.

---

#### 3. Navigate to Deployment Directory

Change into the cloned repository and then into the `deploy/helm` folder:

```bash
cd F5-API-Security
cd deploy/helm
```

> The deployment process navigated to `~/F5-API-Security/deploy/helm`.

---

#### 4. Configure and Deploy

First, configure your deployment values:

```bash
# Copy the example configuration file
cp rag-values.yaml.example rag-values.yaml

# Edit the configuration file to set your values
vim rag-values.yaml  # or use your preferred editor
```

Then deploy using the Makefile:

```bash
make install NAMESPACE=f5-ai-security
```

During installation, the make command:
- Checks required dependencies (helm, oc).
- Creates the namespace if it doesn't exist.
- Updates Helm dependencies.
- Downloads required charts (`pgvector`, `llama-stack`).
- Installs the Helm chart with your custom values from `rag-values.yaml`.

A successful deployment will show:

```
[SUCCESS] All dependencies are installed.
[INFO] Creating namespace f5-ai-security...
[SUCCESS] Namespace f5-ai-security is ready
[INFO] Installing rag helm chart with rag-values.yaml...
NAME: rag
LAST DEPLOYED: Thu Dec 11 10:38:36 2025
NAMESPACE: f5-ai-security
STATUS: deployed
REVISION: 1
[SUCCESS] rag installed successfully
```

---

### Post-Deployment Verification (Optional)

Once deployed, you can verify that the model endpoints are running correctly using `curl`.

### Check Deployed Models (LlamaStack Endpoint)

```bash
curl -sS http://llamastack-f5-ai-security.apps.gpu-ai.bd.f5.com/v1/models
```

> Expected output: Two models available — a large language model and an embedding model.

---

#### Test Chat Completion (LlamaStack Endpoint)

```bash
curl -sS http://llamastack-f5-ai-security.apps.gpu-ai.bd.f5.com/v1/openai/v1/chat/completions   -H "Content-Type: application/json"   -d '{
    "model": "remote-llm/RedHatAI/Llama-3.2-1B-Instruct-quantized.w8a8",
    "messages": [{"role": "user", "content": "Say hello in one sentence."}],
    "max_tokens": 64,
    "temperature": 0
  }' | jq
```

> Example output:  
> `"Hello, how can I assist you today?"`

---

#### Test Chat Completion (Secured vLLM Endpoint)

```bash
curl -sS http://your-xc-endpoint.com/v1/openai/v1/chat/completions   -H "Content-Type: application/json"   -d '{
    "model": "your-model-id",
    "messages": [{"role": "user", "content": "Say hello in one sentence."}],
    "max_tokens": 64,
    "temperature": 0
  }' | jq
```

> This test against the dedicated vLLM endpoint also returned a successful response.

---

#### Summary

The deployment successfully sets up the F5-API-Security QuickStart environment on OpenShift, installs the Helm chart, and exposes model endpoints that can be verified using standard API calls.

---

## Next Steps: Deploying and Securing (Steps 2 & 3)

With the core AI baseline deployed, proceed to the detailed guides for configuring the F5 Distributed Cloud components and running security use cases:

### Step 2: Deploy F5 Distributed Cloud
Configure the F5 Distributed Cloud components and integrate the LLM endpoint.  
➡️ [Deployment and Configuration of F5 Distributed Cloud](docs/f5_xc_deployment.md)

### Step 3: Configure and Run Use Cases for F5 Distributed Cloud
Run security testing to demonstrate how F5 API Security protects the deployed model inference services.  
➡️ [Security Use Cases and Testing](docs/securing_model_inference_use_cases.md)

---



## Delete

To completely remove the F5-API-Security application from your OpenShift cluster:

### Uninstall the Application

```bash
cd F5-API-Security/deploy/helm
make uninstall NAMESPACE=f5-ai-security
```

This will:
- Uninstall the Helm release
- Delete all pods, services, and routes
- Remove the pgvector PVC (persistent volume claim)
- Clean up all resources in the namespace

### Complete Cleanup (Optional)

If you also want to delete the namespace itself:

```bash
oc delete project f5-ai-security
```

### Available Make Commands

```bash
make help              # Show all available commands
make install           # Deploy the application
make uninstall         # Remove the application
make clean             # Clean up all resources including namespace
make logs              # Show logs for all pods
make monitor           # Monitor deployment status
make validate-config   # Validate configuration values
```

## References 

<!-- 

*Section optional.* Remember to remove if do not use.

Include links to supporting information, documentation, or learning materials.

--> 

## Technical details

<!-- 

*Section is optional.* 

Here is your chance to share technical details. 

Welcome to add sections as needed. Keep additions as structured and consistent as possible.

-->

## Tags

<!-- CONTRIBUTOR TODO: add metadata and tags for publication

TAG requirements: 
	* Title: max char: 64, describes quickstart (match H1 heading) 
	* Description: max char: 160, match SHORT DESCRIPTION above
	* Industry: target industry, ie. Healthcare OR Financial Services
	* Product: list primary product, ie. OpenShift AI OR OpenShift OR RHEL 
	* Use case: use case descriptor, ie. security, automation, 
	* Contributor org: defaults to Red Hat unless partner or community
	
Additional MIST tags, populated by web team.

-->
