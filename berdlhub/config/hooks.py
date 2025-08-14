from kubernetes import client
from berdlhub.api_utils.governance_utils import GovernanceUtils
from berdlhub.api_utils.spark_utils import SparkClusterManager


async def pre_spawn_hook(spawner):
    """
    Hook to create a Spark cluster before the user's server starts.
    # TODO MOVE AUTH TO A SHARED UTILS MODULE, or in a prior step in the spawner pre-spawn hooks.
    # TODO TRY CATCH?
    """
    spawner.log.debug("Pre-spawn hook called for user %s", spawner.user.name)
    await GovernanceUtils.set_governance_credentials(spawner)
    await SparkClusterManager.start_spark_cluster(spawner)


async def post_stop_hook(spawner):
    """
    Hook to delete the Spark cluster after the user's server stops.
    """
    spawner.log.debug("Post-stop hook called for user %s", spawner.user.name)
    await SparkClusterManager.stop_spark_cluster(spawner)


def modify_pod_hook(spawner, pod):

    pod.spec.containers[0].env.append(
        client.V1EnvVar(
            "BERDL_POD_IP",
            None,
            client.V1EnvVarSource(
                field_ref=client.V1ObjectFieldSelector(field_path="status.podIP")
            ),
        )
    )
    pod.spec.containers[0].env.append(
        client.V1EnvVar(
            "BERDL_POD_NAME",
            None,
            client.V1EnvVarSource(
                field_ref=client.V1ObjectFieldSelector(field_path="metadata.name")
            ),
        )
    )
    pod.spec.containers[0].env.append(
        client.V1EnvVar(
            "BERDL_CPU_REQUEST",
            None,
            client.V1EnvVarSource(
                resource_field_ref=client.V1ResourceFieldSelector(
                    resource="requests.cpu"
                )
            ),
        )
    )
    pod.spec.containers[0].env.append(
        client.V1EnvVar(
            "BERDL_CPU_LIMIT",
            None,
            client.V1EnvVarSource(
                resource_field_ref=client.V1ResourceFieldSelector(resource="limits.cpu")
            ),
        )
    )
    pod.spec.containers[0].env.append(
        client.V1EnvVar(
            "BERDL_MEMORY_REQUEST",
            None,
            client.V1EnvVarSource(
                resource_field_ref=client.V1ResourceFieldSelector(
                    resource="requests.memory"
                )
            ),
        )
    )
    pod.spec.containers[0].env.append(
        client.V1EnvVar(
            "BERDL_MEMORY_LIMIT",
            None,
            client.V1EnvVarSource(
                resource_field_ref=client.V1ResourceFieldSelector(
                    resource="limits.memory"
                )
            ),
        )
    )

    return pod


def configure_hooks(c):
    c.KubeSpawner.pre_spawn_hook = pre_spawn_hook
    c.KubeSpawner.post_stop_hook = post_stop_hook
    c.KubeSpawner.modify_pod_hook = modify_pod_hook

    # Use the NB_USER environment variable that's already set
    c.KubeSpawner.lifecycle_hooks = {
        "postStart": {
            "exec": {
                "command": [
                    "/bin/sh",
                    "-c",
                    "ln -sfn /global_share /home/$NB_USER/global_share || true",
                ]
            }
        }
    }
