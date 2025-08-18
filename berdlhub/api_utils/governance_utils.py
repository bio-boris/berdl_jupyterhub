import os
import httpx
from typing import Any


class GovernanceUtils:
    """
    A utility class to manage MinIO credentials for a JupyterHub spawner.
    """

    # --- Configuration Constants to be read from the Hub's environment ---
    GOVERNANCE_API_URL_ENV = "GOVERNANCE_API_URL"
    MINIO_ENDPOINT_URL_ENV = "MINIO_ENDPOINT_URL"
    MINIO_SECURE_ENV = "MINIO_SECURE_FLAG"

    # --- Environment variables to be set IN the spawner for the notebook env ---
    MINIO_ACCESS_KEY = "MINIO_ACCESS_KEY"
    MINIO_SECRET_KEY = "MINIO_SECRET_KEY"
    MINIO_ENDPOINT = "MINIO_ENDPOINT"
    MINIO_SECURE = "MINIO_SECURE"
    MINIO_CONFIG_ERROR = "MINIO_CONFIG_ERROR"

    @staticmethod
    async def set_governance_credentials(spawner, kbase_auth_token) -> None:
        """Main method to fetch credentials and mutate and update the spawner's environment."""
        try:
            gov_url = os.environ[GovernanceUtils.GOVERNANCE_API_URL_ENV]
            minio_endpoint_url = os.environ[GovernanceUtils.MINIO_ENDPOINT_URL_ENV]
            headers = {"Authorization": f"Bearer {kbase_auth_token}"}

            async with httpx.AsyncClient() as client:
                response = await client.get(f"{gov_url}/credentials/", headers=headers)
                response.raise_for_status()
                credentials = response.json()

            spawner.environment[GovernanceUtils.MINIO_ACCESS_KEY] = credentials[
                "access_key"
            ]
            spawner.environment[GovernanceUtils.MINIO_SECRET_KEY] = credentials[
                "secret_key"
            ]
            spawner.environment[GovernanceUtils.MINIO_ENDPOINT] = minio_endpoint_url
            spawner.environment[GovernanceUtils.MINIO_SECURE] = os.environ.get(
                GovernanceUtils.MINIO_SECURE_ENV, "True"
            )
            spawner.environment.pop(GovernanceUtils.MINIO_CONFIG_ERROR, None)
            spawner.log.info(
                "Successfully set MinIO credentials for user %s.", spawner.user.name
            )

        except (httpx.RequestError, RuntimeError) as e:
            # --- Graceful Failure Path (for API/auth errors ONLY) ---
            spawner.log.error(
                "Failed to get governance credentials for user %s. Notebook will start with empty credentials.",
                spawner.user.name,
                exc_info=True,  # This will print the full exception traceback.
            )

            spawner.environment[GovernanceUtils.MINIO_ACCESS_KEY] = ""
            spawner.environment[GovernanceUtils.MINIO_SECRET_KEY] = ""
            spawner.environment[GovernanceUtils.MINIO_ENDPOINT] = ""
            spawner.environment[GovernanceUtils.MINIO_SECURE] = "False"
            spawner.environment[GovernanceUtils.MINIO_CONFIG_ERROR] = (
                "Failed to retrieve MinIO credentials. Please contact an administrator."
            )
