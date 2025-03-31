# ApplicationHub Context

Application Hub enables to manage the delivery of work environments and tools for a wide range of user tasks, such as develop, host, execute and perform exploratory analysis of EO applications, all managed within a single, unified Cloud infrastructure.
This capability is offered through:

- **JupyterLab**: for interactive analysis of EO data
- **Code-Server**: for browser-based coding environments
- **Custom-Dashboards**: for specialized visualizations or user-defined apps such as QGIS, SNAP, Streamlit 
- **Multi-User/Profile**: environment—users can be grouped, resource tuned and use different container images 

An Application is a kubernetes pod exposing a service via a port and accessed via a web browser.
Application pods are managed by JupyterHub, a deployment that proxies applications such as JupyterLab or Code Server acting as a SaaS solution for remote desktop applications such as QGIS, SNAP or dashboards. 
JupyterHub provides profiles based on the user groups.
An Application pod runs in a dedicated namespace that may have configurations such as ConfigMaps. 
The Application pod contextualization targets providing:

- **runtime environment variables**
- **runtime configuration files, such as S3 configuration files or docker config files**
- **volumes mounted, such as the workspace volume**
- **Multi-User/Profile**

The Application pod contextualization takes as input a 'profile' and is handled by the kube spawner providing:

- **authentication/authorization**
- **pre-spawn and post-stop hooks**

# SNAP via Remote Desktop

This interactive application provides a remote desktop with SNAP via JupyterHub.
It relies on the [jupyter-remote-desktop-proxy](https://github.com/jupyterhub/jupyter-remote-desktop-proxy)

## ApplicationHubConfiguration

Below an example of configuration in the ApplicationHub:

```yaml
- id: profile_iga_remote_desktop_snap
  groups: 
  - group-1
  definition:
    display_name: SNAP
    slug: iga_remote_desktop_snap
    default: False
    kubespawner_override:
      cpu_limit: 1
      mem_limit: 4G
      image:  eoepca/iga-remote-desktop_snap
  default_url: "desktop"
  node_selector: 
    k8s.provider.com/pool-name: node-pool-a
```

# Remote desktop
This interactive application provides a remote desktop via JupyterHub.
It relies on the [jupyter-remote-desktop-proxy](https://github.com/jupyterhub/jupyter-remote-desktop-proxy)

## ApplicationHubConfiguration
Below an example of configuration in the ApplicationHub:

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


# QGIS via Remote Desktop
This interactive application provides a remote desktop with QGIS via JupyterHub.
It relies on the [jupyter-remote-desktop-proxy](https://github.com/jupyterhub/jupyter-remote-desktop-proxy)

## ApplicationHubConfiguration
Below an example of configuration in the ApplicationHub:

```yaml
- id: profile_iga_remote_desktop_qgis
  groups: 
  - group-1
  definition:
    display_name: QGIS
    slug: iga_remote_desktop_qgis
    default: False
    kubespawner_override:
      cpu_limit: 1
      mem_limit: 4G
      image:  eoepca/iga-remote-desktop_qgis
  default_url: "desktop"
  node_selector: 
    k8s.provider.com/pool-name: node-pool-a
```
Breakdown:

- id: the profile identifier of your app 
- groups: the group list containing the users that can use the declared app 
- definition: display name, reference slug identifying the app, cpu/ram requirements alloted for it, reference docker image for the app-level
- default_url: default uri where to find the app 
- node_selector: identifies on which node pool the app is executed 

To have a compliant candidate app to be added to the AppHub, it must comply with the proper Dockerfile definition before adding this into the configuration.
In addition it must be pushed on a registry accessible from the AppHub deployment, e.g. eoepca/iga-remote-desktop_qgis in the example just above. 
Typically the Dockerfile starts with eoepca/iga-remote-desktop base image and then the specific app-level dependencies are added 

```
FROM eoepca/iga-remote-desktop:1.1.2
USER root

#Install your app with dependencies and add to PATH

RUN chown -R $NB_UID:$NB_GID $HOME
USER $NB_USER
```


In the Dockerfile, after having pre-installed with pip install jhsingle-native-proxy>=0.0.9, the execution entrypoint in the Dockerfile is typically: 

CMD ["jhsingle-native-proxy", "--destport", "<your-dest-port>", "<your-app-cli>", "<your-app-param>", "{--}server.port", "{port}", "{--}server.headless", "True", "{--}server.enableCORS", "False", "--port", "<your-port>"]

E.g.

CMD ["jhsingle-native-proxy", "--destport", "8505", "streamlit", "hello", "{--}server.port", "8888", "{--}server.headless", "True", "{--}server.enableCORS", "False", "--port", "8888"]


Params breakdown:

--destport: specifies the destination port number where the target APPLICATION (in this case, Streamlit) will run.

--authtype: none disables authentication, meaning the application will not require authentication through JupyterHub.

--port $port: This sets the PROXY server's external port number to $port.

The {--} syntax is used to pass arguments to the app, e.g. Streamlit, command itself:
{--}server.port {port}: server.port {port} sets the port number on which the Streamlit SERVER will run. Equivalently {--}bind-addr 0.0.0.0:$port

{--}server.headless: True ensures that Streamlit runs in headless mode, meaning it does not require a graphical user interface (GUI).

{--}server.enableCORS: False disables Cross-Origin Resource Sharing (CORS), which is useful when running behind a proxy.


Generalised command: 
```
jhsingle-native-proxy --destport $destport --authtype none <your-cli-command> <your-cli-params> {--}server.port {port} {--}server.headless True {--}server.enableCORS False --port $port
```

In addition to the usual jhsingle-native-proxy params list, an application, e.g. as PDE Code Server, can leverage a user data path mapping and its VS code loading, e.g. with {--}user-data-dir and CODE_SERVER_WS:  

```
CODE_SERVER_WS="/workspace"
jhsingle-native-proxy --port 8888 --destport $destport code-server {--}auth none {--}bind-addr 0.0.0.0:$destport {--}user-data-dir /workspace $CODE_SERVER_WS
```

