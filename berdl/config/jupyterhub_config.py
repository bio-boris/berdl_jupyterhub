import os

import berdl.config.hooks.kubespawner_hooks
from berdl.auth.kb_jupyterhub_auth import KBaseAuthenticator
from berdl.config.hooks import pre_spawn_hook, post_stop_hook, modify_pod_hook


c = get_config()

# ==============================================================================
# ## Hub Configuration
# General settings for the JupyterHub application itself.
# ==============================================================================
c.JupyterHub.ip = "0.0.0.0"
c.JupyterHub.cookie_secret = bytes.fromhex(
    os.environ["JUPYTERHUB_COOKIE_SECRET_64_HEX_CHARS"]
)

# Paths for custom HTML templates
c.JupyterHub.template_paths = [os.environ["JUPYTERHUB_TEMPLATES_DIR"]]
c.JupyterHub.template_vars = {
    "kbase_origin": os.environ["KBASE_ORIGIN"],
}
# Don't delete servers on restart!
c.JupyterHub.cleanup_servers = False


# ==============================================================================
# ## Authenticator Configuration
# How users will log in to JupyterHub.
# ==============================================================================
c.JupyterHub.authenticator_class = KBaseAuthenticator
# Requires JUPYTERHUB_CRYPT_KEY environment variable to be set
c.Authenticator.enable_auth_state = True
# Allows any user with a valid KBASE token to log in
c.Authenticator.allow_all = True


# ==============================================================================
# ## Spawner Configuration
# How JupyterHub creates and manages individual user notebook servers.
# ==============================================================================
c.JupyterHub.spawner_class = "kubespawner.KubeSpawner"
c.KubeSpawner.image_pull_policy = "Always"

# --- Pod Definition ---
# Defines the contents and metadata of the user's pod.
# c.KubeSpawner.image = os.environ.get('JUPYTERHUB_USER_IMAGE', 'ghcr.io/bio-boris/berdl_notebook:main')
c.KubeSpawner.extra_labels = {"app": "berdl-notebook"}
# Add NBUSER environment variable to the pod
# See https://jupyterhub-kubespawner.readthedocs.io/en/latest/templates.html for template variables


# BERDL Specific Environment Variables
c.KubeSpawner.environment = {
    "KBASE_ORIGIN": os.environ["KBASE_ORIGIN"],
    "SPARK_JOB_LOG_DIR_CATEGORY": "{username}",
}
# https://jupyter-docker-stacks.readthedocs.io/en/latest/using/common.html#user-related-configurations
c.KubeSpawner.environment.update(
    {"NB_USER": "{username}", "CHOWN_HOME": "yes", "GEN_CERT": "yes"}
)
# Change working directory to the user's home directory
c.KubeSpawner.notebook_dir = "/home/{username}"
# Set root dir to be the root directory of the pod and set the default URL to JupyterLab
c.KubeSpawner.cmd = ["start-notebook.sh"]
c.KubeSpawner.args = [
    "--ServerApp.root_dir=/",
    "--ServerApp.default_url=/lab",  # Uncomment to set default URL to JupyterLab
]

# TODO, add post start hook to inject minio credentials into the pod


# --- Lifecycle and Culling ---
# Manages how pods start, stop, and are culled when idle.
c.KubeSpawner.start_timeout = 300  # 5 minutes
c.KubeSpawner.http_timeout = 120  # 2 minutes
c.KubeSpawner.delete_stopped_pods = True

# --- Kubernetes Specifics ---
# Networking and scheduling settings for Kubernetes.
c.KubeSpawner.hub_connect_url = "http://jupyterhub:8000"
c.KubeSpawner.port = 8888  # To help avoid collision with other services
# c.KubeSpawner.services_enabled = True  # TODO TEST THIS


# Debugging
c.KubeSpawner.debug = True
c.JupyterHub.log_level = "DEBUG"


# --- Resource Management ---
# Parameterize memory settings (user provides a number, code adds unit)
mem_limit_gb = os.environ.get("JUPYTERHUB_MEM_LIMIT_GB", "4")
mem_guarantee_gb = os.environ.get("JUPYTERHUB_MEM_GUARANTEE_GB", "1")
c.KubeSpawner.mem_limit = f"{mem_limit_gb}G"
c.KubeSpawner.mem_guarantee = f"{mem_guarantee_gb}G"

# Parameterize CPU settings (user provides a number)
cpu_limit = os.environ.get("JUPYTERHUB_CPU_LIMIT", "2.0")
cpu_guarantee = os.environ.get("JUPYTERHUB_CPU_GUARANTEE", "0.5")
c.KubeSpawner.cpu_limit = float(cpu_limit)
c.KubeSpawner.cpu_guarantee = float(cpu_guarantee)


timeout = os.environ.get("JUPYTERHUB_IDLE_TIMEOUT_SECONDS", "3600")
c.JupyterHub.services = [
    {
        "name": "idle-culler",
        "admin": True,
        "command": [
            "python3",
            "-m",
            "jupyterhub_idle_culler",
            f"--timeout={timeout}",  # Shutdown servers after inactivity
            "--cull-every=600",  # Check for idle servers every 10 minutes
        ],
    }
]


berdl_notebook_image_tag = os.environ.get(
    "BERDL_NOTEBOOK_IMAGE_TAG", "ghcr.io/bio-boris/berdl_notebook:main"
)

# --- User-Selectable Profiles ---
c.KubeSpawner.profile_list = [
    {
        "display_name": "Small Server (2G RAM, 1 CPU)",
        "default": True,
        "kubespawner_override": {
            "mem_limit": "2G",
            "mem_guarantee": "1G",
            "cpu_limit": 1,
            "cpu_guarantee": 0.5,
            "image": "jupyter/base-notebook:latest",
        },
    },
    {
        "display_name": "Medium Server (8G RAM, 2 CPU) w quay.io/jupyter/pyspark-notebook:spark-4.0.0",
        "kubespawner_override": {
            "mem_limit": "8G",
            "mem_guarantee": "4G",
            "cpu_limit": 2,
            "cpu_guarantee": 1,
            "image": "quay.io/jupyter/pyspark-notebook:spark-4.0.0",
        },
    },
    {
        "display_name": f"Large Server (32G RAM, 4 CPU) with {berdl_notebook_image_tag}",
        "kubespawner_override": {
            "mem_limit": "32G",
            "mem_guarantee": "16G",
            "cpu_limit": 4,
            "cpu_guarantee": 2,
            "image": f"{berdl_notebook_image_tag}",
        },
    },
]

# Storage
# For now, we are binding workers to kworker02. We can investigate other solutions for storage
# These mounts below are dependent on the kworker02 node having the /mnt/state/hub/{username} and /mnt/state/hub/global_share directories
# Mount /home/user/ from /mnt/state/hub/user for each notebook
# This also stops us from scaling the number of notebook containers due to specifying the "cpu_guarantee" and "mem_guarantee" parameters
# The specs of kworker02 are: 168 cores, 1TB RAM, 11.TB  storage


node_hostname = os.environ.get("NODE_SELECTOR_HOSTNAME", "kworker02")
if node_hostname:
    c.KubeSpawner.node_selector = {"kubernetes.io/hostname": node_hostname}


c.KubeSpawner.volumes = [
    {
        "name": "user-home",
        "hostPath": {"path": "/mnt/state/hub/{username}", "type": "DirectoryOrCreate"},
    },
    {
        "name": "user-global",
        "hostPath": {
            "path": "/mnt/state/hub/global_share",
            "type": "DirectoryOrCreate",
        },
    },
]
c.KubeSpawner.volume_mounts = [
    {"name": "user-home", "mountPath": "/home/{username}"},
    {"name": "user-global", "mountPath": "/global_share"},
]
# Set permissions on the volume mounts
# c.KubeSpawner.

# Add extra options for the pod template to disable "enableServiceLinks"
# TODO ADD POD IP
c.KubeSpawner.extra_pod_config = {
    "enableServiceLinks": False,
}


# The default command runs 'start-notebook.sh', which passes these args along.

# Hooks for pre-spawn and post-stop actions
c.KubeSpawner.pre_spawn_hook = pre_spawn_hook
c.KubeSpawner.post_spawn_hook = post_stop_hook
c.KubeSpawner.modify_pod_hook = modify_pod_hook
