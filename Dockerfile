FROM jupyterhub/jupyterhub:5.3.0

ENV TINI_VERSION v0.19.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
RUN chmod +x /tini

COPY jupyterhub_customizations/* /srv/jupyterhub/service/


ENTRYPOINT ["/tini", "--"]
CMD ["jupyterhub", "-f", "/srv/jupyterhub/service/jupyterhub_config.py"]
