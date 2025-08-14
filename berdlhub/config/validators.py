"""Validate required environment variables."""

import os
import sys
import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


def _mask_sensitive_value(var_name: str, value: str) -> str:
    """Mask sensitive values for logging."""
    sensitive_keywords = ["SECRET", "TOKEN", "PASSWORD", "KEY", "CRYPT"]
    if any(keyword in var_name.upper() for keyword in sensitive_keywords):
        return "***HIDDEN***"
    return value[:50] + "..." if len(value) > 50 else value


def _log_header(title: str, char: str = "=", width: int = 70):
    """Log a formatted header."""
    logger.info(char * width)
    logger.info(f" {title}")
    logger.info(char * width)


class EnvironmentValidator:
    """Validates and reports on environment configuration."""

    def __init__(self):
        self.required_vars = {
            # Core JupyterHub
            "JUPYTERHUB_COOKIE_SECRET_64_HEX_CHARS": "64 character hex string for cookies",
            "JUPYTERHUB_TEMPLATES_DIR": "Path to JupyterHub templates",

            # KBase integration
            "KBASE_ORIGIN": "KBase origin URL",
            "KBASE_AUTH_URL": "KBase authentication service URL",

            # Services
            "CDM_TASK_SERVICE_URL": "CDM task service endpoint",
            "GOVERNANCE_API_URL": "Governance API endpoint",
            "MINIO_ENDPOINT_URL": "MinIO endpoint URL for governance service",
            "SPARK_CLUSTER_MANAGER_API_URL": "Spark cluster manager API",
            "BERDL_HIVE_METASTORE_URI": "Hive metastore URI",
        }

        self.optional_vars = {
            # Kubernetes
            "NODE_SELECTOR_HOSTNAME": ("Kubernetes node hostname", None),

            # Debug/Logging
            "JUPYTERHUB_DEBUG": ("Enable debug mode", "false"),
            "JUPYTERHUB_LOG_LEVEL": ("JupyterHub log level", "INFO"),

            # Spark defaults
            "DEFAULT_MASTER_CORES": ("Default master cores for Spark", "2"),
            "DEFAULT_MASTER_MEMORY": ("Default master memory for Spark", "4G"),
            "DEFAULT_WORKER_COUNT": ("Default worker nodes for Spark", "2"),
            "DEFAULT_WORKER_CORES": ("Default worker cores for Spark", "2"),
            "DEFAULT_WORKER_MEMORY": ("Default worker memory for Spark", "4G"),

            # MinIO
            "MINIO_SECURE_FLAG": ("MinIO HTTPS flag", "true"),

            # Resource management
            "ENABLE_IDLE_CULLER": ("Enable idle culler", "true"),
            "JUPYTERHUB_IDLE_TIMEOUT_SECONDS": ("Idle timeout (seconds)", "3600"),
            "JUPYTERHUB_MEM_LIMIT_GB": ("Memory limit (GB)", "4"),
            "JUPYTERHUB_MEM_GUARANTEE_GB": ("Memory guarantee (GB)", "1"),
            "JUPYTERHUB_CPU_LIMIT": ("CPU limit (cores)", "2.0"),
            "JUPYTERHUB_CPU_GUARANTEE": ("CPU guarantee (cores)", "0.5"),
        }

    def _check_required(self) -> Tuple[List[str], Dict[str, str]]:
        """Check required variables and return missing and found."""
        missing = []
        found = {}

        for var, description in self.required_vars.items():
            if var not in os.environ:
                missing.append(f"{var}: {description}")
            else:
                found[var] = os.environ[var]

        return missing, found

    def _check_optional(self) -> Dict[str, Tuple[bool, str]]:
        """Check optional variables and return their status."""
        status = {}

        for var, (description, default) in self.optional_vars.items():
            if var in os.environ:
                status[var] = (True, os.environ[var])
            else:
                status[var] = (False, default)

        return status

    def validate(self) -> bool:
        """
        Validate environment variables and log results.

        Returns:
            bool: True if all required variables are set, False otherwise.
        """
        missing, found = self._check_required()
        optional_status = self._check_optional()

        # Check for missing required variables
        if missing:
            _log_header("❌ ENVIRONMENT VALIDATION FAILED", "=")
            logger.error("Missing required environment variables:")
            for item in missing:
                logger.error(f"  ✗ {item}")
            logger.error("")
            logger.error("Please set these variables and restart JupyterHub.")
            _log_header("", "=")
            return False

        # All required variables are present
        _log_header("✅ ENVIRONMENT VALIDATION SUCCESSFUL", "=")

        # Log required variables (with masked sensitive values)
        logger.info("")
        logger.info("📋 Required Variables (all present):")
        logger.info("-" * 40)
        for var, value in found.items():
            masked_value = _mask_sensitive_value(var, value)
            logger.info(f"  ✓ {var}: {masked_value}")

        # Log optional variables
        logger.info("")
        logger.info("📋 Optional Variables:")
        logger.info("-" * 40)

        # Group by status for better readability
        set_vars = []
        unset_vars = []

        for var, (is_set, value) in optional_status.items():
            description, default = self.optional_vars[var]
            if is_set:
                masked_value = _mask_sensitive_value(var, value)
                set_vars.append((var, masked_value, description))
            else:
                unset_vars.append((var, default, description))

        # Log set optional variables
        if set_vars:
            logger.info("  Configured:")
            for var, value, description in set_vars:
                logger.info(f"    ✓ {var} = {value}")
                logger.info(f"      └─ {description}")

        # Log unset optional variables
        if unset_vars:
            logger.info("  Using defaults:")
            for var, default, description in unset_vars:
                if default:
                    logger.info(f"    ○ {var} = {default} (default)")
                else:
                    logger.info(f"    ○ {var} (not set)")
                logger.info(f"      └─ {description}")

        # Summary
        logger.info("")
        logger.info("📊 Summary:")
        logger.info(f"  • Required variables: {len(found)}/{len(self.required_vars)} ✅")
        logger.info(f"  • Optional variables: {len(set_vars)}/{len(self.optional_vars)} configured")

        _log_header("", "=")
        return True


def validate_environment():
    """Validate environment variables and exit if required ones are missing."""
    validator = EnvironmentValidator()
    if not validator.validate():
        sys.exit(1)