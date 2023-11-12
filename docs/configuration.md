# Configuration

## Profiles

A profile entry is defined as an entry in the `config.yml` file:

```yaml
profiles:
- id: profile_1
  ...
- id: profile_2
  ...
```

A profile is defined with:

```yaml
# an identifier
id: profile_1
# the group(s) this profile is included in:
groups:
- group-A
- group-B
# a definition block, see config c.KubeSpawner.profile_list in the kubespawner documentation
definition:
    display_name: Profile 1
    slug: profile_1_slug
    default: False
    kubespawner_override:
        cpu_limit: 4
        mem_limit: 8G
        image: eoepca/iat-jupyterlab:main
# the default URL to redirect (optional)
default_url: "lab"
# spawned pod environment variables (optional)
pod_env_vars:
    A: 10
    B: 20
    GITLAB_TOKEN:
      from_config_map:
        name: gitlabenv
        key: GITLAB_TOKEN
# a list of volumes (optional)
volumes: []
# a list of config maps (optional)
config_maps: []
# kubernetes node pool selector
node_selector: {}
```

## Understanding the groups

The `groups` element allows a granular access to different apps.

Users and groups can be managed via UI in the `/hub/admin` deployment URL or via API (see https://jupyterhub.readthedocs.io/en/stable/reference/rest-api.html#/)

With a configuration like:

```yaml
profiles:
- id: profile_1
  groups:
  - group-A
  - group-B
  definition:
  ...
- id: profile_2
  groups:
  - group-B
  definition:
  ...
```

A user that belongs to `group-A` is:

- able to spawn the application defined in the `profile_1`.
- not able to spawn the application defined in the `profile_2`.

A user belonging to `group-B` is:

- able to spawn the application defined in the `profile_1`.
- able to spawn the application defined in the `profile_2`.


## Profile definition

A `profile definition` example is shown below:

```yaml
definition:
  display_name: Profile 1
  slug: profile_1_slug
  default: False
  kubespawner_override:
    cpu_limit: 4
    mem_limit: 8G
    image: eoepca/iat-jupyterlab:main
```

The `kubespawner_override` can also include `extra_resource_limits` and `extra_resource_guarantees` to provide GPUs:

```yaml
kubespawner_override:
  cpu_limit: 4
  mem_limit: 8G
  image: eoepca/iat-jupyterlab:main
  extra_resource_limits: {"nvidia.com/gpu": "1"}
  extra_resource_guarantees: {"nvidia.com/gpu": "1"}
```

## Environment variables

Environment variables can be defined by

* Providing a fixed global value, or
* Referencing a key in a config map (which must exist in the same Kubernetes namespace,
  e.g. an individual user's namespace)

The two ways of defining environment variables work as follows (global and specific):

```yaml
pod_env_vars:
  global: global_value
  specific:
    from_config_map:
      name: config_map_name
      key: config_map_key
```


## Volumes

A volume is defined with:

```yaml
name: volume-workspace
claim_name: claim-workspace
size: 10Gi
storage_class: "scw-bssd"
access_modes:
- "ReadWriteOnce"
volume_mount:
  name: volume-workspace
  mount_path: "/workspace"
persist: true
```

**Note**: if the _PVC_ does not exist it is created.

If the `persist` boolean flag is set to `false`, both the _PVC_ and _Volume_ are deleted.

## ConfigMaps

An existing configMap to be mounted on the spawned pod is defined with:

```yaml
name: aws-credentials
key: aws-credentials
mount_path: /home/jovyan/.aws/credentials
default_mode: 0660
readonly: true
```

A new configMap with the content inline to be mounted on the spawned pod is defined with:

```yaml
name: aws-credentials
key: aws-credentials
mount_path: /home/jovyan/.aws/credentials
default_mode: 0660
readonly: true
content: -|
  [default]
  aws_access_key_id=5...b
  aws_secret_access_key=c7...3
```

## Roles and role bindings

Roles and role bindings are defined as follows (following the model of the Kubernetes [RBAC authorisation](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)):

```yaml
role_bindings:
  - name: pod_reader_role_binding
    subjects:
      - name: default
        kind: ServiceAccount
    role:
        name: pod_reader_role
        api_group: rbac.authorization.k8s.io
        verbs:
          - get
          - list
          - watch
        resources:
          - pods
          - pods/log
    persist: false
```

If the `persist` boolean flag is set to `false`, both the _role_ and _role binding_ are deleted when the pod is disposed.

## Image Pull Secrets

Image Pull Secrets are defined with:

```yaml
image_pull_secrets:
  - data: "eyJhdXRocyI6eyJjci50ZXJyYWR1ZS5jkdWWWVXTnpiMVZuTm14VmJUWkllWGhUIn19fQ=="
    name: "cr-config"
    persist: false
```

## Init Containers

This init container use an `.init.sh` mounted from a configMap and a volume to contextualize the environment:

```yaml
init_containers:
  - command:
    - sh
    - /opt/init/.init.sh
    image: bitnami/git:latest
    name: init-file-on-volume
    volume_mounts:
    - mount_path: /workspace
      name: workspace-volume
    - mount_path: /opt/init/.init.sh
      name: init
      sub_path: init
```

The configMap `init` is created with:


```yaml
- config_maps:
  - name: init
    key: init
    content: |-
      echo "# Hello World!" > /workspace/README.md
    default_mode: null
    mount_path: /opt/init/.init.sh
    persist: false
    readonly: true
```
