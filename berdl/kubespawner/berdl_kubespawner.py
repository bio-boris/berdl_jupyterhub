import os
import shutil
import venv
from datetime import datetime, timedelta
from pathlib import Path

import json5
from filelock import FileLock
from kubespawner import KubeSpawner

from service.arg_checkers import not_falsy
from spark import cluster


class B(KubeSpawner):
    RW_MINIO_GROUP = "minio_rw"
    DEFAULT_IDLE_TIMEOUT_MINUTES = 180

    def start(self):
        username = self.user.name
        global_home = Path(os.environ["JUPYTERHUB_USER_HOME"])

        # Configure environment variables for the pod
        self._configure_environment(user_dir, user_env_dir, username)

        # Configure notebook directory
        self._configure_notebook_dir(username, user_dir)

        # Set up volume mounts specific for Kubernetes
        self._ensure_user_volume(user_dir)

        # Set up JupyterLab favorites (if applicable)
        self._add_favorite_dir(
            user_dir, favorites={Path(os.environ["KBASE_GROUP_SHARED_DIR"])}
        )

        self.namespace = os.environ["KUBE_NAMESPACE"]

        # Finally, create a Spark cluster for the user
        self._start_spark_cluster(
            username,
            not_falsy(self.environment["KBASE_AUTH_TOKEN"], "KBASE_AUTH_TOKEN"),
        )

        return super().start()

    async def stop(self, now=False):
        """Override the stop method with additional Spark cluster cleanup"""

        # Delete the user's Spark cluster
        self._stop_spark_cluster(
            self.user.name,
            not_falsy(self.environment["KBASE_AUTH_TOKEN"], "KBASE_AUTH_TOKEN"),
        )

        # Call the parent class's stop method to stop the pod
        return await super().stop(now=now)

    def _start_spark_cluster(self, username: str, kbase_auth_token: str):
        """
        Create a Spark cluster for the user
        """
        try:
            self.log.info(f"Creating Spark cluster for user {username}")
            response = cluster.create_cluster(
                kbase_auth_token=kbase_auth_token, force=True
            )
            if response and hasattr(response, "master_url") and response.master_url:
                self.log.info(
                    f"Spark cluster created with master URL: {response.master_url}"
                )
                # Update environment with the Spark master URL
                self.environment["SPARK_MASTER_URL"] = response.master_url
            else:
                raise ValueError(f"Master URL not found in response: {response}")
        except Exception as e:
            self.log.error(
                f"Error creating Spark cluster for user {username}: {str(e)}"
            )

    def _stop_spark_cluster(self, username: str, kbase_auth_token: str):
        """
        Delete the Spark cluster for the user
        """
        try:
            self.log.info(f"Deleting Spark cluster for user {username}")
            cluster.delete_cluster(kbase_auth_token=kbase_auth_token)
            self.log.info(f"Spark cluster deleted for user {username}")
        except Exception as e:
            self.log.error(
                f"Error deleting Spark cluster for user {username}: {str(e)}"
            )

        self.environment["SPARK_DRIVER_HOST"] = self.pod_name
        self.environment["SPARK_JOB_LOG_DIR_CATEGORY"] = username

        self.environment["SHELL"] = "/usr/bin/bash"

        if self._is_rw_minio_user():
            self.log.info(
                f"MinIO read/write user detected: {self.user.name}. Setting up minio_rw credentials."
            )
            self.environment["MINIO_ACCESS_KEY"] = self.environment[
                "MINIO_RW_ACCESS_KEY"
            ]
            self.environment["MINIO_SECRET_KEY"] = self.environment[
                "MINIO_RW_SECRET_KEY"
            ]

        else:
            self.log.info(
                f"Non-admin user detected: {self.user.name}. Removing admin credentials."
            )
            self.environment.pop("MINIO_RW_ACCESS_KEY", None)
            self.environment.pop("MINIO_RW_SECRET_KEY", None)

    def _is_rw_minio_user(self):
        """
        Check if the user is a read/write MinIO user.

        Admin users and users in the minio_rw group are considered read/write MinIO users.
        """
        group_names = [group.name for group in self.user.groups]
        return self.user.admin or self.RW_MINIO_GROUP in group_names
