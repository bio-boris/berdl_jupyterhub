# Set the base image
FROM jupyterhub/jupyterhub:5.3.0

# --- Environment Configuration ---
ENV APP_DIR=/hub
ENV PYTHONPATH=${APP_DIR}
ENV JUPYTERHUB_TEMPLATES_DIR=${APP_DIR}/berdl/auth/templates
ENV KBASE_ORIGIN="https://ci.kbase.us"
# --- Environment Configuration ---


WORKDIR ${APP_DIR}

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ./berdl/ ${APP_DIR}/berdl/

ENTRYPOINT ["jupyterhub"]
CMD ["-f", "/{$APP_DIR}/berdl/config/jupyterhub_config.py"]