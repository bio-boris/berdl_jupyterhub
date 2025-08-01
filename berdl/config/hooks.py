from berdl.config.spark_utils import SparkClusterManager


async def pre_spawn_hook(spawner):
    """
    Hook to create a Spark cluster before the user's server starts.
    """
    # If this is using the user's token, rather than a service token, maybe this logic should move into jupyter notebook itself.
    # Or we should make the notebook still be able to start up, even if the cluster is not created due to some error?
    # if the spark cluster is already running, this crashes...
    await SparkClusterManager.start_spark_cluster(spawner)




async def post_stop_hook(spawner):
    """
    Hook to delete the Spark cluster after the user's server stops.
    """
    await SparkClusterManager.stop_spark_cluster(spawner)


def modify_pod_hook(spawner, pod):
    pod.spec.containers[0].env.append(client.V1EnvVar("BERDL_POD_IP", None, client.V1EnvVarSource(field_ref = client.V1ObjectFieldSelector(
        field_path = "status.podIP"))))
    pod.spec.containers[0].env.append(client.V1EnvVar("BERDL_POD_NAME", None, client.V1EnvVarSource(field_ref = client.V1ObjectFieldSelector(
        field_path = "metadata.name"))))
    pod.spec.containers[0].env.append(client.V1EnvVar("BERDL_CPU_REQUEST", None, client.V1EnvVarSource(resource_field_ref = client.V1ResourceFieldSelector(resource = "requests.cpu"))))
    pod.spec.containers[0].env.append(client.V1EnvVar("BERDL_CPU_LIMIT", None, client.V1EnvVarSource(resource_field_ref = client.V1ResourceFieldSelector(resource = "limits.cpu"))))
    pod.spec.containers[0].env.append(client.V1EnvVar("BERDL_MEMORY_REQUEST", None, client.V1EnvVarSource(resource_field_ref = client.V1ResourceFieldSelector(resource = "requests.memory"))))
    pod.spec.containers[0].env.append(client.V1EnvVar("BERDL_MEMORY_LIMIT", None, client.V1EnvVarSource(resource_field_ref = client.V1ResourceFieldSelector(resource = "limits.memory"))))
    return pod

