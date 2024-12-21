FROM ghcr.io/eoepca/container-k8s-hub/container-k8s-hub:4.0.0

ARG NB_USER=johub
ARG NB_UID=1001
ARG HOME=/home/johub

USER root

#  Packages update and dependencies installation
RUN microdnf update -y && \
    microdnf install -y \
    npm \
    git \
    sudo \
    python3-pip \
    python3-devel \
    gcc \
    libcurl-devel \
    openssl-devel \
    && microdnf clean all

# Installation of configurable-http-proxy via npm
RUN npm install -g configurable-http-proxy

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

# Python packages installation from requirements.txt
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --upgrade --no-cache-dir setuptools pip

# Specific Python dependencies installation
RUN PYCURL_SSL_LIBRARY=openssl \
    pip install --no-cache-dir -r /tmp/requirements.txt

# Check and correct requirejs version
RUN sed -i 's/"version": "[^"]*"/"version": "2.3.7"/' /usr/local/share/jupyterhub/static/components/requirejs/package.json

# Set permission on the directory /srv/jupyterhub
RUN chown ${NB_USER}:${NB_USER} /srv/jupyterhub

COPY . /tmp
RUN cd /tmp && python3 setup.py install

# Set not root user
USER ${NB_USER}

# Command to start jupyterhub
CMD ["jupyterhub", "--config", "/etc/jupyterhub/jupyterhub_config.py"]