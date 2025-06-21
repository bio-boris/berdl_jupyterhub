FROM jupyterhub/jupyterhub:5.3.0

COPY jupyterhub_customizations/ /opt/jupyterhub_customizations/
COPY auth/ /opt/auth/

ENV PYTHONPATH=/opt:$PYTHONPATH

COPY jupyterhub_customizations/jupyterhub_config.py /etc/jupyterhub/jupyterhub_config.py

ENTRYPOINT ["jupyterhub"]
CMD ["-f", "/etc/jupyterhub/jupyterhub_config.py"]