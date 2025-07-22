# BERDL Custom JupyterHub Image


# ENV VARS

* KBASE_AUTH_URL
* KBASE_ORIGIN


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
