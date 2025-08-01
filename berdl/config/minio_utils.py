def set_credentials(spawner) -> dict:
    """
    Retrieve MinIO credentials from the spawner's environment.
    """
    outside_service_creds = {
        "MINIO_ACCESS_KEY": "123",
        "MINIO_SECRET_KEY": "123",
    }

    spawner.environment["MINIO_ACCESS_KEY"] = outside_service_creds["MINIO_ACCESS_KEY"]
    spawner.environment["MINIO_SECRET_KEY"] = outside_service_creds["MINIO_SECRET_KEY"]
    spawner.log.info(
        f"Set MinIO credentials for user {spawner.user.name} "
        f"Access Key: {outside_service_creds['MINIO_ACCESS_KEY']}, "
        f"Secret Key: {outside_service_creds['MINIO_SECRET_KEY']}"
    )
