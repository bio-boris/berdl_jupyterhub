"""Validate required environment variables."""

import os
import sys


def validate_environment():
    """Validate that all required environment variables are set."""

    required_vars = {
        # Core JupyterHub
        "JUPYTERHUB_COOKIE_SECRET_64_HEX_CHARS": "64 character hex string for cookies",
        "JUPYTERHUB_TEMPLATES_DIR": "Path to JupyterHub templates",
        # KBase integration
        "KBASE_ORIGIN": "KBase origin URL",
        # Services
        "CDM_TASK_SERVICE_URL": "CDM task service endpoint",
        "SPARK_CLUSTER_MANAGER_API_URL": "Spark cluster manager API",
        "BERDL_HIVE_METASTORE_URI": "Hive metastore URI",
    }

    optional_vars = {
        "NODE_SELECTOR_HOSTNAME": "Kubernetes node hostname",
        "STORAGE_TYPE": "Storage type (hostpath/pvc/nfs)",
        "MINIO_ACCESS_KEY": "MinIO access key",
        "MINIO_SECRET_KEY": "MinIO secret key",
        "ENABLE_GPU_SUPPORT": "Enable GPU support (true/false)",
    }

    # Check required variables
    missing = []
    for var, description in required_vars.items():
        if var not in os.environ:
            missing.append(f"  - {var}: {description}")

    if missing:
        print("ERROR: Missing required environment variables:", file=sys.stderr)
        print("\n".join(missing), file=sys.stderr)
        sys.exit(1)

    # Log optional variables
    print("Environment validation successful!")
    print("\nOptional variables status:")
    for var, description in optional_vars.items():
        status = "✓ Set" if var in os.environ else "✗ Not set"
        print(f"  {status}: {var} ({description})")
