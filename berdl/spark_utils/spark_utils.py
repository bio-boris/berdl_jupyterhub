def _start_spark_cluster(self, username: str, kbase_auth_token: str):
    """
    Create a Spark cluster for the user
    """
    try:
        self.log.info(f"Creating Spark cluster for user {username}")
        response = cluster.create_cluster(kbase_auth_token=kbase_auth_token, force=True)
        if response and hasattr(response, 'master_url') and response.master_url:
            self.log.info(f"Spark cluster created with master URL: {response.master_url}")
            # Update environment with the Spark master URL
            self.environment['SPARK_MASTER_URL'] = response.master_url
        else:
            raise ValueError(f"Master URL not found in response: {response}")
    except Exception as e:
        self.log.error(f"Error creating Spark cluster for user {username}: {str(e)}")

def _stop_spark_cluster(self, username: str, kbase_auth_token: str):
    """
    Delete the Spark cluster for the user
    """
    try:
        self.log.info(f"Deleting Spark cluster for user {username}")
        cluster.delete_cluster(kbase_auth_token=kbase_auth_token)
        self.log.info(f"Spark cluster deleted for user {username}")
    except Exception as e:
        self.log.error(f"Error deleting Spark cluster for user {username}: {str(e)}")