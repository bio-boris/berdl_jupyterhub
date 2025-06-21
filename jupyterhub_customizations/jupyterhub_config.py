from jupyterhub_customizations.kb_jupyterhub_auth import KBaseAuthenticator

c = get_config()

# Authenticator
c.JupyterHub.authenticator_class = KBaseAuthenticator
c.Authenticator.enable_auth_state = True
c.Authenticator.allow_all = True

# General
c.JupyterHub.ip = '0.0.0.0'


# Enable authentication state persistence
# c.JupyterHub.template_paths = [os.environ['JUPYTERHUB_TEMPLATES_DIR']]
#     c.JupyterHub.template_vars = {
#         'kbase_origin': f'https://{kbase_origin()}'
#     }

# ref: https://jupyterhub.readthedocs.io/en/latest/reference/api/auth.html#jupyterhub.auth.Authenticator.allow_all


# c.JupyterHub.cookie_secret_file = f"{os.environ['JUPYTERHUB_SECRETS_DIR']}/jupyterhub_cookie_secret"
# c.JupyterHub.db_url = f"sqlite:///{os.environ['JUPYTERHUB_SECRETS_DIR']}/jupyterhub.sqlite"

