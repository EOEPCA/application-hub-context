from typing import List, Optional

from pydantic import BaseModel


class VolumeMount(BaseModel):
    """volume mount object"""

    name: str
    mount_path: str


class Volume(BaseModel):

    """
    class defining a volume object:
        name: volume-workspace
        claimName: claim-workspace
        size: 10Gi
        storage_class: "scw-bssd"
        access_modes:
          - "ReadWriteOnce"
        volume_mount:
          name: volume-workspace
          mountPath: "/workspace"
        persist: true
    """

    name: str
    claim_name: str
    size: str
    storage_class: str
    access_modes: List[str]
    volume_mount: VolumeMount
    persist: bool


class ConfigMap(BaseModel):

    """
    name: aws-credentials
    key: aws-credentials
    mountPath: /home/jovyan/.aws/credentials
    defaultMode: 0660
    readOnly: true
    content: |
    """

    name: str
    key: str
    mount_path: str
    default_mode: Optional[str]
    readonly: bool
    content: Optional[str] = None
    persist: Optional[bool] = True


class KubespawnerOverride(BaseModel):
    cpu_limit: int
    cpu_guarantee: Optional[int] = None
    mem_limit: str
    mem_guarantee: Optional[str] = None
    image: str
    extra_resource_limits: Optional[dict] = {}
    extra_resource_guarantees: Optional[dict] = {}


class ProfileDefinition(BaseModel):

    """
    display_name: Profile 2
    slug: profile_2_slug
    default: False
    kubespawner_override:
        cpu_limit: 4
        mem_limit: 8G
        image: eoepca/pde-code-server:develop
    """

    display_name: str
    slug: str
    default: bool
    kubespawner_override: KubespawnerOverride


class ConfigMapKeyRef(BaseModel):
    name: str
    key: str


class ConfigMapEnvVarReference(BaseModel):
    from_config_map: ConfigMapKeyRef


class Profile(BaseModel):
    id: str
    groups: List[str]
    definition: ProfileDefinition
    config_maps: Optional[List[ConfigMap]] = None
    volumes: Optional[List[Volume]] = None
    pod_env_vars: Optional[dict[str, str | ConfigMapEnvVarReference]] = None
    default_url: Optional[str] = None
    node_selector: dict


class Config(BaseModel):
    profiles: List[Profile]
