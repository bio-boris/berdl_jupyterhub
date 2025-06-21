FROM jupyterhub/jupyterhub:5.3.0

COPY jupyterhub_customizations/ /opt/jupyterhub_customizations/
COPY auth/ /opt/auth/
COPY requirements.txt /opt/requirements.txt

ENV PYTHONPATH=/opt:$PYTHONPATH

COPY jupyterhub_customizations/jupyterhub_config.py /etc/jupyterhub/jupyterhub_config.py

RUN pip install -r /opt/requirements.txt
ENTRYPOINT ["jupyterhub"]
CMD ["-f", "/etc/jupyterhub/jupyterhub_config.py"]