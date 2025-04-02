# ApplicationHubConfiguration

The config-generator folder contains the hatch module for the jupyter notebook to support the generation of ApplicationHub configurations and its documentation is in the dedicated readme. 
The definition of an application in the config.yml is addressed according to this pattern:

```yaml
- id: <profile-id>
  groups: 
  - <group-id-1>
  - <group-id-N>
  definition:
    display_name: <display-name>
    slug: <reference-slug>
    default: <True/False>
    kubespawner_override:
      cpu_limit: <Cpu-limit-as-number>
      mem_limit: <ram-limit-as-G>
      image:  <app-docker-image-registry-path>
  default_url: <default-url>
  node_selector: 
    k8s.provider.com/pool-name: <node-selector>
```

E.g. 

```yaml
- id: profile_iga_remote_desktop
  groups: 
  - group-1
  definition:
    display_name: Remote Desktop
    slug: iga_remote_desktop
    default: False
    kubespawner_override:
      cpu_limit: 1
      mem_limit: 4G
      image:  eoepca/iga-remote-desktop
  default_url: "desktop"
  node_selector: 
    k8s.provider.com/pool-name: node-pool-a
```

Breakdown:

- id: the profile identifier of your app 
- groups: the group list containing the users groups that can use the declared app 
- definition: display name, reference slug identifying the app, cpu/ram requirements alloted for it, reference docker image for the app-level
- default_url: default uri where to find the app 
- node_selector: identifies on which node pool the app is executed 

To have a compliant candidate app to be added to the AppHub, it must comply with the proper Dockerfile definition before reference its produced docker image into the configuration.
In addition it must be pushed on a registry accessible from the AppHub deployment.
These images must expose a service on a given port.
There are two options to have JupyterHub to proxy these applications: 
- jupyter-server-proxy 
- jhsingle-native-proxy

## jupyter-server-proxy approach
The jupyter-server-proxy exposes the application alongside with the JupyterLab instance whilst jhsingle-native-proxy proxies the application without a running JupyterLab instance.

In example the eoepca/iga-remote-desktop_qgis uses the approach with jupyter-server-proxy.
It relies on the [jupyter-remote-desktop-proxy](https://github.com/jupyterhub/jupyter-remote-desktop-proxy) and [app-repo](https://github.com/EOEPCA/iga-remote-desktop-qgis/) 
 
Typically the Dockerfile starts with eoepca/iga-remote-desktop base image and then the specific app-level dependencies are added 

```
FROM eoepca/iga-remote-desktop
USER root

#Install your app with dependencies and add to PATH

RUN chown -R $NB_UID:$NB_GID $HOME
USER $NB_USER
```

## jhsingle-native-proxy approach
The jhsingle-native-proxy approach instead is based on a Dockerfile following this flow:

```
FROM python
RUN pip3 install \
    jhsingle-native-proxy>=0.0.9 \
    <your-other-pip-dependencies>

# create a user, since we don't want to run as root
RUN useradd -m jovyan
ENV HOME=/home/jovyan
WORKDIR $HOME
USER jovyan

EXPOSE <server-port>
CMD ["jhsingle-native-proxy", "--destport", "<your-dest-port>", "<your-app-cli>", "<your-app-params>", "{--}server.port", "{port}", "{--}server.headless", "True", "{--}server.enableCORS", "False", "--port", "<your-port>"]
```

It relies on the [jhsingle-native-proxy](https://github.com/ideonate/jhsingle-native-proxy) and [app-repo](https://github.com/EOEPCA/iga-streamlit-demo) 

So after having pip installed the jhsingle-native-proxy, the execution entrypoint in the Dockerfile is typically: 

```
CMD ["jhsingle-native-proxy", "--destport", "<your-dest-port>", "<your-app-cli>", "<your-app-params>", "{--}server.port", "{port}", "{--}server.headless", "True", "{--}server.enableCORS", "False", "--port", "<your-port>"]
```

E.g.

```
CMD ["jhsingle-native-proxy", "--destport",      "8505",         "streamlit",         "hello",         "{--}server.port", "8888", "{--}server.headless", "True", "{--}server.enableCORS", "False", "--port", "8888"]
```

Params breakdown:

--destport: specifies the destination port number where the target APPLICATION (in this case, Streamlit) will run.

--authtype: none disables authentication, meaning the application will not require authentication through JupyterHub.

--port $port: This sets the PROXY server's external port number to $port.

The {--} syntax is used to pass arguments to the app, e.g. Streamlit, command itself:
{--}server.port {port}: server.port {port} sets the port number on which the Streamlit SERVER will run. Equivalently {--}bind-addr 0.0.0.0:$port

{--}server.headless: True ensures that Streamlit runs in headless mode, meaning it does not require a graphical user interface (GUI).

{--}server.enableCORS: False disables Cross-Origin Resource Sharing (CORS), which is useful when running behind a proxy.


In addition to the usual jhsingle-native-proxy params list an could require an user data path mapping and its VS code loading, e.g. with {--}user-data-dir & CODE_SERVER_WS:  

```
CODE_SERVER_WS="/workspace"
jhsingle-native-proxy --port 8888 --destport $destport code-server {--}auth none {--}bind-addr 0.0.0.0:$destport {--}user-data-dir /workspace $CODE_SERVER_WS
```


## Private app images pulling 
The [docker-config](https://github.com/EOEPCA/helm-charts-dev/blob/f9c77a1e850c8e061de8b113ddcdcfd367b7fc0e/charts/application-hub/files/hub/config.yml#L198) configmap contains container registry authorization definitions. 
It is a config map mounted on the pod.
This file enables the pulling of the app images from container registries. 

```
{
    "auths": {
        "my-registry-1.com": {
            "auth": "<base64encoded-docker-config-1>"
        },
        "my-registry-1.com": {
            "auth": "<base64encoded-docker-config-2>"
        }
      }
}
```

Example:

```
{
    "auths": {
        "my-private-registry.com": {
            "auth": "am…g1Ml4="
        },
        "docker-co.domain.com": {
            "auth": "Zm…Q=="
        }
      }
}
```

In this example my-private-registry.com and docker-co.domain.com are added together with their credentials to let the AppHub deployment pull some of their images as propedeutic action before the app exposure.  
