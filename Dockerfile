# Set the base image
FROM jupyterhub/jupyterhub:5.3.0

# --- Environment Configuration ---
# Use a single, consistent directory for the application.
ENV APP_DIR=/hub
# Add this directory to PYTHONPATH so Python can find the 'berdl' module.
ENV PYTHONPATH=${APP_DIR}
ENV JUPYTERHUB_TEMPLATES_DIR=${APP_DIR}/berdl/auth/templates
ENV KBASE_ORIGIN="https://ci.kbase.us"

# Set the working directory.
WORKDIR ${APP_DIR}

# Copy and install requirements.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your application code into a 'berdl' subdirectory inside /kbase.
COPY ./berdl/ ${APP_DIR}/berdl/


# Set the entrypoint and default command to run the application.
ENTRYPOINT ["jupyterhub"]
# Update the path to your config file to reflect the new location.
CMD ["-f", "/kbase/berdl/config/jupyterhub_config.py"]