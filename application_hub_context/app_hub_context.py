import os
import time
from abc import ABC
from http import HTTPStatus
from typing import Dict, TextIO

from kubernetes import client, config
from kubernetes.client import Configuration
from kubernetes.client.rest import ApiException
from kubernetes.config.config_exception import ConfigException

from application_hub_context.models import (
    ConfigMapEnvVarReference,
    Role,
    RoleBinding,
    Subject,
    Verb,
)
from application_hub_context.parser import ConfigParser


class ApplicationHubContext(ABC):
    def __init__(
        self,
        namespace,
        spawner,
        config_path: str,
        kubeconfig_file: TextIO = None,
        **kwargs,
    ):
        # k8s
        self.kubeconfig_file = kubeconfig_file
        self.api_client = self._get_api_client(self.kubeconfig_file)
        self.core_v1_api = self._get_core_v1_api()
        self.batch_v1_api = self._get_batch_v1_api()
        self.rbac_authorization_v1_api = self._get_rbac_authorization_v1_api()
        self.namespace = namespace

        self.spawner = spawner
        # get the groups the user belongs to
        self.user_groups = [group.name for group in self.spawner.user.groups]
        # try to get the profile slug (e.g. during a hook call)
        self.profile_slug = self.spawner.user_options.get("profile", None)
        # pod env vars
        self.env_vars = {}

        # loads config
        self.config_parser = ConfigParser.read_file(
            config_path=config_path, user_groups=self.user_groups
        )

        # update class dict with kwargs
        self.__dict__.update(kwargs)

    def set_pod_env_vars(self, **kwargs):
        extended_vars = {**self.env_vars, **kwargs}

        for key, value in extended_vars.items():
            if isinstance(value, str):
                # If value is a simple string
                self.spawner.environment[key] = value
            elif isinstance(value, ConfigMapEnvVarReference):
                # If value must be retrieved from an existing configmap
                config_map_name = value.from_config_map.name
                config_map_key = value.from_config_map.key
                try:
                    api_response = self.core_v1_api.read_namespaced_config_map(
                        name=config_map_name, namespace=self.namespace
                    )
                    if config_map_key not in api_response.data:
                        raise KeyError(
                            f"Key '{config_map_key}' not found "
                            f"in config map '{config_map_name}'"
                        )
                    self.spawner.environment[key] = api_response.data[config_map_key]
                except ApiException as e:
                    print("Exception in read_namespaced_config_map: %s\n" % e)
                    raise
                except KeyError as e:
                    print("Configuration error: %s\n" % e)
                    raise

    @staticmethod
    def _get_api_client(kubeconfig_file: TextIO = None):
        try:
            config.load_incluster_config()  # raises if not in cluster
            api_client = client.ApiClient()
            return api_client
        except ConfigException as exception:
            print(exception)

        proxy_url = os.getenv("HTTP_PROXY", None)
        kubeconfig = os.getenv("KUBECONFIG", None)

        if proxy_url:
            api_config = Configuration(host=proxy_url)
            api_config.proxy = proxy_url
            api_client = client.ApiClient(api_config)

        elif kubeconfig:
            # this is needed because kubernetes-python does not consider
            # the KUBECONFIG env variable
            config.load_kube_config(config_file=kubeconfig)
            api_client = client.ApiClient()
        elif kubeconfig_file:
            config.load_kube_config(config_file=kubeconfig_file)
            api_client = client.ApiClient()
        else:
            # if nothing is specified, kubernetes-python will use the file
            # in ~/.kube/config
            config.load_kube_config()
            api_client = client.ApiClient()

        return api_client

    def _get_core_v1_api(self) -> client.CoreV1Api:
        return client.CoreV1Api(api_client=self.api_client)

    def _get_batch_v1_api(self) -> client.BatchV1Api:
        return client.BatchV1Api(api_client=self.api_client)

    def _get_rbac_authorization_v1_api(self) -> client.RbacAuthorizationApi:
        return client.RbacAuthorizationV1Api(self.api_client)

    def is_object_created(self, read_method, **kwargs):
        read_methods = {}

        read_methods["read_namespace"] = self.core_v1_api.read_namespace
        read_methods[
            "read_namespaced_role"
        ] = self.rbac_authorization_v1_api.read_namespaced_role  # noqa: E501
        read_methods[
            "read_namespaced_role_binding"
        ] = self.rbac_authorization_v1_api.read_namespaced_role_binding  # noqa: E501

        read_methods[
            "read_namespaced_config_map"
        ] = self.core_v1_api.read_namespaced_config_map  # noqa: E501

        read_methods[
            "read_namespaced_persistent_volume_claim"
        ] = self.core_v1_api.read_namespaced_persistent_volume_claim  # noqa: E501

        read_methods[
            "read_namespaced_secret"
        ] = self.core_v1_api.read_namespaced_secret  # noqa: E501
        try:
            if read_method in [
                "read_namespaced_config_map",
                "read_namespaced_role",
                "read_namespaced_role_binding",
                "read_namespaced_persistent_volume_claim",
                "read_namespaced_secret",
            ]:
                read_methods[read_method](namespace=self.namespace, **kwargs)
            else:
                read_methods[read_method](self.namespace)
        except ApiException as exc:
            if exc.status == HTTPStatus.NOT_FOUND:
                return None
            else:
                raise exc
        return read_methods

    def is_namespace_created(self, **kwargs):
        return self.is_object_created("read_namespace", **kwargs)

    def is_namespace_deleted(self, **kwargs):
        """Helper function for retry in dispose"""
        return not self.is_namespace_created()

    def is_role_binding_created(self, **kwargs):
        return self.is_object_created("read_namespaced_role_binding", **kwargs)

    def is_role_created(self, **kwargs):
        return self.is_object_created("read_namespaced_role", **kwargs)

    def is_config_map_created(self, **kwargs):
        return self.is_object_created("read_namespaced_config_map", **kwargs)

    def is_pvc_created(self, **kwargs):
        return self.is_object_created(
            "read_namespaced_persistent_volume_claim", **kwargs
        )  # noqa: E501

    def is_image_pull_secret_created(self, **kwargs):
        return self.is_object_created("read_namespaced_secret", **kwargs)

    def get_profile_list(self):
        pass

    def initialise(self):
        pass

    def dispose(self):
        pass

    @staticmethod
    def retry(fun, max_tries=10, interval=1, **kwargs):
        for i in range(max_tries):
            try:
                time.sleep(interval)
                return fun(**kwargs)
            except ApiException as exc:
                if exc.status.value < 500 and exc.status.value != 429:
                    # Useless to retry against a 4xx/not-429
                    raise exc
            except Exception:
                continue
        if i == max_tries:
            raise ApiException()

    def create_configmap(
        self,
        name,
        key,
        content,
        annotations: Dict = {},
        labels: Dict = {},
    ):
        metadata = client.V1ObjectMeta(
            annotations=annotations,
            deletion_grace_period_seconds=30,
            labels=labels,
            name=name,
            namespace=self.namespace,
        )

        data = {}
        data[key] = content

        config_map = client.V1ConfigMap(
            api_version="v1",
            kind="ConfigMap",
            data=data,
            metadata=metadata,
        )

        try:
            response = self.core_v1_api.create_namespaced_config_map(
                namespace=self.namespace,
                body=config_map,
                pretty=True,
            )

            if not self.retry(self.is_config_map_created, name=name, interval=2):
                raise ApiException(http_resp=response)
            self.spawner.log.info(f"config map {name} created")
            return response

        except ApiException as e:
            self.spawner.log.info(
                f"config map {name} not created in the time interval assigned"
            )
            raise e

    def create_pvc(
        self,
        name,
        access_modes,
        size,
        storage_class,
    ):
        if self.is_pvc_created(name=name):
            return self.core_v1_api.read_namespaced_persistent_volume_claim(
                name=name, namespace=self.namespace
            )

        metadata = client.V1ObjectMeta(name=name, namespace=self.namespace)

        spec = client.V1PersistentVolumeClaimSpec(
            access_modes=access_modes,
            resources=client.V1ResourceRequirements(
                requests={"storage": size}
            ),  # noqa: E501
        )

        spec.storage_class_name = storage_class

        body = client.V1PersistentVolumeClaim(metadata=metadata, spec=spec)

        try:
            response = self.core_v1_api.create_namespaced_persistent_volume_claim(  # noqa: E501
                self.namespace, body, pretty=True
            )

            if not self.retry(self.is_pvc_created, name=name):
                raise ApiException(http_resp=response)
            self.spawner.log.info(f"pvc {name} created")
            return response
        except ApiException as e:
            self.spawner.log.error(
                f"pvc {name} not created in the time interval assigned:"
                f" Exception when calling get status: {e}\n"
            )
            raise e

    def delete_pvc(self, name):
        try:
            response = self.core_v1_api.delete_namespaced_persistent_volume_claim(
                name=name, namespace=self.namespace
            )
            return response
        except ApiException as e:
            self.spawner.log.error(f"Exception deleting pvc {name}: {e}\n")

    def delete_config_map(self, name):
        try:
            response = self.core_v1_api.delete_namespaced_config_map(
                name=name, namespace=self.namespace
            )
            return response
        except ApiException as e:
            self.spawner.log.error(f"Exception deleting config map {name}: {e}\n")

    def delete_role_binding(self, role_binding: RoleBinding):
        try:
            self.rbac_authorization_v1_api.delete_namespaced_role_binding(
                name=role_binding.name, namespace=self.namespace
            )
        except ApiException as e:
            self.spawner.log.error(
                f"Exception deleting role binding {role_binding.name}: {e}\n"
            )

        try:
            self.rbac_authorization_v1_api.delete_namespaced_role(
                name=role_binding.role.name, namespace=self.namespace
            )
        except ApiException as e:
            self.spawner.log.error(
                f"Exception deleting role {role_binding.role.name}: {e}\n"
            )

    def create_role_binding(self, name: str, subjects: [Subject], role: Role):
        if self.is_role_binding_created(name=name):
            return self.rbac_authorization_v1_api.read_namespaced_role_binding(
                name=name, namespace=self.namespace
            )

        metadata = client.V1ObjectMeta(name=name, namespace=self.namespace)

        role_ref = client.V1RoleRef(api_group="", kind="Role", name=role.name)

        subject_list = []
        for subject in subjects:
            subject = client.models.V1Subject(
                api_group="",
                kind=subject.kind.value,
                name=subject.name,
                namespace=self.namespace,
            )
            subject_list.append(subject)

        body = client.V1RoleBinding(
            metadata=metadata, role_ref=role_ref, subjects=subject_list
        )  # noqa: E501

        try:
            response = self.rbac_authorization_v1_api.create_namespaced_role_binding(  # noqa: E501
                self.namespace, body, pretty=True
            )

            if not self.retry(self.is_role_binding_created, name=name):
                raise ApiException(http_resp=response)
            self.spawner.log.info(f"role binding {name} created")
            return response
        except ApiException as e:
            self.spawner.log.error(
                f"role binding {name} not created in the time interval assigned:"
                f" Exception when calling get status: {e}\n"
            )
            raise e

    def delete_image_pull_secret(self, name):
        try:
            response = self.core_v1_api.delete_namespaced_secret(
                name=name, namespace=self.namespace
            )
            return response
        except ApiException as e:
            self.spawner.log.error(
                f"Exception deleting image pull secret {name}: {e}\n"
            )

    def create_role(
        self,
        name: str,
        verbs: list[Verb],
        resources: list[str] = [""],
        api_groups: list[str] = ["*"],
    ):

        if self.is_role_created(name=name):
            return self.rbac_authorization_v1_api.read_namespaced_role(
                name=name, namespace=self.namespace
            )

        metadata = client.V1ObjectMeta(name=name, namespace=self.namespace)

        rule = client.V1PolicyRule(
            api_groups=api_groups, resources=resources, verbs=verbs
        )

        body = client.V1Role(metadata=metadata, rules=[rule])

        try:
            response = (
                self.rbac_authorization_v1_api.create_namespaced_role(  # noqa: E501
                    self.namespace, body, pretty=True
                )
            )

            if not self.retry(self.is_role_created, name=name):
                raise ApiException(http_resp=response)
            self.spawner.log.info(f"role {name} created")
            return response

        except ApiException as e:
            self.spawner.log.error(
                f"role {name} not created in the time interval assigned: "
                f"Exception when calling get status: {e}\n"
            )
            raise e

    def create_image_pull_secret(self, name: str, data):

        if self.is_image_pull_secret_created(name=name):

            return self.core_v1_api.read_namespaced_secret(
                namespace=self.namespace, name=name
            )  # noqa: E501

        metadata = {"name": name, "namespace": self.namespace}

        secret_data = {".dockerconfigjson": data}

        secret = client.V1Secret(
            api_version="v1",
            data=secret_data,
            kind="Secret",
            metadata=metadata,
            type="kubernetes.io/dockerconfigjson",
        )

        try:
            response = self.core_v1_api.create_namespaced_secret(
                namespace=self.namespace,
                body=secret,
                pretty=True,
            )

            if not self.retry(self.is_image_pull_secret_created, name=name, interval=1):
                raise ApiException(http_resp=response)
            self.spawner.log.info(f"image pull secret {name} created")
            return response

        except ApiException as e:
            self.spawner.log.error(
                f"image pull secret {name} not created " "in the time interval assigned"
            )
            raise e

    def patch_service_account(self, secret_name: str):
        # adds a secret to the namespace default service account

        service_account_body = self.core_v1_api.read_namespaced_service_account(
            name="default", namespace=self.namespace
        )

        self.spawner.log.info(
            "service_account_body.image_pull_secrets "
            f"{service_account_body.image_pull_secrets}"
        )
        self.spawner.log.info(
            f"service_account_body.secrets {service_account_body.secrets}"
        )

        if service_account_body.secrets is None:
            service_account_body.secrets = []

        if service_account_body.image_pull_secrets is None:
            service_account_body.image_pull_secrets = []

        for elem in service_account_body.image_pull_secrets:
            if elem.name == secret_name:
                return

        self.spawner.log.info(f"patching service account with secret {secret_name}")
        service_account_body.secrets.append({"name": secret_name})
        service_account_body.image_pull_secrets.append({"name": secret_name})

        try:
            self.core_v1_api.patch_namespaced_service_account(
                name="default",
                namespace=self.namespace,
                body=service_account_body,
                pretty=True,
            )
        except ApiException as e:
            raise e


class DefaultApplicationHubContext(ApplicationHubContext):
    def get_profile_list(self):
        return self.config_parser.get_profiles()

    def initialise(self):
        # set the spawner timeout to 10 minutes
        self.spawner.http_timeout = 600

        # get the profile id from the profile definition slug
        profile_id = self.config_parser.get_profile_by_slug(slug=self.profile_slug).id

        self.spawner.log.info(
            f"Initialising {self.profile_slug} (profile id {profile_id})"
        )

        self.spawner.image = self.config_parser.get_profile_by_slug(
            slug=self.profile_slug
        ).definition.kubespawner_override.image

        # pod limits
        self.spawner.cpu_limit = self.config_parser.get_profile_by_slug(
            slug=self.profile_slug
        ).definition.kubespawner_override.cpu_limit
        self.spawner.mem_limit = self.config_parser.get_profile_by_slug(
            slug=self.profile_slug
        ).definition.kubespawner_override.mem_limit
        if (
            self.config_parser.get_profile_by_slug(
                slug=self.profile_slug
            ).definition.kubespawner_override.extra_resource_limits
            is not None
        ):
            self.spawner.extra_resource_limits = self.config_parser.get_profile_by_slug(
                slug=self.profile_slug
            ).definition.kubespawner_override.extra_resource_limits

        # pod guarantees
        cpu_guarantee = self.config_parser.get_profile_by_slug(
            slug=self.profile_slug
        ).definition.kubespawner_override.cpu_guarantee
        if cpu_guarantee is not None:
            self.spawner.cpu_guarantee = cpu_guarantee

        mem_guarantee = self.config_parser.get_profile_by_slug(
            slug=self.profile_slug
        ).definition.kubespawner_override.mem_guarantee
        if cpu_guarantee is not None:
            self.spawner.mem_guarantee = mem_guarantee

        extra_resource_guarantee = self.config_parser.get_profile_by_slug(
            slug=self.profile_slug
        ).definition.kubespawner_override.extra_resource_limits

        if extra_resource_guarantee is not None:
            self.spawner.extra_resource_guarantees = extra_resource_guarantee

        # node selector
        self.spawner.node_selector = self.config_parser.get_profile_by_slug(
            slug=self.profile_slug
        ).node_selector
        self.spawner.log.info(
            f"Initialising pod with image {self.spawner.image} on node pool"
            f"{self.spawner.node_selector}, cpu_limit: "
            f"{self.spawner.cpu_limit}, mem_limit: {self.spawner.mem_limit}"
        )

        # set the pod env vars
        config_env_vars = self.config_parser.get_profile_pod_env_vars(
            profile_id=profile_id
        )
        self.set_pod_env_vars(**(config_env_vars or {}))

        # process the config maps
        config_maps = self.config_parser.get_profile_config_maps(profile_id=profile_id)

        if config_maps:
            for config_map in config_maps:
                try:
                    if not self.is_config_map_created(name=config_map.name):
                        self.spawner.log.info(f"Creating configmap {config_map.name}")
                        self.create_configmap(
                            name=config_map.name,
                            key=config_map.key,
                            content=config_map.content,
                            annotations=None,
                            labels=None,
                        )
                    self.spawner.log.info(f"Mounting configmap {config_map.name}")
                    self.spawner.volume_mounts.extend(
                        [
                            {
                                "name": config_map.name,
                                "mountPath": config_map.mount_path,
                                "subPath": config_map.key,
                            },
                        ]
                    )

                    self.spawner.volumes.extend(
                        [
                            {
                                "name": config_map.name,
                                "configMap": {"name": config_map.key},
                            }
                        ]
                    )
                except Exception as err:
                    self.spawner.log.error(f"Unexpected {err=}, {type(err)=}")
                    self.spawner.log.error(
                        f"Skipping creation of configmap {config_map.name}"
                    )

        #  process the volumes
        volumes = self.config_parser.get_profile_volumes(profile_id=profile_id)

        if volumes:
            for volume in volumes:
                self.spawner.log.info(f"Mounting volume {volume.name}")
                try:
                    if not self.is_pvc_created(name=volume.claim_name):
                        self.spawner.log.info(
                            f"Creating volume claim {volume.claim_name})"
                        )
                        self.create_pvc(
                            name=volume.claim_name,
                            access_modes=volume.access_modes,
                            size=volume.size,
                            storage_class=volume.storage_class,
                        )
                    self.spawner.log.info(
                        f"Mounting volume {volume.name} (claim {volume.claim_name}))"
                    )
                    self.spawner.volume_mounts.extend(
                        [
                            {
                                "name": volume.volume_mount.name,
                                "mountPath": volume.volume_mount.mount_path,
                            },
                        ]
                    )

                    self.spawner.volumes.extend(
                        [
                            {
                                "name": volume.name,
                                "persistentVolumeClaim": {
                                    "claimName": volume.claim_name
                                },
                            }
                        ]
                    )

                except Exception as err:
                    self.spawner.log.error(f"Unexpected {err}, {type(err)}")
                    self.spawner.log.error(f"Skipping creation of volume {volume.name}")

            # process the role bindings
            role_bindings = self.config_parser.get_profile_role_bindings(
                profile_id=profile_id
            )

            if role_bindings:
                for role_binding in role_bindings:
                    self.spawner.log.info(f"Creating role binding {role_binding.name}")
                    try:
                        # checking if role binding is already created
                        if not self.is_role_binding_created(name=role_binding.name):

                            # checking if role is already created
                            if not self.is_role_created(name=role_binding.role.name):
                                self.spawner.log.info(
                                    f"Creating role {role_binding.role.name}"
                                )
                                self.create_role(
                                    name=role_binding.role.name,
                                    verbs=role_binding.role.verbs,
                                    resources=role_binding.role.resources,
                                    api_groups=role_binding.role.api_groups,
                                )

                            # creating role binding
                            self.create_role_binding(
                                name=role_binding.name,
                                role=role_binding.role,
                                subjects=role_binding.subjects,
                            )

                    except Exception as err:
                        self.spawner.log.error(f"Unexpected {err}, {type(err)}")
                        self.spawner.log.error(
                            f"Skipping creation of role binding {role_binding.name}"
                        )
            # process the role bindings
            image_pull_secrets = self.config_parser.get_profile_image_pull_secrets(
                profile_id=profile_id
            )

            if image_pull_secrets:
                for image_pull_secret in image_pull_secrets:
                    self.spawner.log.info(
                        f"Create image pull secret {image_pull_secret.name}"
                    )
                    try:
                        if not self.is_image_pull_secret_created(
                            name=image_pull_secret.name
                        ):
                            self.spawner.log.info(
                                f"Creating image pull secret {image_pull_secret.name})"
                            )
                            self.create_image_pull_secret(
                                name=image_pull_secret.name,
                                data=image_pull_secret.data,
                            )
                    except Exception as err:
                        self.spawner.log.error(f"Unexpected {err}, {type(err)}")
                        self.spawner.log.error(
                            "Skipping creation of image pull secret"
                            f" {image_pull_secret.name}"
                        )

                    self.patch_service_account(secret_name=image_pull_secret.name)

            # process the init containers
            init_containers = self.config_parser.get_profile_init_containers(
                profile_id=profile_id
            )

            if init_containers:
                for init_container in init_containers:
                    self.spawner.log.info(
                        f"Create init container {init_container.name}"
                    )
                    try:
                        self.spawner.init_containers.extend(
                            [
                                {
                                    "name": init_container.name,
                                    "image": init_container.image,
                                    "command": init_container.command,
                                    "volumeMounts": [
                                        volume_mount.model_dump(
                                            by_alias=True, exclude_none=True
                                        )
                                        for volume_mount in init_container.volume_mounts
                                    ],
                                }
                            ]
                        )
                    except Exception as err:
                        self.spawner.log.error(f"Unexpected {err}, {type(err)}")
                        self.spawner.log.error(
                            f"Skipping creation of init container {init_container.name}"
                        )

    def dispose(self):
        profile_id = self.config_parser.get_profile_by_slug(slug=self.profile_slug).id

        self.spawner.log.info(
            f"Disposing {self.profile_slug} instance (profile id {profile_id})"
        )

        # process the config maps
        config_maps = self.config_parser.get_profile_config_maps(profile_id=profile_id)
        if config_maps:
            for config_map in config_maps:
                if not config_map.persist:
                    self.spawner.log.info(f"Dispose config map {config_map.name}")

                    self.delete_config_map(name=config_map.name)

        # deal with the volumes
        volumes = self.config_parser.get_profile_volumes(profile_id=profile_id)

        if volumes:
            for volume in volumes:
                if not volume.persist:
                    self.spawner.log.info(
                        f"Dispose volume {volume.name}, claim {volume.claim_name}"
                    )

                    self.delete_pvc(name=volume.claim_name)

        # deal with the role bindings
        role_bindings = self.config_parser.get_profile_role_bindings(
            profile_id=profile_id
        )

        if role_bindings:
            for role_binding in role_bindings:
                if not role_binding.persist:
                    self.spawner.log.info(f"Dispose role binding {role_binding.name}")
                    self.delete_role_binding(role_binding=role_binding)

        # deal with the image pull secrets
        image_pull_secrets = self.config_parser.get_profile_image_pull_secrets(
            profile_id=profile_id
        )

        if image_pull_secrets:
            for image_pull_secret in image_pull_secrets:
                if not image_pull_secret.persist:
                    self.spawner.log.info(
                        f"Dispose image pull secret {image_pull_secret.name}"
                    )
                    self.delete_image_pull_secret(name=image_pull_secret.name)

                    service_account_body = (
                        self.core_v1_api.read_namespaced_service_account(
                            name="default", namespace=self.namespace
                        )
                    )
                    for elem in service_account_body.image_pull_secrets:
                        if elem.name == image_pull_secret.name:

                            service_account_body.image_pull_secrets.remove(
                                {"name": elem.name}
                            )

                            self.spawner.log.info(
                                f"Remove image pull secret {image_pull_secret.name}"
                                " from default service account"
                            )

                            try:
                                self.core_v1_api.patch_namespaced_service_account(
                                    name="default",
                                    namespace=self.namespace,
                                    body=service_account_body,
                                    pretty=True,
                                )
                            except ApiException as e:
                                raise e

                            break
