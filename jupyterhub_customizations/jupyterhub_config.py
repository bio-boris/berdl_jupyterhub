from jupyterhub_customizations.kb_jupyterhub_auth import KBaseAuthenticator, kbase_origin
import os

c = get_config()

# Authenticator


c.JupyterHub.authenticator_class = KBaseAuthenticator
# Requires JUPYTERHUB_CRYPT_KEY environment variable to be set
c.Authenticator.enable_auth_state = True
# ref: https://jupyterhub.readthedocs.io/en/latest/reference/api/auth.html#jupyterhub.auth.Authenticator.allow_all
# Anyone with a KBASE token can log in
c.Authenticator.allow_all = True
# Enable authentication state persistence
c.JupyterHub.template_paths = [os.environ['JUPYTERHUB_TEMPLATES_DIR']]
c.JupyterHub.template_vars = {
    'kbase_origin': os.environ['KBASE_ORIGIN'],
}


# General
#
# The /jupyterhub.sqlite db needs to be persisted
c.JupyterHub.ip = '0.0.0.0'
c.JupyterHub.cookie_secret = bytes.fromhex(os.environ['JUPYTERHUB_COOKIE_SECRET_64_HEX_CHARS'])

# Idle Behavior
c.JupyterHub.spawner_class = 'kubespawner.KubeSpawner'


# shutdown the server after no activity for an hour
c.ServerApp.shutdown_no_activity_timeout = 60 * 60
# shutdown kernels after no activity for 20 minutes
c.MappingKernelManager.cull_idle_timeout = 20 * 60
# check for idle kernels every two minutes
c.MappingKernelManager.cull_interval = 2 * 60
