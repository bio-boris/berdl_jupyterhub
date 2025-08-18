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

### Required Variables

| Variable                                | Description                                                                      |
|-----------------------------------------|----------------------------------------------------------------------------------|
| `JUPYTERHUB_COOKIE_SECRET_64_HEX_CHARS` | A 64-character hex string for securing user session cookies.                     |
| `JUPYTERHUB_TEMPLATES_DIR`              | The path to custom HTML templates for login.                                     |
| `KBASE_ORIGIN`                          | The KBase service URL used by the auth login html.                               |
| `KBASE_AUTH_URL`                        | The URL for the KBase authentication service.                                    |
| `CDM_TASK_SERVICE_URL`                  | The URL for the CTS service.                                                     |
| `GOVERNANCE_API_URL`                    | The URL for the Governance API.                                                  |
| `MINIO_ENDPOINT_URL`                    | The endpoint URL for the MinIO object storage service.                           |
| `SPARK_CLUSTER_MANAGER_API_URL`         | The URL for the Spark Cluster Manager API.                                       |
| `BERDL_HIVE_METASTORE_URI`              | The URI for the Hive Metastore service.                                          |

### Optional Variables

| Variable                                | Default Value                           | Description                                                                      |
|-----------------------------------------|-----------------------------------------|----------------------------------------------------------------------------------|
| `AUTH_FULL_ADMIN_ROLES`                 | _(empty string)_                        | A comma-separated list of KBase roles to be granted full admin rights.           |
| `JUPYTERHUB_CRYPT_KEY`                  | _(none)_                                | A 32-byte key for the authenticator to encrypt auth state.                       |
| `JUPYTERHUB_IDLE_TIMEOUT_SECONDS`       | `3600`                                  | Seconds of inactivity before a user's server is automatically shut down.         |
| `NODE_SELECTOR_HOSTNAME`                | _(none)_                                | If set, forces user notebook pods to be scheduled on a specific Kubernetes node. |
| `BERDL_NOTEBOOK_IMAGE_TAG`              | `ghcr.io/bio-boris/berdl_notebook:pr-1` | The tag of the BERDL notebook image to use for user servers.                     |
| `MINIO_SECURE_FLAG`                     | `True`                                  | Whether to use HTTPS for MinIO connections.                                      |
| `JUPYTERHUB_DEBUG`                      | `False`                                 | Enable debug mode for JupyterHub.                                                |
| `JUPYTERHUB_LOG_LEVEL`                  | `INFO`                                  | Set JupyterHub log level (DEBUG, INFO, WARN, ERROR).                             |
| `ENABLE_IDLE_CULLER`                    | `True`                                  | Enable idle culler for JupyterHub.                                               |
| `JUPYTERHUB_MEM_LIMIT_GB`               | `4`                                     | Memory limit in GB for JupyterHub user containers.                               |
| `JUPYTERHUB_MEM_GUARANTEE_GB`           | `2`                                     | Memory guarantee in GB for JupyterHub user containers.                           |
| `JUPYTERHUB_CPU_LIMIT`                  | `2`                                     | CPU limit (cores) for JupyterHub user containers.                                |
| `DEFAULT_MASTER_CORES`                  | `1`                                     | Default master cores for Spark clusters.                                         |
| `DEFAULT_MASTER_MEMORY`                 | `2g`                                    | Default master memory for Spark clusters.                                        |
| `DEFAULT_WORKER_COUNT`                  | `2`                                     | Default number of worker nodes for Spark clusters.                               |
| `DEFAULT_WORKER_CORES`                  | `1`                                     | Default worker cores for Spark clusters.                                         |
| `DEFAULT_WORKER_MEMORY`                 | `2g`                                    | Default worker memory for Spark clusters.                                        |

---

**Note**: All required variables **must be set at runtime**. Optional variables will use their default values if not provided.

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