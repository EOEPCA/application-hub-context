## ApplicationHub configuration generator

The AppHub configuration generator is the helper that eases the generation of the desired configuration selecting tools among the predefined ones. 
They include:

- **aws-cli**: CLI used for interfacing with an S3 service  
- **Stars**: CLI used for EO data stage-in from S3 or external repos and Data stage-out to S3 bucket  
- **cwltool**: CWL runner using local resources  
- **calrissian**: CWL runner on Kubernetes  
- **cwl-wrapper**: Utility to add stage-in/out nodes to an Application Package  
- **podman**: Container engine  
- **git**: CLI used for interfacing with git-based software repositories  
- **dvc**: Data versioning  
- **oras**: Client for OCI compliant repositories  

# apphub-configurator

[![PyPI - Version](https://img.shields.io/pypi/v/apphub-configurator.svg)](https://pypi.org/project/apphub-configurator)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/apphub-configurator.svg)](https://pypi.org/project/apphub-configurator)

-----
## Table of Contents

- [Installation](#installation)
- [Overview](#overview)
- [Examples](#Examples)
- [License](#license)

## Installation
Create a hatch environment with the dependencies listed in the file `pyproject.toml`. 

```console
hatch shell prod
hatch -e prod run python -m ipykernel install --user --name=apphub_configurator --display-name "apphub_configurator"
```
## Overview
This package contains a notebook and the python modules to support the generation of ApplicationHub configurations for a minikube cluster. For more information about ApplicationHub please check this [link](https://github.com/EOEPCA/application-hub-context)

## Examples:
The [example](./examples/) folder contains a notebook and the python modules to support the generation of ApplicationHub configurations.

## License
`apphub-configurator` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
