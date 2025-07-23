# Set the base image
FROM jupyterhub/jupyterhub:5.3.0

# --- Environment Configuration ---
ENV DESTINATION_DIR=/berdl
ENV PYTHONPATH=${DESTINATION_DIR}:${PYTHONPATH}
ENV JUPYTERHUB_TEMPLATES_DIR=${DESTINATION_DIR}/auth/templates
ENV KBASE_ORIGIN="https://ci.kbase.us"

WORKDIR ${DESTINATION_DIR}

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./berdl/ /berdl/


# Set the entrypoint and default command to run the application.
ENTRYPOINT ["jupyterhub"]
CMD ["-f", "/berdl/config/jupyterhub_config.py"]