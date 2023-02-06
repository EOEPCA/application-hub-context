import os
from abc import ABC
from http import HTTPStatus
from typing import TextIO

from kubernetes import client, config
from kubernetes.client import Configuration
from kubernetes.client.rest import ApiException
from kubernetes.config.config_exception import ConfigException


class ApplicationHubContext(ABC):
    def __init__(self, namespace, spawner, kubeconfig_file: TextIO = None, **kwargs):

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

        # update class dict with kwargs
        self.__dict__.update(kwargs)

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
            config.load_kube_config(config_file=kubeconfig)
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


class DefaulfApplicationHubContext(ApplicationHubContext):
    def get_profile_list(self):

        profile_list = [
            {
                "display_name": "JupyterLab",
                "slug": "iat_lab",
                "default": True,
                "kubespawner_override": {
                    "cpu_limit": 1,
                    "mem_limit": "4G",
                    "image": "jupyter/datascience-notebook",
                    "default_url": "lab",
                },
            },
        ]

        if ["developer"] in self.user_groups:
            profile_list.append(
                {
                    "display_name": "JupyterLab for developer",
                    "slug": "iat_lab_developers",
                    "default": True,
                    "kubespawner_override": {
                        "cpu_limit": 1,
                        "mem_limit": "4G",
                        "image": "jupyter/datascience-notebook",
                        "default_url": "lab",
                    },
                },
            )

        return profile_list

    def initialise(self):

        self.env_vars["A_VAR"] = "A_VALUE"

        self._set_pod_env_vars()

        for config_map in self._get_config_maps():

            if not self.is_config_map_created(name=config_map.name):
                message = f"configMap {config_map.name} does not "
                "exist in the namespace {self.namespace}"
                raise ValueError(message)

            if "mountPath" in config_map.keys():
                self.spawner.volume_mounts.extend(
                    [
                        {
                            "name": config_map.name,
                            "mountPath": config_map.mountPath,
                            "subPath": config_map.key,
                        },
                    ]
                )

                self.spawner.volumes.extend(
                    [
                        {
                            "name": config_map.name,
                            "configMap": {
                                "name": config_map.key,
                                "defaultMode": config_map.defaultMode,
                            },
                        },
                    ]
                )

    def dispose(self):
        return True

    def _set_pod_env_vars(self):

        for key, value in self.env_vars.items():
            self.spawner.environment[key] = value

    def _get_config_maps(self):

        config_maps = {}

        config_maps["aws-credentials"] = {
            "key": "aws-credentials",
            "name": "aws-credentials",
            "mountPath": "/home/jovyan/.aws/credentials",
            "defaultMode": "0660",
            "readOnly": "true",
        }
