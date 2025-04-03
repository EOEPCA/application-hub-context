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


