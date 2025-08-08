# BERDL JupyterHub on Kubernetes

This project provides the necessary configuration to build and deploy a JupyterHub instance on Kubernetes for the BERDL project.

It uses `KubeSpawner` to launch user notebook servers as individual Kubernetes pods and authenticates users against KBase. The entire application is packaged into a self-contained Docker image for easy deployment.

---

## Features

* **Kubernetes Native**: Deploys directly to a Kubernetes cluster, with user servers running in isolated pods.
* **Dynamic User Servers**: Uses `KubeSpawner` to dynamically create and manage notebook servers.
* **KBase Authentication**: Integrates with KBase for user authentication.
* **Selectable Server Profiles**: Users can choose from pre-defined server sizes (Small, Medium, Large) with different resource allocations.
* **Idle Server Culling**: Automatically shuts down user servers after a period of inactivity to conserve resources.
* **Self-Contained Image**: All code, dependencies, and configurations are bundled into a single Docker image.


## ⚙️ Runtime Configuration

The container is configured at runtime using the following environment variables.

| Variable                                | Default Value                           | Description                                                                      |
|-----------------------------------------|-----------------------------------------|----------------------------------------------------------------------------------|
| `AUTH_FULL_ADMIN_ROLES`                 | _(empty string)_                        | A comma-separated list of KBase roles to be granted full admin rights.           |
| `JUPYTERHUB_COOKIE_SECRET_64_HEX_CHARS` | _(none)_                                | A 64-character hex string for securing user session cookies.                     |
| `JUPYTERHUB_CRYPT_KEY`                  | _(none)_                                | A 32-byte key for the authenticator to encrypt auth state.                       |
| `JUPYTERHUB_IDLE_TIMEOUT_SECONDS`       | `3600`                                  | Seconds of inactivity before a user's server is automatically shut down.         |
| `JUPYTERHUB_TEMPLATES_DIR`              | `/hub/berdl/auth/templates`             | The path to custom HTML templates for login.                                     |
| `KBASE_AUTH_URL`                        | `https://ci.kbase.us/services/auth`     | The URL for the KBase authentication service.                                    |
| `KBASE_ORIGIN`                          | `https://ci.kbase.us`                   | The KBase service URL used by the auth login html.                               |
| `NODE_SELECTOR_HOSTNAME`                | _(none)_                                | If set, forces user notebook pods to be scheduled on a specific Kubernetes node. |
| `BERDL_NOTEBOOK_IMAGE_TAG`              | `ghcr.io/bio-boris/berdl_notebook:pr-1` | The tag of the BERDL notebook image to use for user servers.                     |
| `SPARK_CLUSTER_MANAGER_API_URL`         | _(none)_                                | The URL for the Spark Cluster Manager API.                                       |
| `GOVERNANCE_API_URL`                    | _(none)_                                | The URL for the Governance API.                                                  |
| `MINIO_ENDPOINT`                      | _(none)_                                | The endpoint for the MinIO object storage service.                                |
 | `MINIO_SECURE_FLAG`                  | _(none)_`                               | Whether to use HTTPS for MinIO connections.                                      |
---


**Note**: Variables with a default value of `_(none)_` **must be set at runtime**. All other variables are optional and will use their default if not provided.


# User Guide
# TODO Move to the notebook image repo
-- Users must install with pip install --user to preserve


# Future Work and Known Issues

---
* Consider backing up the sqlite database
* Considerate Separate configurable-http-proxy Proxy
* Test Environment setup
* All hub data is not backed up, and saved to a single mount on the host
* Only one host is supported at this time.
* Make sure all env vars are documented