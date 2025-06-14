# BERDL Custom JupyterHub Image

This document outlines key considerations and design decisions for the BERDL Custom JupyterHub Image, including answers to open questions regarding its configuration and deployment.

---

## Open Questions & Answers

### Cookie Secret (`JUPYTERHUB_COOKIE_SECRET`)

* **Purpose:** This secret is essential for JupyterHub to securely encrypt and decrypt user session cookies. This allows users to remain logged in across page refreshes and browser sessions (as long as the cookie is valid).
* **Persistence:** It **must be stable and persistent** across all JupyterHub restarts and deployments. If it changes, all existing user sessions will be immediately invalidated, forcing users to log in again.
* **Recommendation:** Generate a strong, random key once (e.g., using `openssl rand -hex 32`). Store this key securely as a Kubernetes `Secret` and then inject it as an environment variable named `JUPYTERHUB_COOKIE_SECRET` into your JupyterHub Deployment pod.

### Auth Secret (`JUPYTERHUB_CRYPT_KEY`)

* **Purpose:** This key is required for JupyterHub to encrypt and decrypt sensitive authentication state (`auth_state`) data (e.g., OAuth tokens) stored in its database. Spawners can then retrieve these details to configure the user's environment.
* **Persistence:** It **must be stable and persistent** across JupyterHub restarts and deployments, especially if `c.Authenticator.enable_auth_state` is set to `True`. If this key changes, any `auth_state` encrypted with the previous key becomes unreadable. This can break features relying on stored authentication data and may force users to re-authenticate.
* **Recommendation:** Similar to the cookie secret, generate a strong, random key once and store it securely as a Kubernetes `Secret`. Inject this secret as an environment variable named `JUPYTERHUB_CRYPT_KEY` into your JupyterHub Deployment pod.

### Database Persistence

* **Consequences of Wiping DB:** If the JupyterHub database is reset or deleted with every restart or deployment, you will **lose all persistent state** vital for JupyterHub's operation. This includes:
    * All user registrations, their associated IDs, and custom settings.
    * Group memberships.
    * The complete state and identity of all currently running user servers (Kubernetes pods).
    * All `last_activity` timestamps, which will disable idle culling for user pods.
    * Any stored `auth_state`.
    * This will lead to orphaned user pods in your Kubernetes cluster, making it impossible for JupyterHub to manage or stop them. Users will always be treated as new and unable to reconnect to existing sessions.
* **Recommendation:** **Always ensure database persistence for production or any long-lived JupyterHub deployment.**
    * **Default:** JupyterHub uses SQLite (`jupyterhub.sqlite`) by default. For Kubernetes, this requires mounting a **persistent volume** to the directory where `jupyterhub.sqlite` is stored.
    * **Production Standard:** For better robustness and scalability, it's highly recommended to use an external, persistent relational database like **PostgreSQL** or MySQL/MariaDB, configured via `c.JupyterHub.db_url`.

### Separate Proxy (JupyterHub's Internal Proxy)

* **Clarification:** You're asking about separating the **JupyterHub application process** itself from its **internal proxy component** (e.g., `configurable-http-proxy` or `traefik`) into different Docker containers.
* **Standard Practice:** For robust, scalable, and stable production deployments, it's **highly recommended and standard practice** to run the JupyterHub application and its internal proxy in **separate Kubernetes Deployments/Pods**.
* **Reasons for Separation:**
    * **Resource Management:** The Hub (a Python application) and the proxy (often a Node.js application like `configurable-http-proxy`) have different resource needs. Separating them allows for independent resource requests and limits, preventing one from starving the other.
    * **Scalability:** While the Hub is usually a single instance, the proxy can be scaled horizontally to handle more concurrent connections if needed, which isn't possible if they're coupled in one container.
    * **Stability & Isolation:** A crash or issue in one component (e.g., the Hub encounters an unhandled exception) is less likely to directly bring down the other. The proxy could continue routing traffic to active user servers or display an appropriate error page.
    * **Independent Updates/Maintenance:** Each component can be updated or restarted independently without affecting the other, reducing downtime during upgrades.
    * **Clearer Monitoring & Troubleshooting:** It's easier to monitor logs, metrics, and health checks for distinct services.
* **Typical Kubernetes Setup:** In a common Kubernetes deployment (e.g., via the `zero-to-jupyterhub-k8s` Helm chart), you'll typically find:
    * A `jupyterhub` Deployment/Pod running the main JupyterHub application.
    * A `proxy` Deployment/Pod running the `configurable-http-proxy` (or similar).
    * Kubernetes Services that enable these two components to discover and communicate with each other.
* **Conclusion:** Yes, if your current setup combines the Hub and its internal proxy into a single Docker container, you should separate them into distinct containers/Deployments for a more robust and maintainable production environment.

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
