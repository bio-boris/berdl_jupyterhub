from berdl.config.spark_utils import SparkClusterManager


async def pre_spawn_hook(spawner):
    """
    Hook to create a Spark cluster before the user's server starts.
    """
    # If this is using the user's token, rather than a service token, maybe this logic should moved into jupyter notebook itself.
    # Or we should make the notebook still be able to start up, even if the cluster is not created due to some error?
    # if the spark cluster is already running, this crashes...
    await SparkClusterManager.start_spark_cluster(spawner)


async def post_stop_hook(spawner):
    """
    Hook to delete the Spark cluster after the user's server stops.
    """
    await SparkClusterManager.stop_spark_cluster(spawner)
