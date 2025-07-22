import logging
import os

from jupyterhub.auth import Authenticator
from traitlets import Unicode, List

from auth.kb_auth import KBaseAuth, MissingTokenError, AdminPermission

logger = logging.getLogger(__name__)





class KBaseAuthenticator(Authenticator):
    """
    Custom JupyterHub Authenticator for KBase.
    Authenticates users by verifying the 'kbase_session' cookie
    against the KBase Auth2 API.

    This requires `c.Authenticator.enable_auth_state` to be set to True in JupyterHub config.
    This also requires JUPYTERHUB_CRYPT_KEY to be set in the environment.
    """

    SESSION_COOKIE_NAME = "kbase_session"
    SESSION_COOKIE_BACKUP = "kbase_session_backup"

    kbase_auth_url = os.environ.get("KBASE_AUTH_URL", "https://ci.kbase.us/services/auth")

    auth_full_admin_roles = List(
        default_value=[
            role.strip() for role in os.getenv("AUTH_FULL_ADMIN_ROLES", "").split(",") if role.strip()
        ],
        config=True,
        help="Comma-separated list of KBase roles with full administrative access to JupyterHub."
    )

    async def authenticate(self, handler, data=None) -> dict:
        """
        Authenticate user using KBase session cookie and API validation

        """
        session_token = handler.get_cookie(self.SESSION_COOKIE_NAME)

        if not session_token:
            session_token = handler.get_cookie(self.SESSION_COOKIE_BACKUP)

        if not session_token:
            raise MissingTokenError(f"Authentication required - missing {self.SESSION_COOKIE_NAME} and {self.SESSION_COOKIE_BACKUP} cookie.")

        kb_auth = KBaseAuth(self.kbase_auth_url, self.auth_full_admin_roles)
        kb_user = await kb_auth.get_user(session_token)

        logger.info(f"Authenticated user: {kb_user.user}")
        return {
            "name": str(kb_user.user),
            "admin": kb_user.admin_perm == AdminPermission.FULL,
            "auth_state": {
                "kbase_token": session_token,
            }
        }

    async def pre_spawn_start(self, user, spawner) -> None:
        """
        Pass KBase authentication token to spawner environment
        """
        auth_state = await user.get_auth_state() or {}
        kbase_auth_token = auth_state.get("kbase_token")

        if not kbase_auth_token:
            raise MissingTokenError("Missing KBase authentication token in auth state")

        spawner.environment["KBASE_AUTH_TOKEN"] = kbase_auth_token
