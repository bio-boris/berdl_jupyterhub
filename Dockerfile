# Set the base image
FROM jupyterhub/jupyterhub:5.3.0

# Required for installing python packages from git
RUN apt-get update && apt-get install -y git

# --- Environment Configuration ---
# Define variables for all key paths
ENV HUB_DIR=/hub
ENV BERDL_DIR=${HUB_DIR}/berdl
ENV PYTHONPATH=${HUB_DIR}
ENV JUPYTERHUB_TEMPLATES_DIR=${BERDL_DIR}/auth/templates
ENV KBASE_ORIGIN="https://ci.kbase.us"

# --- Build Steps ---
WORKDIR ${HUB_DIR}
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ./berdlhub/ ${BERDL_DIR}/


# This default directory must be mounted in order to preserve the sqlite and pid files
WORKDIR /srv/jupyterhub
ENTRYPOINT ["jupyterhub"]
CMD ["-f", "/hub/berdlhub/config/jupyterhub_config.py"]