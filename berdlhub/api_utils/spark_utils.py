"""
CDM Spark Cluster Manager API Client Wrapper
"""

import os
from typing import Optional

from spark_manager_client import AuthenticatedClient
from spark_manager_client.api.clusters import (
    create_cluster_clusters_post,
    delete_cluster_clusters_delete,
)
from spark_manager_client.models import (
    ClusterDeleteResponse,
    SparkClusterConfig,
    SparkClusterCreateResponse,
)
from spark_manager_client.types import Response


class SparkClusterManager:
    """
    A unified class to manage Spark clusters for users.
    It retrieves the necessary authentication token from the spawner's user auth_state
    and sets the environment variables required for Spark.
    """

    # Default configuration values
    DEFAULT_WORKER_COUNT = int(os.environ.get("DEFAULT_WORKER_COUNT", 2))
    DEFAULT_WORKER_CORES = int(os.environ.get("DEFAULT_WORKER_CORES", 1))
    DEFAULT_WORKER_MEMORY = os.environ.get("DEFAULT_WORKER_MEMORY", "10GiB")
    DEFAULT_MASTER_CORES = int(os.environ.get("DEFAULT_MASTER_CORES", 1))
    DEFAULT_MASTER_MEMORY = os.environ.get("DEFAULT_MASTER_MEMORY", "10GiB")

    def __init__(self, kbase_auth_token: str):
        """
        Initialize the SparkClusterManager with optional authentication token.

        Args:
            kbase_auth_token: Optional KBase authentication token
        """
        self.kbase_auth_token = kbase_auth_token
        self.client = AuthenticatedClient(
            base_url=os.environ["SPARK_CLUSTER_MANAGER_API_URL"], token=kbase_auth_token
        )

    def create_cluster(
        self,
        worker_count: Optional[int] = None,
        worker_cores: Optional[int] = None,
        worker_memory: Optional[str] = None,
        master_cores: Optional[int] = None,
        master_memory: Optional[str] = None,
    ) -> Optional[SparkClusterCreateResponse]:
        """
        Create a new Spark cluster with the given configuration.

        Args:
            worker_count: Number of worker nodes (defaults to DEFAULT_WORKER_COUNT)
            worker_cores: CPU cores per worker (defaults to DEFAULT_WORKER_CORES)
            worker_memory: Memory per worker (defaults to DEFAULT_WORKER_MEMORY)
            master_cores: CPU cores for master (defaults to DEFAULT_MASTER_CORES)
            master_memory: Memory for master (defaults to DEFAULT_MASTER_MEMORY)

        Returns:
            SparkClusterCreateResponse: Cluster creation response or None

        Raises:
            ValueError: If API call fails
        """
        # Use provided values or fall back to defaults
        worker_count = (
            worker_count if worker_count is not None else self.DEFAULT_WORKER_COUNT
        )
        worker_cores = (
            worker_cores if worker_cores is not None else self.DEFAULT_WORKER_CORES
        )
        worker_memory = worker_memory or self.DEFAULT_WORKER_MEMORY
        master_cores = (
            master_cores if master_cores is not None else self.DEFAULT_MASTER_CORES
        )
        master_memory = master_memory or self.DEFAULT_MASTER_MEMORY

        with self.client as client:
            # Create the config object
            config = SparkClusterConfig(
                worker_count=worker_count,
                worker_cores=worker_cores,
                worker_memory=worker_memory,
                master_cores=master_cores,
                master_memory=master_memory,
            )

            response: Response[SparkClusterCreateResponse] = (
                create_cluster_clusters_post.sync_detailed(client=client, body=config)
            )

        if response.status_code == 201 and response.parsed:
            print(f"Spark cluster created successfully.")
            print(f"Master URL: {response.parsed.master_url}")
            return response.parsed
        else:
            _raise_api_error(response)

    def delete_cluster(self) -> Optional[ClusterDeleteResponse]:
        """
        Delete the Spark cluster for the user.

        Args:
            kbase_auth_token: Optional token to override instance token

        Returns:
            ClusterDeleteResponse: Deletion response or None

        Raises:
            ValueError: If API call fails
        """

    async def start_spark_cluster(
        self,
        spawner,
    ):
        """
        Create a Spark cluster for the user (async method for spawner integration).

        Args:
            spawner: JupyterHub spawner instance
            kbase_auth_token: Optional token to override instance token

        Raises:
            ValueError: If cluster creation fails or master URL not found
        """
        username = spawner.user.name

        try:
            spawner.log.info(f"Creating Spark cluster for user {username}")
            response = self.create_cluster()
            master_url = getattr(response, "master_url", None)
            if master_url:
                spawner.log.info(f"Spark cluster created with master URL: {master_url}")
                spawner.environment["SPARK_MASTER_URL"] = master_url
            else:
                raise ValueError(f"Master URL not found in response: {response}")

        except Exception as e:
            spawner.log.error(
                f"Error creating Spark cluster for user {username}: {str(e)}"
            )
            raise

    async def stop_spark_cluster(self, spawner):
        """
        Delete the Spark cluster for the user (async method for spawner integration).

        Args:
            spawner: JupyterHub spawner instance
            kbase_auth_token: Optional token to override instance token
        """
        username = spawner.user.name
        try:
            spawner.log.info(f"Deleting Spark cluster for user {username}")
            with self.client as client:
                response: Response[ClusterDeleteResponse] = (
                    delete_cluster_clusters_delete.sync_detailed(client=client)
                )
            if response.status_code in (200, 204) and response.parsed:
                print("Spark cluster deleted successfully.")

            spawner.log.info(f"Spark cluster deleted for user {username}")
        except Exception as e:
            spawner.log.error(
                f"Error deleting Spark cluster for user {username}: {str(e)}"
            )
