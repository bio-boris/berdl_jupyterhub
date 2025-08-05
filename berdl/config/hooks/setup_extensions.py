import os

# TODO FIX THIS TO CALL THE MINIO GOVERNANCE API


def setup_minio_credentials(spawner):
    """
    Setup MinIO credentials for the user's environment.
    """
    minio_access_key = os.environ.get("MINIO_ACCESS_KEY", "minioadmin")
    minio_secret_key = os.environ.get("MINIO_SECRET_KEY", "minioadmin")
    minio_endpoint = os.environ.get("MINIO_ENDPOINT", "minio:9000")
    minio_secure = os.environ.get("MINIO_SECURE", "false").lower() == "true"

    spawner.environment.update(
        {
            "MINIO_ACCESS_KEY": minio_access_key,
            "MINIO_SECRET_KEY": minio_secret_key,
            "MINIO_ENDPOINT": minio_endpoint,
            "MINIO_SECURE": str(minio_secure).lower(),
        }
    )
    spawner.log.info(
        f"MinIO credentials set for user {spawner.user.name}: "
        f"Endpoint: {minio_endpoint}, Secure: {minio_secure}"
    )
