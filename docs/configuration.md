# Configuration

## Profiles

A profile entry is defined as an entry in the `config.yml` file:

```yaml
profiles:
  - id: profile_1
    ...
  - id: profile_2
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
# the default URL to redirect
default_url: "lab"
# spawned pod environment variables (optional)
pod_env_vars:
    A: 10
    B: 20
# a list of volumes (optional)
volumes: []
# a list of config maps (optional)
config_maps: []
```

## Understanding the groups

The `groups` element allows a granular access to different apps.

A user belonging to `group-A` is able to spawn the application defined in the `profile_1`.

Users and groups can be managed via UI in the `/hub/admin` deployment URL or via API (see https://jupyterhub.readthedocs.io/en/stable/reference/rest-api.html#/)

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

## ConfigMaps

An existing configMap is defined with:

```yaml
name: aws-credentials
key: aws-credentials
mount_path: /home/jovyan/.aws/credentials
default_mode: 0660
readonly: true
```

A new configMap with the content inline:

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
