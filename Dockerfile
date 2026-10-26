FROM ghcr.io/eoepca/container-k8s-hub:5.0.0

ARG NB_USER=johub
ARG NB_UID=1001
ARG HOME=/home/johub

USER root

# The rebuilt base provides a pip-free Python environment and patched uv.
COPY security/ /opt/python-security/
ENV UV_SYSTEM_CERTS=true
ENV UV_CONSTRAINT=/opt/python-security/python-constraints.txt
ENV UV_NO_CACHE=true
RUN microdnf update -y && \
    microdnf install -y \
        npm git sudo python3.12-devel gcc libcurl-devel openssl-devel libpq-devel && \
    microdnf clean all && \
    rm -f /usr/share/python-wheels/pip-*.whl /usr/share/python3-wheels/pip-*.whl

# Installation of configurable-http-proxy via npm.
# NOTE: configurable-http-proxy is pinned to 4.5.3 to ensure compatibility and reproducible builds
# with the current JupyterHub/base image setup. Review and test carefully before changing this
# version, as upgrades may affect proxy behavior, compatibility, or security posture.
RUN npm install -g configurable-http-proxy@4.5.3

# User creation
RUN adduser \
    --uid ${NB_UID} \
    --home ${HOME} \
    ${NB_USER} \
    --comment "Default user" \
    --shell /bin/bash

# Add jovyan to the sudoers group
RUN usermod -aG wheel jovyan && \
    echo '%wheel ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

# Set permission on the directory /srv/jupyterhub
RUN chown ${NB_USER}:${NB_USER} /srv/jupyterhub

COPY . /tmp
RUN uv pip install --python /opt/hub-venv/bin/python3 --no-cache /tmp && \
    uv pip check --python /opt/hub-venv/bin/python3

# Replace JupyterHub's bundled Moment.js with the patched package, including JS assets.
RUN npm install --prefix /tmp/jupyterhub-assets --cache /tmp/moment-npm-cache \
        --ignore-scripts --no-audit --no-fund --package-lock=false moment@2.31.0 && \
    rm -rf /opt/hub-venv/share/jupyterhub/static/components/moment && \
    mv /tmp/jupyterhub-assets/node_modules/moment /opt/hub-venv/share/jupyterhub/static/components/moment && \
    rm -rf /tmp/jupyterhub-assets /tmp/moment-npm-cache

# Check and correct requirejs version
RUN sed -i 's/"version": "[^"]*"/"version": "2.3.7"/' /opt/hub-venv/share/jupyterhub/static/components/requirejs/package.json


# Set not root user
USER ${NB_USER}

# Command to start jupyterhub
CMD ["jupyterhub", "--config", "/etc/jupyterhub/jupyterhub_config.py"]

RUN sh /opt/python-security/remediate-python-trust.sh python3 --check
