from models import *
import yaml
import os
from loguru import logger
from helpers import (
    load_config_map,
    load_manifests,
    create_init_container,
    load_init_script,
)
import click

storage_class_rwo = "standard"
storage_class_rwx = "standard"
profiles = []
workspace_volume_size = "50Gi"
calrissian_volume_size = "50Gi"
image = "eoepca/pde-code-server:develop"
node_selector = {}

# get the current directory
current_dir = os.path.dirname(os.path.realpath(__file__))

# load the manifests

# localstack_manifest
localstack_manifest = load_manifests(
    name="localstack",
    key="localstack",
    file_path=os.path.join(current_dir, "manifests/manifest.yaml"),
)

# Dask Gateway manifest
dask_gateway_manifest = load_manifests(
    name="dask-gateway",
    key="dask-gateway",
    file_path=os.path.join(current_dir, "manifests/dask-gateway.yaml"),
)

# volumes

workspace_volume = Volume(
    name="workspace-volume",
    size=workspace_volume_size,
    claim_name="workspace-claim",
    mount_path="/workspace",
    storage_class=storage_class_rwo,
    access_modes=["ReadWriteOnce"],
    volume_mount=VolumeMount(name="workspace-volume", mount_path="/workspace"),
    persist=True,
)

calrissian_volume = Volume(
    name="calrissian-volume",
    claim_name="calrissian-claim",
    size=calrissian_volume_size,
    storage_class=storage_class_rwx,
    access_modes=["ReadWriteMany"],
    volume_mount=VolumeMount(name="calrissian-volume", mount_path="/calrissian"),
    persist=False,
)


bash_login_cm = load_config_map(
    name="bash-login",
    key="bash-login",
    file_name=os.path.join(current_dir, "config-maps/bash-login"),
    mount_path="/etc/profile.d/bash-login.sh",
)

bash_rc_cm = load_config_map(
    name="bash-rc",
    key="bash-rc",
    file_name=os.path.join(current_dir, "config-maps/bash-rc"),
    mount_path="/workspace/.bashrc",
)

init_cm = load_init_script(os.path.join(current_dir, "config-maps/init.sh"))

init_container = create_init_container(
    image=image,
    volume=workspace_volume,
    mount_path="/calrissian",
)

profile_1 = Profile(
    id=f"profile_1",
    groups=["group-a", "group-b"],
    definition=ProfileDefinition(
        display_name="Coder demo init script",
        description="This profile is used to demonstrate the use of an init script",
        slug="profile_1",
        default=False,
        kubespawner_override=KubespawnerOverride(
            cpu_guarantee=1,
            cpu_limit=2,
            mem_guarantee="4G",
            mem_limit="6G",
            image=image,
        ),
    ),
    node_selector=node_selector,
    volumes=[calrissian_volume, workspace_volume],
    config_maps=[
        init_cm,
        ConfigMap(
            name="dask-gateway-config",
            key="gateway",
            mount_path="/etc/dask/gateway.yaml",
            readonly=True,
        ),
        ConfigMap(
            name="dask-gateway-config-ws",
            key="gateway",
            mount_path="/workspace/.config/dask/gateway.yaml",
            readonly=True,
        ),
        bash_login_cm,
        bash_rc_cm,
    ],
    pod_env_vars={
        "HOME": "/workspace",
        "CONDA_ENVS_PATH": "/workspace/.envs",
        "CONDARC": "/workspace/.condarc",
        "XDG_RUNTIME_DIR": "/workspace/.local",
        "CODE_SERVER_WS": "/workspace/mastering-app-package",
        "DASK_GATEWAY": "http://traefik-dask-gw-jupyter-{{ spawner.user.name }}-dask-gateway.jupyter-{{ spawner.user.name }}.svc.cluster.local:80",
    },
    init_containers=[init_container],
    manifests=[localstack_manifest, dask_gateway_manifest],
    env_from_config_maps=["my-config"],
    env_from_secrets=["my-secret", "data-by-name"],
    secret_mounts=[
        SecretMount(
            name="aws-credentials-{{ spawner.user.name }}", mount_path="/workspace/.aws"
        ),
        SecretMount(name="data-by-name", mount_path="/workspace/.data-by-name"),
        SecretMount(
            name="eoepca-plus-secret-ro",
            mount_path="/workspace/.docker/config.json",
            sub_path=".dockerconfigjson",
        ),
    ],
    image_pull_secrets=[ImagePullSecret(name="eoepca-plus-secret-ro")],
)

profiles.append(profile_1)

config = Config(profiles=profiles)

with open("files/hub/config.yml", "w") as file:
    yaml.dump(config.dict(), file, width=200)
