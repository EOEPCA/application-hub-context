# Configuration

## Overview

In the Application Hub, configuration is vital for defining Kubernetes objects through YAML files, ensuring consistent and scalable deployments. This approach allows users to specify the desired state of resources, with Kubernetes managing the necessary adjustments to align with this state.

Developing Kubernetes manifests or configuring the cluster using YAML files can be challenging and prone to errors. To simplify this process, a Python-based configuration generator can be used to produce clean, well-structured YAML files. This reduces the risk of misconfiguration and improves maintainability.
Users can programmatically define and customize various Kubernetes resources(e.g.**Pods**, **Volumes**, and **ConfigMaps**), well as handling the **External Secrets Operator**, define **profiles**, and manage **Helm releases**. This approach offers flexibility and empowers users to tailor deployments to their specific requirements.

## Apphub-configurator

The Configuration Generator is a Python module designed to facilitate the creation of configuration files for Application Hub deployments. It offers various utilities to streamline the configuration process.
### Python utilities:
- **`load_config_map(name, key, file_name, mount_path)`**: Reads a specified file and returns a `ConfigMap` object with the file's content, intended for use within Kubernetes configurations.

- **`load_manifests(name, key, file_path)`**: Loads a YAML file containing Kubernetes manifests and returns a `Manifest` object. This is useful for deploying one or multiple Kubernetes objects, such as Roles, RoleBindings, ServiceAccounts, and Releases.

- **`create_init_container(image, volume, mount_path)`**: Sets up an init container that executes specified commands during pod initialization. 

- **`load_init_script(file_name)`**: Loads a bash script intended for pod initialization and returns a `ConfigMap` object.

By utilizing these utilities, users can efficiently generate and manage configuration files, ensuring consistent and scalable deployments within the Application Hub environment.

### Kubernetes Object Data Classes

The module defines several Pydantic-based data classes representing Kubernetes objects, facilitating structured and validated configuration management:

- **`ConfigMapKeyRef`**: Represents a reference to a specific key within a Kubernetes ConfigMap, including the `name` of the ConfigMap and the `key` within it.

- **`ConfigMapEnvVarReference`**: Encapsulates a reference to a ConfigMap key, used to define environment variables in Kubernetes pods sourced from ConfigMap data.

- **`SubjectKind`**: An enumeration specifying the type of subject (e.g., `ServiceAccount`, `User`) for role-based access control (RBAC) configurations.

- **`Verb`**: An enumeration listing the permissible actions (e.g., `get`, `list`, `create`) for RBAC roles and role bindings.

- **`Subject`**: Defines a subject in RBAC, comprising a `name` and a `kind` (type).

- **`Role`**: Represents a Kubernetes Role, detailing the `name`, a list of `resources` it governs, permissible `verbs` (actions), and optional `api_groups`.

- **`RoleBinding`**: Binds a `Role` to specific `subjects`, assigning the defined permissions within a namespace. It includes a `name`, a list of `subjects`, the associated `role`, and a `persist` flag indicating whether the binding should be saved.

- **`VolumeMount`**: Specifies how a volume is mounted into a pod, detailing the `name` of the volume and the `mount_path` within the container's filesystem.

- **`InitContainerVolumeMount`**: Extends `VolumeMount` by adding a `sub_path`, allowing a specific file or directory within the volume to be mounted at the desired path.

- **`Volume`**: Describes a Kubernetes volume, including its `name`, `claim_name` for persistent volumes, `size`, `storage_class`, `access_modes`, an associated `volume_mount`, and a `persist` flag.

- **`Manifest`**: Represents a collection of Kubernetes objects, encompassing a `name`, a `key`, optional `content` (a list of dictionaries representing Kubernetes resources), and a `persist` flag.

- **`ConfigMap`**: Defines a Kubernetes ConfigMap, including a `name`, `key`, optional `mount_path` for mounting the ConfigMap as a file, an optional `default_mode` for file permissions, a `readonly` flag, optional `content`, and a `persist` flag.

- **`KubespawnerOverride`**: Allows customization of Kubernetes spawner settings for JupyterHub, specifying resource limits and guarantees such as `cpu_limit`, optional `cpu_guarantee`, `mem_limit`, optional `mem_guarantee`, `image`, and dictionaries for `extra_resource_limits` and `extra_resource_guarantees`.

- **`InitContainer`**: Details an initialization container within a pod, specifying its `name`, `image`, a list of `command` arguments to execute, and a list of `volume_mounts` (which can be either `VolumeMount` or `InitContainerVolumeMount`).

- **`ProfileDefinition`**: Describes a user profile within the Application-Hub, including a `display_name`, an optional `description`, a `slug` for identification, a `default` flag, and `kubespawner_override` settings.

- **`ImagePullSecret`**: Represents a secret used for pulling container images, including a `name`, a `persist` flag, and optional `data` (e.g., authentication credentials).

- **`SecretMount`**: Specifies a secret to be mounted into a pod, detailing the `name` of the secret, the `mount_path` within the container, an optional `sub_path` to a specific file within the secret, and a `default_mode` for file permissions.

- **`Profile`**: Encapsulates a user profile, including an `id`, a list of `groups` the user belongs to, a `definition` (of type `ProfileDefinition`), optional lists of `config_maps` and `volumes`, optional environment variable settings (`pod_env_vars`), optional `default_url`, `node_selector` for pod scheduling, optional `role_bindings`, `image_pull_secrets`, `init_containers`, `manifests`, environment variables sourced from ConfigMaps and Secrets, and optional `secret_mounts`.

- **`Config`**: Serves as the root configuration object, containing a list of `profiles` (of type `Profile`).

These data classes provide a structured approach to defining Kubernetes resources.

### Examples: 
The user can follow the examples provided to setup different profiles on Application Hub through the provided [notebook](../apphub-configurator/examples/config-generator.ipynb) under example folder. In the notebook, the user is able to configure different profile including:
- Coder
- Coder with a init.sh
- Jupyter Lab
- JupyterLab Plus
- E-learning
- QGIS

### Output format:

The `apphub-configurator` package generates a `config.yaml` file to define various profiles for your application deployment. Each profile includes several key attributes that need to be configured:

- **id**: the profile identifier of your app 
- **groups**: the group list containing the users groups that can use the declared app 
- **definition**: display name, reference slug identifying the app, cpu/ram requirements alloted for it, reference docker image for the app-level
- **config-maps**: definition of env variables expressed as '<key>:<value>' or config/secret files together with their mount_path, access, default_mode 
- **volumes**: handle the volumes, their persistency, their kubernetes access type (e.g. ReadWriteOnce, ReadWriteMany, ...), their size claim and their mount_path
- **pod_env_vars**: Handle the environment variables for the pod.
- **default_url**: default uri where to find the app 
- **node_selector**: identifies on which node pool the app is executed 
- **role_bindings**: A list of `RoleBinding` objects that associate users or groups with specific roles within the Kubernetes cluster, controlling access to resources.
- **image_pull_secrets**: A list of `ImagePullSecret` objects containing credentials for pulling private Docker images required by the application.
- **init_containers**: A list of `InitContainer` objects specifying containers that run before the main application containers, typically used for initialization tasks.
- **manifests**: A list of `Manifest` objects representing Kubernetes manifests to be applied during deployment, allowing for the creation and management of various Kubernetes resources.
- **env_from_config_maps**: A list of strings specifying the names of ConfigMaps whose data should be exposed as environment variables to the application pods.
- **env_from_secrets**: A list of strings specifying the names of Secrets whose data should be exposed as environment variables to the application pods.
- **secret_mounts**: A list of `SecretMount` objects defining Secrets to be mounted as files within the application pods, providing secure storage for sensitive data.
