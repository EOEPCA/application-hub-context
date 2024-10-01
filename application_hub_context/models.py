from enum import Enum
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field


class VolumeMount(BaseModel):
    """volume mount object"""

    name: str
    mount_path: str = Field(serialization_alias="mountPath")
    sub_path: Union[str, None] = Field(default=None, serialization_alias="subPath")


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


class Manifest(BaseModel):
    name: str
    key: str
    content: Optional[List[Dict]] = None
    persist: Optional[bool] = True


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
    mount_path: Optional[str] = None
    default_mode: Optional[str] = None
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


class InitContainerVolumeMount(VolumeMount):
    sub_path: str


class InitContainer(BaseModel):
    name: str
    image: str
    command: List[str]
    volume_mounts: List[VolumeMount]

    # {
    #     "name": "init-file-on-volume",
    #     "image": "bitnami/git:latest",
    #     "command": ["sh", "-c", "sh -x /opt/init/.init.sh"],
    #     "volumeMounts": [
    #         {"name": "workspace-volume", "mountPath": "/workspace"},
    #         {"name": "init", "subPath": "init", "mountPath": "/opt/init/.init.sh"},
    #     ],
    # }


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
    description: Optional[str] = None
    slug: str
    default: bool
    kubespawner_override: KubespawnerOverride


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


class ImagePullSecret(BaseModel):
    name: str
    persist: bool = True
    data: Optional[str] = None


class Profile(BaseModel):
    id: str
    groups: List[str]
    definition: ProfileDefinition
    config_maps: Optional[List[ConfigMap]] = None
    volumes: Optional[List[Volume]] = None
    pod_env_vars: Optional[dict[str, Union[str, ConfigMapEnvVarReference]]] = None
    default_url: Optional[str] = None
    node_selector: dict
    role_bindings: Optional[List[RoleBinding]] = None
    image_pull_secrets: Optional[List[ImagePullSecret]] = None
    init_containers: Optional[List[InitContainer]] = None
    manifests: Optional[List[Manifest]] = None


class Config(BaseModel):
    profiles: List[Profile]
