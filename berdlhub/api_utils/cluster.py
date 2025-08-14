"""
CDM Spark Cluster Manager API Client Wrapper
"""

import os

from spark_manager_client import AuthenticatedClient, Client
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

# So this is not part of the client, but it depends on outside code
from berdlhub.auth.arg_checkers import not_falsy

DEFAULT_WORKER_COUNT = int(os.environ.get("DEFAULT_WORKER_COUNT", 2))
DEFAULT_WORKER_CORES = int(os.environ.get("DEFAULT_WORKER_CORES", 1))
DEFAULT_WORKER_MEMORY = os.environ.get("DEFAULT_WORKER_MEMORY", "10GiB")
DEFAULT_MASTER_CORES = int(os.environ.get("DEFAULT_MASTER_CORES", 1))
DEFAULT_MASTER_MEMORY = os.environ.get("DEFAULT_MASTER_MEMORY", "10GiB")


def _get_client() -> Client:
    """
    Get an unauthenticated client for the Spark Cluster Manager API.
    """
    api_url = not_falsy(
        os.environ.get("SPARK_CLUSTER_MANAGER_API_URL"), "SPARK_CLUSTER_MANAGER_API_URL"
    )
    return Client(base_url=str(api_url))


def _get_authenticated_client(
    kbase_auth_token: str | None = None,
) -> AuthenticatedClient:
    """
    Get an authenticated client for the Spark Cluster Manager API.
    """
    api_url = not_falsy(
        os.environ.get("SPARK_CLUSTER_MANAGER_API_URL"), "SPARK_CLUSTER_MANAGER_API_URL"
    )
    return AuthenticatedClient(base_url=str(api_url), token=str(kbase_auth_token))


def _raise_api_error(response: Response) -> None:
    """
    Process the API error response and raise an error.
    """
    error_message = f"API Error (HTTP {response.status_code})"

    if hasattr(response, "content") and response.content:
        error_message += f": {response.content}"

    raise ValueError(error_message)


def create_cluster(
    kbase_auth_token: str | None = None,
    worker_count: int = DEFAULT_WORKER_COUNT,
    worker_cores: int = DEFAULT_WORKER_CORES,
    worker_memory: str = DEFAULT_WORKER_MEMORY,
    master_cores: int = DEFAULT_MASTER_CORES,
    master_memory: str = DEFAULT_MASTER_MEMORY,
) -> SparkClusterCreateResponse | None:
    """
    Create a new Spark cluster with the given configuration.

    Args:
        kbase_auth_token:
        worker_count: Number of worker nodes
        worker_cores: CPU cores per worker
        worker_memory: Memory per worker (e.g., "10GiB")
        master_cores: CPU cores for master
        master_memory: Memory for master (e.g., "10GiB")
    """

    client = _get_authenticated_client(kbase_auth_token)
    with client as client:
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

    _raise_api_error(response)


def delete_cluster(kbase_auth_token: str | None = None) -> ClusterDeleteResponse | None:
    """
    Delete the user's Spark cluster.
    """
    client = _get_authenticated_client(kbase_auth_token)
    with client as client:
        response: Response[ClusterDeleteResponse] = (
            delete_cluster_clusters_delete.sync_detailed(client=client)
        )

    if response.status_code == 200 and response.parsed:
        return response.parsed

    _raise_api_error(response)
