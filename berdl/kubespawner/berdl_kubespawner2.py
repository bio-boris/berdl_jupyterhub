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


class BERDLKubeSpawner(KubeSpawner):
    RW_MINIO_GROUP = 'minio_rw'
    DEFAULT_IDLE_TIMEOUT_MINUTES = 180
    kbase_shared_dir = os.environ['KBASE_GROUP_SHARED_DIR']

    def start(self):
        # username = self.user.name
        # global_home = Path(os.environ['JUPYTERHUB_USER_HOME'])
        # user_dir = global_home / username
        # self.idle_timeout = self._get_idle_timeout()
        #
        # # Ensure the user directory exists
        # self._ensure_user_directory(user_dir, username)
        # self._ensure_bashrc(user_dir)
        #
        # # Ensure the user's Jupyter directory exists
        # self._ensure_user_jupyter_directory(user_dir)
        #
        # # Ensure the virtual environment is created or reused
        # user_env_dir = user_dir / '.virtualenvs' / 'envs' / f'{username}_default_env'
        # self._ensure_virtual_environment(user_env_dir)
        #
        # # Configure environment variables for the pod
        # self._configure_environment(user_dir, user_env_dir, username)
        #
        # # Configure notebook directory
        # self._configure_notebook_dir(username, user_dir)
        #
        # # Set up volume mounts specific for Kubernetes
        # self._ensure_user_volume(user_dir)
        #
        # # Set up JupyterLab favorites (if applicable)
        # self._add_favorite_dir(user_dir, favorites={Path(os.environ['KBASE_GROUP_SHARED_DIR'])})
        #
        # self.namespace = os.environ['KUBE_NAMESPACE']
        #
        # # Finally, create a Spark cluster for the user
        # self._start_spark_cluster(username, not_falsy(self.environment['KBASE_AUTH_TOKEN'], 'KBASE_AUTH_TOKEN'))

        return super().start()

    async def stop(self, now=False):
        """Override the stop method with additional Spark cluster cleanup"""
        # Delete the user's Spark cluster
        #self._stop_spark_cluster(self.user.name, not_falsy(self.environment['KBASE_AUTH_TOKEN'], 'KBASE_AUTH_TOKEN'))
        return await super().stop(now=now)



    # def _get_idle_timeout(self):
    #     """
    #     Retrieves the idle timeout from the environment variable `IDLE_TIMEOUT_MINUTES`.
    #     If not set, defaults to 180 minutes.
    #
    #     Returns:
    #         timedelta: Idle timeout duration.
    #     """
    #     idle_timeout_minutes = int(os.getenv("IDLE_TIMEOUT_MINUTES", self.DEFAULT_IDLE_TIMEOUT_MINUTES))
    #     self.log.info(f"Idle timeout set to {idle_timeout_minutes} minutes")
    #     return timedelta(minutes=idle_timeout_minutes)
    #
    #






    def _configure_environment(self, user_dir: Path, user_env_dir: Path, username: str):
        pass
        # self.environment.update({key: str(value) for key, value in os.environ.items() if key not in self.environment})
        # self.environment['SPARK_DRIVER_HOST'] = self.pod_name
        # # self.environment['PYTHONSTARTUP'] = os.path.join(os.environ['JUPYTERHUB_CONFIG_DIR'], 'startup.py')
        # self.environment['SPARK_JOB_LOG_DIR_CATEGORY'] = username
        #
        # # if self._is_rw_minio_user():
        # #     self.log.info(f"MinIO read/write user detected: {self.user.name}. Setting up minio_rw credentials.")
        # #     self.environment['MINIO_ACCESS_KEY'] = self.environment['MINIO_RW_ACCESS_KEY']
        # #     self.environment['MINIO_SECRET_KEY'] = self.environment['MINIO_RW_SECRET_KEY']
        # #     # USAGE_MODE is used by the setup.sh script to determine the appropriate configuration for the user.
        # #     self.environment['USAGE_MODE'] = 'dev'
        # # else:
        # #     self.log.info(f"Non-admin user detected: {self.user.name}. Removing admin credentials.")
        # #     self.environment.pop('MINIO_RW_ACCESS_KEY', None)
        # #     self.environment.pop('MINIO_RW_SECRET_KEY', None)
        #
        # # TODO: add a white list of environment variables to pass to the user's environment
        # self.environment.pop('JUPYTERHUB_ADMIN_PASSWORD', None)
        #
        # self.log.info(f"Environment variables for user '{self.user.name}' at pod startup: {self.environment}")


    # def _ensure_user_volume(self, user_dir: Path):
    #     """
    #     Ensure the user's volume is correctly mounted in the container.
    #     """
    #
    #
    #     # within cdm_shared_dir
    #
    #     if self.user.admin:
    #         self.log.info(f"Admin user detected: {self.user.name}. Setting up admin volume mounts.")
    #         self.volumes = [
    #             # Global users home directory
    #             {
    #                 "name": "user-home",
    #                 "hostPath": {"path": f"{mount_base_dir}/{user_home_dir}"}
    #             },
    #             {
    #                 "name": "jupyterhub-secrets",
    #                 "hostPath": {"path": f"{mount_base_dir}/{hub_secrets_dir}"}
    #             },
    #             # Legacy data volume from JupyterLab
    #             {
    #                 "name": "cdm-shared",
    #                 "hostPath": {"path": f"{mount_base_dir}/{cdm_shared_dir}"}
    #             }
    #         ]
    #         self.volume_mounts = [
    #             {"name": "user-home", "mountPath": user_home_dir},
    #             {"name": "jupyterhub-secrets", "mountPath": hub_secrets_dir},
    #             {"name": "cdm-shared", "mountPath": cdm_shared_dir}
    #         ]
    #     else:
    #         self.log.info(f"Non-admin user detected: {self.user.name}. Setting up user-specific volume mounts.")
    #         # Determine readOnly mode: True if NOT a read/write minio user
    #         read_only = not self._is_rw_minio_user()
    #         self.volumes = [
    #             # User specific home directory
    #             {
    #                 "name": "user-home",
    #                 "hostPath": {"path": f"{mount_base_dir}/{user_home_dir}/{self.user.name}"}
    #             },
    #             # Legacy data volume from JupyterLab
    #             {
    #                 "name": "kbase-shared",
    #                 "hostPath": {"path": f"{mount_base_dir}/{kbase_shared_dir}"}
    #             }
    #         ]
    #         self.volume_mounts = [
    #             {
    #                 "name": "user-home",
    #                 "mountPath": f"{user_home_dir}/{self.user.name}"
    #             },
    #             {
    #                 "name": "kbase-shared",
    #                 "mountPath": kbase_shared_dir
    #             }

    # def _add_favorite_dir(self, user_dir: Path, favorites: set[Path] = None):
    #     """
    #     Configure the JupyterLab favorites for the user.
    #     """
    #     self.log.info('Configuring JupyterLab favorites for user')
    #
    #     # Ensure the user's home directory is always in the favorites
    #     favorites = {user_dir} if not favorites else favorites | {user_dir}
    #
    #     # Path to the JupyterLab favorites configuration file
    #     jupyterlab_favorites_path = user_dir / '.jupyter' / 'lab' / 'user-settings' / '@jlab-enhanced' / 'favorites' / 'favorites.jupyterlab-settings'
    #     favorites_dir = jupyterlab_favorites_path.parent
    #
    #     favorites_dir.mkdir(parents=True, exist_ok=True)
    #
    #     # Create a file lock to prevent race conditions
    #     lock_path = str(jupyterlab_favorites_path) + ".lock"
    #     lock = FileLock(lock_path)
    #
    #     with lock:
    #         if jupyterlab_favorites_path.exists():
    #             with open(jupyterlab_favorites_path, 'r') as f:
    #                 # JupyterHub writes JSON comments in the file
    #                 exist_favorites = json5.load(f)
    #         else:
    #             exist_favorites = {"favorites": []}
    #
    #         existing_fav_set = {(fav["root"], fav["path"]) for fav in exist_favorites.get('favorites', [])}
    #
    #         for fav in favorites:
    #
    #             if not fav.is_dir():
    #                 raise ValueError(f"Favorite {fav} is not a directory or does not exist")
    #
    #             # same approach used by NERSC JupyterHub
    #             root_str = "/"
    #             path_str = str(fav.relative_to(root_str))
    #
    #             if (root_str, path_str) not in existing_fav_set:
    #                 exist_favorites["favorites"].append({
    #                     "root": root_str,
    #                     "path": path_str,
    #                     "contentType": "directory",
    #                     "iconLabel": "ui-components:folder",
    #                     "name": "$HOME" if str(fav) == str(user_dir) else fav.name,
    #                 })
    #
    #         with open(jupyterlab_favorites_path, 'w') as f:
    #             json5.dump(exist_favorites, f, indent=4)
