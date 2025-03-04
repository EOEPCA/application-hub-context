## ApplicationHub configuration generator






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
