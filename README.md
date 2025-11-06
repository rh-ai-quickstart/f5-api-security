# Securing Model Inference with F5 Distributed Cloud API Security

<!-- CONTRIBUTOR TODO: update title ^^

*replace the H1 title above with your quickstart title*

TITLE requirements:
	* MAX CHAR: 64 
	* Industry use case, ie: Protect patient data with LLM guardrails

TITLE will be extracted for publication.

-- > 



<!-- CONTRIBUTOR TODO: short description 

*ADD a SHORT DESCRIPTION of your use case between H1 title and next section*

SHORT DESCRIPTION requirements:
	* MAX CHAR: 160
	* Describe the INDUSTRY use case 

SHORT DESCRIPTION will be extracted for publication.

--> 


## Table of contents

<!-- Table of contents is optional, but recommended. 

REMEMBER: to remove this section if you don't use a TOC.

-->

## Detailed description

This QuickStart shows how to protect AI inference endpoints on Red Hat OpenShift AI using F5 Distributed Cloud (XC) Web App & API Protection (WAAP) + API Security. You’ll deploy a KServe/vLLM model service in OpenShift AI, front it with an F5 XC HTTP Load Balancer, and enforce API discovery, OpenAPI schema validation, rate limiting, bot defense, and sensitive-data controls—without changing your ML workflow. OpenShift AI’s single-model serving is KServe-based (recommended for LLMs), and KServe’s HuggingFace/vLLM runtime exposes OpenAI-compatible endpoints, which we’ll secure via F5 XC

Key Components

- Red Hat OpenShift AI – Unified MLOps platform for developing and inference models at scale.
- F5 Distributed Cloud API Security – Provides LLM-aware threat detection, schema validation, and sensitive data redaction.
- Integration Blueprint – Demonstrates secure model inference across hybrid environments


### See it in action 

<!-- 

*This section is optional but recommended*

Arcades are a great way to showcase your quickstart before installation.

-->

### Architecture diagrams

<!-- CONTRIBUTOR TODO: add architecture diagram. 

*Section is required. Put images in `docs/images` folder* 

--> 


## Requirements


### Minimum hardware requirements 

<!-- CONTRIBUTOR TODO: add minimum hardware requirements

*Section is required.* 

Be as specific as possible. DON'T say "GPU". Be specific.

List minimum hardware requirements.

--> 

### Minimum software requirements

<!-- CONTRIBUTOR TODO: add minimum software requirements

*Section is required.*

Be specific. Don't say "OpenShift AI". Instead, tested with OpenShift AI 2.22

If you know it only works in a specific version, say so. 

-->

### Required user permissions

<!-- CONTRIBUTOR TODO: add user permissions

*Section is required. Describe the permissions the user will need. Cluster
admin? Regular user?*

--> 


## Deploy

<!-- CONTRIBUTOR TODO: add installation instructions 

*Section is required. Include the explicit steps needed to deploy your
quickstart. 

Assume user will follow your instructions EXACTLY. 

If screenshots are included, remember to put them in the
`docs/images` folder.*

-->

### Delete

<!-- CONTRIBUTOR TODO: add uninstall instructions

*Section required. Include explicit steps to cleanup quickstart.*

Some users may need to reclaim space by removing this quickstart. Make it easy.

-->

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
