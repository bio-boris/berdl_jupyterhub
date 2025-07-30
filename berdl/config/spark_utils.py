from berdl.clients.spark import cluster
from typing import Optional

class SparkClusterManager:
    """
    A utility class with static methods to manage Spark clusters for users.
    It retrieves the necessary authentication token from the spawner.
    """
    @staticmethod
    def _get_auth_token(spawner) -> str:
        """Helper method to retrieve and validate the auth token."""
        kb_auth_token: Optional[str] = spawner.auth_state.get("kbase_auth_token")
        if not kb_auth_token:
            spawner.log.error("KBase auth token not found in spawner auth_state.")
            raise RuntimeError("KBase authentication token is missing.")
        return kb_auth_token

    @staticmethod
    def start_spark_cluster(spawner):
        """
        Create a Spark cluster for the user.
        """
        username = spawner.user.name
        kb_auth_token = SparkClusterManager._get_auth_token(spawner)
        try:
            spawner.log.info(f"Creating Spark cluster for user {username}")
            response = cluster.create_cluster(kbase_auth_token=kb_auth_token, force=True)

            master_url = getattr(response, "master_url", None)
            if master_url:
                spawner.log.info(f"Spark cluster created with master URL: {master_url}")
                spawner.environment["SPARK_MASTER_URL"] = master_url
            else:
                raise ValueError(f"Master URL not found in response: {response}")
        except Exception as e:
            spawner.log.error(f"Error creating Spark cluster for user {username}: {str(e)}")
            raise

    @staticmethod
    def stop_spark_cluster(spawner):
        """
        Delete the Spark cluster for the user.
        """
        username = spawner.user.name
        try:
            kb_auth_token = SparkClusterManager._get_auth_token(spawner)
            spawner.log.info(f"Deleting Spark cluster for user {username}")
            cluster.delete_cluster(kbase_auth_token=kb_auth_token)
            spawner.log.info(f"Spark cluster deleted for user {username}")
        except Exception as e:
            # For stopping, we just log the error and don't re-raise
            # because the server is already shutting down.
            spawner.log.error(f"Error deleting Spark cluster for user {username}: {str(e)}")


def pre_spawn_hook(spawner):
    """
    Hook to create a Spark cluster before the user's server starts.
    """
    SparkClusterManager.start_spark_cluster(spawner)


def post_stop_hook(spawner):
    """
    Hook to delete the Spark cluster after the user's server stops.
    """
    SparkClusterManager.stop_spark_cluster(spawner)