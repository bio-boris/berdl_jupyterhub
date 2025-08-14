import os
import sys


def validate_environment():
    """Validate that all required environment variables are set."""

    required_vars = {
        "Core JupyterHub": {
            "JUPYTERHUB_COOKIE_SECRET_64_HEX_CHARS": "64 character hex string for cookies",
            "JUPYTERHUB_TEMPLATES_DIR": "Path to JupyterHub templates",
        },
        "KBase Integration": {
            "KBASE_ORIGIN": "KBase origin URL",
            "KBASE_AUTH_URL": "KBase authentication service URL",
        },
        "ServiceUrls": {
            "CDM_TASK_SERVICE_URL": "CDM task service endpoint",
            "GOVERNANCE_API_URL": "Governance API endpoint",
            "MINIO_ENDPOINT_URL": "MinIO endpoint URL for the governance service to inject into the users env",
            "SPARK_CLUSTER_MANAGER_API_URL": "Spark cluster manager API",
            "BERDL_HIVE_METASTORE_URI": "Hive metastore URI",
            "BERDL_NOTEBOOK_IMAGE_TAG": "BERDL notebook Docker image tag",
        },
    }

    optional_vars = {
        "Kubernetes": {
            "NODE_SELECTOR_HOSTNAME": "Kubernetes node hostname",
        },
        "JupyterHub Settings": {
            "JUPYTERHUB_DEBUG": "Enable debug mode",
            "JUPYTERHUB_LOG_LEVEL": "Set JupyterHub log level. Default is INFO",
            "ENABLE_IDLE_CULLER": "Enable idle culler for JupyterHub. Defaults to True",
            "JUPYTERHUB_IDLE_TIMEOUT_SECONDS": "Idle timeout in seconds for JupyterHub users. Defaults to 3600 seconds (1 hour)",
            "JUPYTERHUB_MEM_LIMIT_GB": "Memory limit in GB for JupyterHub users. Defaults to XGB",
            "JUPYTERHUB_MEM_GUARANTEE_GB": "Memory guarantee in GB for JupyterHub users. Defaults to YGB",
            "JUPYTERHUB_CPU_LIMIT": "CPU limit for JupyterHub users. Defaults to Z cores",
            "JUPYTERHUB_CPU_GUARANTEE": "CPU guarantee for JupyterHub users. Defaults to W cores",
        },
        "Spark Cluster Settings": {
            "DEFAULT_MASTER_CORES": "Default master cores for Spark clusters",
            "DEFAULT_MASTER_MEMORY": "Default master memory for Spark clusters",
            "DEFAULT_WORKER_COUNT": "Default number of worker nodes for Spark clusters",
            "DEFAULT_WORKER_CORES": "Default worker cores for Spark clusters",
            "DEFAULT_WORKER_MEMORY": "Default worker memory for Spark clusters",
        },
        "MinIO Settings": {
            "MINIO_SECURE_FLAG": "Flag indicating if MinIO uses HTTPS to inject into the users env. Defaults to True",
        },
    }

    # Check required variables
    missing = []
    for category, vars_dict in required_vars.items():
        for var, description in vars_dict.items():
            if var not in os.environ:
                missing.append(f"  - {var} ({category}): {description}")

    if missing:
        print("ERROR: Missing required environment variables:", file=sys.stderr)
        print("\n".join(missing), file=sys.stderr)
        sys.exit(1)

    # Log optional variables
    print("Environment validation successful!")
    print("\nOptional variables status:")
    for category, vars_dict in optional_vars.items():
        print(f"\n  --- {category} ---")
        for var, description in vars_dict.items():
            status = "✓ Set" if var in os.environ else "✗ Not set"
            print(f"    {status}: {var} ({description})")
