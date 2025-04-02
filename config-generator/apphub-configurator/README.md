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

```console
pip install apphub-configurator
```
## Overview
This package contains a notebook and the python modules to support the generation of ApplicationHub configurations for a minikube cluster. For more information about ApplicationHub please check this [link](https://github.com/EOEPCA/application-hub-context)

## Examples:

Find more examples if you need from this [link](https://github.com/EOEPCA/application-hub-context/tree/ESAEOEPCA-236/config-generator/apphub-configurator/examples)

### Step 1: Setup the environment

To begin using the `apphub-configurator` package, import the required functions from the package:

```python
from apphub_configurator.helpers import load_config_map, load_manifests, create_init_container, load_init_script
```

### Step 2: Example of configuration generation

Here is an overview of the functions and how to use them to generate configurations:

1. **Loading Kubernetes Manifests:**
   Use `load_manifests()` to load the required Kubernetes manifests. This function takes the following parameters:
   - `name`: The name of the manifest.
   - `key`: The key used to reference the manifest.
   - `file_path`: The file path to the manifest YAML file.

   Example usage:
   ```python
   load_manifests(name="example-name", key="example-key", file_path="path/to/manifest.yaml")
   ```

2. **Creating Volumes:**
   You can create a Kubernetes `Volume` by specifying the following:
   - `name`: The name of the volume.
   - `size`: The size of the volume (e.g., `"50Gi"`).
   - `claim_name`: The claim name for the volume.
   - `mount_path`: The path where the volume should be mounted.

   Example usage:
   ```python
   Volume(
       name="workspace-volume",
       size="50Gi",
       claim_name="workspace-claim",
       mount_path="/workspace"
   )
   ```

3. **Loading ConfigMaps:**
   Use `load_config_map()` to load configuration maps. It requires the following parameters:
   - `name`: The name of the config map.
   - `key`: The key for the configuration map.
   - `file_name`: The file path to the configuration file.
   - `mount_path`: The path where the config map should be mounted.

   Example usage:
   ```python
   load_config_map(name="bash-login", key="bash-login", file_name="path/to/bash-login", mount_path="/etc/profile.d/bash-login.sh")
   ```

4. **Creating Init Containers:**
   The `create_init_container()` function allows you to define init containers with the following parameters:
   - `image`: The container image to use.
   - `volume`: The volume associated with the container.
   - `mount_path`: The path where the volume will be mounted inside the container.

   Example usage:
   ```python
   create_init_container(image="example-image", volume=your_volume, mount_path="/calrissian")
   ```

5. **Creating Profiles:**
   You can create a `Profile` by defining its parameters such as `id`, `groups`, `definition`, and others. The profile can include volumes, config maps, init containers, and manifests.

   Example usage:
   ```python
   Profile(
       id="profile_1",
       definition=ProfileDefinition(
           display_name="Example Profile",
           description="This profile configures an example service",
           default=True
       ),
       volumes=[your_volume],
       config_maps=[your_config_map],
       init_containers=[your_init_container],
       manifests=[your_manifest]
   )
   ```

6. **Generating the Configuration:**
   After defining your profiles and configurations, you can use the `Config` class to generate the final configuration. This configuration can be saved to a YAML file.

   Example usage:
   ```python
   config = Config(profiles=[your_profile])
   with open("generated_config.yml", "w") as file:
       yaml.dump(config.dict(), file)
   ```


## License

`apphub-configurator` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
