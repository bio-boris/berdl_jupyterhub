FROM jupyterhub/jupyterhub:5.3.0

ENV TINI_VERSION v0.19.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
RUN chmod +x /tini

COPY jupyterhub_customizations/kb_jupyterhub_auth.py /srv/jupyterhub/service/
COPY jupyterhub_customizations/custom_kube_spawner.py /srv/jupyterhub/service/

ENTRYPOINT ["/tini", "--"]
CMD ["jupyterhub", "-f", "/etc/jupyterhub/jupyterhub_config.py"]
