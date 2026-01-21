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


## Container Image Strategy & Availability

This project publishes container images to GitHub Container Registry (GHCR) following a clear and deterministic tagging strategy aligned with the Git branching and release model.

### Image Registry

Images are published to:

```
ghcr.io/<repository-owner>/application-hub
```

The registry owner corresponds to the GitHub repository owner (user or organization).

Images are built using Kaniko and pushed using OCI-compliant tooling.

### Tagging Strategy

The image tag is derived automatically from the Git reference that triggered the build:


| Git reference    | Image tag    | Purpose                            |
| ---------------- | ------------ | ---------------------------------- |
| `develop` branch | `latest-dev` | Development and integration builds |
| `main` branch    | `latest`     | Stable branch builds               |
| Git tag `vX.Y.Z` | `X.Y.Z`      | Immutable release builds           |