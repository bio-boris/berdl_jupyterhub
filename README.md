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

| Variable                                 | Default Value                           | Description                                                                      |
|------------------------------------------|-----------------------------------------|----------------------------------------------------------------------------------|
| `AUTH_FULL_ADMIN_ROLES`                  | _(empty string)_                        | A comma-separated list of KBase roles to be granted full admin rights.           |
| `JUPYTERHUB_COOKIE_SECRET_64_HEX_CHARS`  | _(none)_                                | A 64-character hex string for securing user session cookies.                     |
| `JUPYTERHUB_CRYPT_KEY`                   | _(none)_                                | A 32-byte key for the authenticator to encrypt auth state.                       |
| `JUPYTERHUB_IDLE_TIMEOUT_SECONDS`        | `3600`                                  | Seconds of inactivity before a user's server is automatically shut down.         |
| `JUPYTERHUB_TEMPLATES_DIR`               | `/hub/berdl/auth/templates`             | The path to custom HTML templates for login.                                     |
| `KBASE_AUTH_URL`                         | `https://ci.kbase.us/services/auth`     | The URL for the KBase authentication service.                                    |
| `KBASE_ORIGIN`                           | `https://ci.kbase.us`                   | The KBase service URL used by the auth login html.                               |
| `NODE_SELECTOR_HOSTNAME`                 | _(none)_                                | If set, forces user notebook pods to be scheduled on a specific Kubernetes node. |
| `BERDL_NOTEBOOK_IMAGE_TAG`               | `ghcr.io/bio-boris/berdl_notebook:pr-1` | The tag of the BERDL notebook image to use for user servers.                     |
---

**Note**: Variables with a default value of `_(none)_` **must be set at runtime**. All other variables are optional and will use their default if not provided.


# abc123
This document outlines key considerations and design decisions for the BERDL Custom JupyterHub Image, including answers to open questions regarding its configuration and deployment.

---
* Need to put jupyterhub_cookie_secret into secret
* Need to put minio keys into secret, etc.
* Need to mount sqlite database onto specific volume due to restarts
* Considerate Separate configurable-http-proxy Proxy 



### Spawner Method Separation (KubeSpawner vs. Notebook Server)

To improve separation of concerns, some methods can be shifted from the `CustomKubeSpawner` (running in the Hub pod) into the single-user notebook server's Docker image (executed via its `ENTRYPOINT` script or an `initContainer`).

* **Methods to Consider Moving to the Single-User Docker Image / Entrypoint / InitContainer:**
    * **Static Directory Setup:** Creation of consistent, non-user-specific subdirectories within the user's home (e.g., the basic `.jupyter` directory structure like `runtime` and `data`).
    * **Templated Dotfiles:** Copying of default shell configuration files (like `.bashrc`, `.bash_profile`) from templates within the image to the user's mounted home directory.
    * **Base Virtual Environment Creation:** The `venv.create()` call, as this operation occurs *within* the user's persistent volume and doesn't require elevated Hub-level permissions.
    * **JupyterLab Favorites Setup:** The logic to add or update `favorites.jupyterlab-settings` entries, as this involves manipulating files within the user's persistent volume.
    * **Static Environment Variables:** Any `ENV` variables that are universal and don't change with each spawn (e.g., `JUPYTER_MODE`, `SHELL`, base `PATH`).

* **Methods That Must Remain in `CustomKubeSpawner` (Hub Pod):**
    * **Kubernetes Pod Specification:** Defining `volumes` and `volume_mounts` is a core function of `KubeSpawner`, directly controlling how Kubernetes creates and configures the user's pod.
    * **Dynamic Environment Variables:** Setting environment variables that are unique per-user, involve sensitive secrets, or depend on dynamically provisioned resources (e.g., `JUPYTERHUB_USER`, `SPARK_MASTER_URL`, Minio credentials).
    * **External Service Provisioning/Deprovisioning:** The creation and deletion of external services like your Spark cluster (`_start_spark_cluster`, `_stop_spark_cluster`) must remain in the Hub's Spawner, as it interacts with external APIs and requires Hub-level permissions.
    * **User/Server Lifecycle Management:** Logic for idle culling (`poll`), determining admin status for resource allocation, or handling user/group-based logic that directly affects the *Kubernetes pod specification* for a user.

---
