from enum import Enum
from typing import Dict, List, Optional, Union

from pydantic import BaseModel


class ConfigMapKeyRef(BaseModel):
    name: str
    key: str


class ConfigMapEnvVarReference(BaseModel):
    from_config_map: ConfigMapKeyRef


class SubjectKind(str, Enum):
    service_account = "ServiceAccount"
    user = "User"


class Verb(str, Enum):
    get = "get"
    list = "list"
    watch = "watch"
    create = "create"
    update = "update"
    patch = "patch"
    delete = "delete"
    deletecollection = "deletecollection"


class Subject(BaseModel):
    name: str
    kind: SubjectKind


class Role(BaseModel):
    name: str
    resources: List[str]
    verbs: List[Verb]
    api_groups: Optional[List[str]] = [""]


class RoleBinding(BaseModel):
    name: str
    subjects: List[Subject]
    role: Role
    persist: bool = True


class VolumeMount(BaseModel):
    """volume mount object"""

    name: str
    mount_path: str


class InitContainerVolumeMount(VolumeMount):
    sub_path: str


class Volume(BaseModel):
    """volume object"""

    name: str
    claim_name: str
    size: str
    storage_class: str
    access_modes: List[str]
    volume_mount: VolumeMount
    persist: bool


class Manifest(BaseModel):
    name: str
    key: str
    content: Optional[List[Dict]] = None
    persist: Optional[bool] = True


class ConfigMap(BaseModel):
    """config map object"""

    name: str
    key: str
    mount_path: Optional[str] = None
    default_mode: Optional[str] = None
    readonly: bool
    content: Optional[str] = None
    persist: Optional[bool] = True


class KubespawnerOverride(BaseModel):
    """kubespawner override object"""

    cpu_limit: int
    cpu_guarantee: Optional[int] = None
    mem_limit: str
    mem_guarantee: Optional[str] = None
    image: str
    extra_resource_limits: Optional[dict] = {}
    extra_resource_guarantees: Optional[dict] = {}


class InitContainer(BaseModel):
    name: str
    image: str
    command: List[str]
    volume_mounts: list[VolumeMount | InitContainerVolumeMount]


class ProfileDefinition(BaseModel):
    """profile definition object"""

    display_name: str
    description: Optional[str] = None
    slug: str
    default: bool
    kubespawner_override: KubespawnerOverride


class ImagePullSecret(BaseModel):
    name: str
    persist: bool = True
    data: Optional[str] = None


class Profile(BaseModel):
    """profile object"""

    id: str
    groups: List[str]
    definition: ProfileDefinition
    config_maps: Optional[List[ConfigMap]] = None
    volumes: Optional[List[Volume]] = None
    pod_env_vars: Optional[Dict[str, Union[str, ConfigMapEnvVarReference]]] = None
    default_url: Optional[str] = None
    node_selector: dict
    role_bindings: Optional[List[RoleBinding]] = None
    image_pull_secrets: Optional[List[ImagePullSecret]] = []
    init_containers: Optional[List[InitContainer]] = []
    manifests: Optional[List[Manifest]] = None
    env_from_config_maps: Optional[List[str]] = None
    env_from_secrets: Optional[List[str]] = None

class Config(BaseModel):
    """config object"""

    profiles: List[Profile]
