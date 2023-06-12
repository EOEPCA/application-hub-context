FROM jupyterhub/k8s-hub:2.0.0

ARG NB_USER=johub
ARG NB_UID=1001
ARG HOME=/home/johub

USER root

RUN apt update && \
    apt install npm git sudo -y && \
    npm install -g configurable-http-proxy

RUN adduser --disabled-password \
    --gecos "Default user" \
    --uid ${NB_UID} \
    --home ${HOME} \
    --force-badname \
    ${NB_USER}

RUN adduser jovyan sudo && \
    echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --upgrade --no-cache-dir \
        setuptools \
        pip

RUN PYCURL_SSL_LIBRARY=openssl \
    pip install --no-cache-dir \
        -r /tmp/requirements.txt

# So we can actually write a db file here
RUN chown ${NB_USER}:${NB_USER} /srv/jupyterhub

COPY . /tmp
RUN cd /tmp && python setup.py install

USER ${NB_USER}

CMD ["jupyterhub", "--config", "/etc/jupyterhub/jupyterhub_config.py"]
