import yaml

from models import (
    Volume,
    InitContainer,
    VolumeMount,
    ConfigMap,
    InitContainerVolumeMount,
    Manifest,
)


def load_config_map(name, key, file_name, mount_path):
    with open(file_name, "r") as f:
        content = f.read()
    return ConfigMap(
        name=name,
        key=key,
        content=content,
        readonly=True,
        persist=True,
        mount_path=mount_path,
    )


def load_manifests(name, key, file_path):
    with open(file_path, "r") as f:
        content = yaml.safe_load_all(f.read())
    return Manifest(
        name=name, key=key, readonly=True, persist=False, content=[e for e in content]
    )


def create_init_container(image: str, volume: Volume, mount_path: str) -> InitContainer:

    init_context_volume_mount = InitContainerVolumeMount(
        mount_path="/opt/init/.init.sh", name="init", sub_path="init"
    )

    return InitContainer(
        name="init-file-on-volume",
        image=image,
        command=["sh", "-c", "sh /opt/init/.init.sh"],
        volume_mounts=[
            VolumeMount(name=volume.name, mount_path=mount_path),
            init_context_volume_mount,
        ],
    )


def load_init_script(file_name: str) -> ConfigMap:
    with open(file_name, "r") as f:
        content = f.read()
    return ConfigMap(
        name="init",
        key="init",
        content=content,
        readonly=True,
        persist=False,
        mount_path="/opt/init/.init.sh",
        default_mode="0660",
    )
