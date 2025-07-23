import os
from berdl.auth.kb_jupyterhub_auth import KBaseAuthenticator

c = get_config()

# ==============================================================================
# ## Hub Configuration
# General settings for the JupyterHub application itself.
# ==============================================================================
c.JupyterHub.ip = '0.0.0.0'
c.JupyterHub.cookie_secret = bytes.fromhex(os.environ['JUPYTERHUB_COOKIE_SECRET_64_HEX_CHARS'])

# Paths for custom HTML templates
c.JupyterHub.template_paths = [os.environ['JUPYTERHUB_TEMPLATES_DIR']]
c.JupyterHub.template_vars = {
    'kbase_origin': os.environ['KBASE_ORIGIN'],
}


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
c.JupyterHub.spawner_class = 'kubespawner.KubeSpawner'

# --- Pod Definition ---
# Defines the contents and metadata of the user's pod.
c.KubeSpawner.image = os.environ.get('JUPYTERHUB_USER_IMAGE', 'ghcr.io/bio-boris/berdl_notebook:main')
c.KubeSpawner.labels = {"app": "berdl-notebook"}

# --- Lifecycle and Culling ---
# Manages how pods start, stop, and are culled when idle.
c.KubeSpawner.start_timeout = 300  # 5 minutes
c.KubeSpawner.http_timeout = 120   # 2 minutes
c.KubeSpawner.delete_stopped_pods = True

# Pass arguments to the user server for self-culling
c.KubeSpawner.args = [
    '--ServerApp.shutdown_no_activity_timeout=3600', # Shutdown server after 1hr of no activity
    '--MappingKernelManager.cull_idle_timeout=1200'  # Shutdown kernels after 20min of no activity
]

# --- Kubernetes Specifics ---
# Networking and scheduling settings for Kubernetes.
c.KubeSpawner.hub_connect_url = 'http://jupyterhub:8000'
c.KubeSpawner.debug = True

# Set a node selector if the environment variable is present
node_hostname = os.environ.get("NODE_SELECTOR_HOSTNAME")
if node_hostname:
    c.KubeSpawner.node_selector = {"kubernetes.io/hostname": node_hostname}



# --- Resource Management ---

# Parameterize memory settings (user provides a number, code adds unit)
mem_limit_gb = os.environ.get('JUPYTERHUB_MEM_LIMIT_GB', '4')
mem_guarantee_gb = os.environ.get('JUPYTERHUB_MEM_GUARANTEE_GB', '1')
c.KubeSpawner.mem_limit = f"{mem_limit_gb}G"
c.KubeSpawner.mem_guarantee = f"{mem_guarantee_gb}G"

# Parameterize CPU settings (user provides a number)
cpu_limit = os.environ.get('JUPYTERHUB_CPU_LIMIT', '2.0')
cpu_guarantee = os.environ.get('JUPYTERHUB_CPU_GUARANTEE', '0.5') # Added this line
c.KubeSpawner.cpu_limit = float(cpu_limit)
c.KubeSpawner.cpu_guarantee = float(cpu_guarantee) # Added this line


# This goes at the top level of the config, outside the spawner if/else block

# --- Service for Culling Idle Servers ---
c.JupyterHub.services = [
    {
        'name': 'idle-culler',
        'admin': True,
        'command': [
            'python3',
            '-m', 'jupyterhub_idle_culler',
            '--timeout=3600',      # Shutdown servers after 1 hour of inactivity
            '--cull-every=600'     # Check for idle servers every 10 minutes
        ],
    }
]

# --- User-Selectable Profiles ---
c.KubeSpawner.profile_list = [
    {
        'display_name': 'Small Server (2G RAM, 1 CPU)',
        'default': True,
        'kubespawner_override': {
            'mem_limit': '2G',
            'mem_guarantee': '1G',
            'cpu_limit': 1,
            'cpu_guarantee': 0.5
        }
    },
    {
        'display_name': 'Medium Server (8G RAM, 2 CPU)',
        'kubespawner_override': {
            'mem_limit': '8G',
            'mem_guarantee': '4G',
            'cpu_limit': 2,
            'cpu_guarantee': 1
        }
    },
    {
        'display_name': 'Large Server (32G RAM, 4 CPU)',
        'kubespawner_override': {
            'mem_limit': '32G',
            'mem_guarantee': '16G',
            'cpu_limit': 4,
            'cpu_guarantee': 2
        }
    }
]