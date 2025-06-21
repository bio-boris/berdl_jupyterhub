from jupyterhub_customizations.kb_jupyterhub_auth import KBaseAuthenticator, kbase_origin
import os

c = get_config()

# Authenticator
c.JupyterHub.authenticator_class = KBaseAuthenticator
c.Authenticator.enable_auth_state = True
# ref: https://jupyterhub.readthedocs.io/en/latest/reference/api/auth.html#jupyterhub.auth.Authenticator.allow_all
c.Authenticator.allow_all = True
# Enable authentication state persistence
c.JupyterHub.template_paths = [os.environ['JUPYTERHUB_TEMPLATES_DIR']]
c.JupyterHub.template_vars = {
    'kbase_origin': os.environ['KBASE_ORIGIN'],
}


# General
c.JupyterHub.ip = '0.0.0.0'






# c.JupyterHub.cookie_secret_file = f"{os.environ['JUPYTERHUB_SECRETS_DIR']}/jupyterhub_cookie_secret"
# c.JupyterHub.db_url = f"sqlite:///{os.environ['JUPYTERHUB_SECRETS_DIR']}/jupyterhub.sqlite"

