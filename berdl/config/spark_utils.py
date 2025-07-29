from berdl.clients.spark import cluster
class SparkClusterManager:
    """
    Manages Spark clusters for users in the KBase environment.
    Implements a singleton pattern for instance management.
    """
    _singleton_instance = None

    def __init__(self, spawner):
        self.spawner = spawner
        self.user = spawner.user
        self.token = spawner.user.auth_state.get("kbase_auth_token", None)

    @classmethod
    def get_singleton(cls, spawner):
        if cls._singleton_instance is None or cls._singleton_instance.spawner != spawner:
            cls._singleton_instance = cls(spawner)
        return cls._singleton_instance

    def start_spark_cluster(self, kbase_auth_token: str):
        """
        Create a Spark cluster for the user.
        """
        username = self.spawner.user.name
        try:
            self.spawner.log.info(f"Creating Spark cluster for user {username}")
            response = cluster.create_cluster(
                kbase_auth_token=kbase_auth_token, force=True
            )
            if response and hasattr(response, "master_url") and response.master_url:
                self.spawner.log.info(
                    f"Spark cluster created with master URL: {response.master_url}"
                )
                self.spawner.environment["SPARK_MASTER_URL"] = response.master_url
            else:
                raise ValueError(f"Master URL not found in response: {response}")
        except Exception as e:
            self.spawner.log.error(
                f"Error creating Spark cluster for user {username}: {str(e)}"
            )

    def stop_spark_cluster(self, kbase_auth_token: str):
        """
        Delete the Spark cluster for the user.
        """
        username = self.spawner.user.name
        try:
            self.spawner.log.info(f"Deleting Spark cluster for user {username}")
            cluster.delete_cluster(kbase_auth_token=kbase_auth_token)
            self.spawner.log.info(f"Spark cluster deleted for user {username}")
        except Exception as e:
            self.spawner.log.error(
                f"Error deleting Spark cluster for user {username}: {str(e)}"
            )




def pre_spawn_hook(spawner):
    # Get the auth token from a secure source
    kbase_auth_token = os.environ.get("KBASE_AUTH_TOKEN")
    manager = SparkClusterManager(spawner)
    manager.start_spark_cluster(kbase_auth_token)

def post_stop_hook(spawner):
    # Get the auth token from a secure source
    kbase_auth_token = os.environ.get("KBASE_AUTH_TOKEN")
    manager = SparkClusterManager(spawner)
    manager.stop_spark_cluster(kbase_auth_token)