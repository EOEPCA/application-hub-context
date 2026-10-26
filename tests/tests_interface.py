import unittest
from copy import deepcopy
from unittest.mock import Mock, patch

from kubernetes import client

from addict import Dict
from kubernetes.client.rest import ApiException

from application_hub_context.app_hub_context import DefaultApplicationHubContext
from application_hub_context.models import (
    ConfigMapEnvVarReference,
    Role,
    Subject,
    SubjectKind,
)

group = Dict()
group.name = "group_a"
groups = [group]
spawner = Dict()

spawner.user_options = {"profile": "selected_slug"}
spawner.user.name = "alice"
spawner.user.groups = groups
spawner.environment = {}

spawner.profile_list = [
    {
        "display_name": "Studio Labs version 0.4",
        "slug": "ellip_studio_notebook",
        "default": False,
        "kubespawner_override": {
            "cpu_limit": 1,
            "mem_limit": "8G",
            "image": "cr.terradue.com/ellip-studio/studio-lab:0.1",
        },
    },
    {
        "display_name": "Studio Coder version 0.8",
        "slug": "ellip_studio_coder_slug",
        "default": False,
        "kubespawner_override": {
            "cpu_limit": 1,
            "mem_limit": "8G",
            "image": "cr.terradue.com/ellip-studio/studio-coder:0.8",
        },
    },
]


class TestConstructor(unittest.TestCase):
    def setUp(self):
        api_client = client.ApiClient(client.Configuration(host="https://kubernetes.invalid"))
        self.addCleanup(api_client.close)
        patcher = patch(
            "application_hub_context.app_hub_context.ApplicationHubContext._get_api_client",
            return_value=api_client,
        )
        patcher.start()
        self.addCleanup(patcher.stop)
        test_spawner = deepcopy(spawner)
        test_spawner.log = Mock()
        self.app_hub_context = DefaultApplicationHubContext(
            namespace="apphub-test",
            spawner=test_spawner,
            config_path="tests/data/config.yml",
            a=1,
            b=2,
        )

        def read_config_map(name, namespace):
            if name != "gitlabenv":
                raise ApiException(status=404, reason="ConfigMap not found")
            return client.V1ConfigMap(data={"GITLAB_TOKEN": "adafeaflwejfowe"})

        self.app_hub_context.core_v1_api.read_namespaced_config_map = Mock(
            side_effect=read_config_map
        )
        self.role_read = Mock(side_effect=[ApiException(status=404), Mock()])
        self.binding_read = Mock(side_effect=[ApiException(status=404), Mock()])
        rbac = self.app_hub_context.rbac_authorization_v1_api
        rbac.read_namespaced_role = self.role_read
        rbac.read_namespaced_role_binding = self.binding_read
        rbac.create_namespaced_role = Mock(return_value=Mock())
        rbac.create_namespaced_role_binding = Mock(return_value=Mock())

    def test_obj(self):
        self.assertIs(type(self.app_hub_context), DefaultApplicationHubContext)

    def test_kwarg_1(self):
        self.assertEqual(self.app_hub_context.a, 1)

    def test_kwarg_2(self):
        self.assertTrue(hasattr(self.app_hub_context, "b"))

    def test_profile_slug_1(self):
        self.assertEqual(self.app_hub_context.profile_slug, "selected_slug")

    def test_pod_env_vars(self):
        self.app_hub_context.env_vars["A_VAR"] = "A_VALUE"

        self.app_hub_context.set_pod_env_vars()

        self.assertEqual(self.app_hub_context.spawner.environment["A_VAR"], "A_VALUE")

    def test_pod_env_vars_from_configmap(self):
        self.app_hub_context.env_vars["A_VAR_1"] = ConfigMapEnvVarReference(
            from_config_map={"name": "gitlabenv", "key": "GITLAB_TOKEN"}
        )
        self.app_hub_context.set_pod_env_vars()
        self.assertEqual(
            self.app_hub_context.spawner.environment["A_VAR_1"], "adafeaflwejfowe"
        )

    def test_pod_env_vars_from_configmap_wrong_configmap(self):
        self.app_hub_context.env_vars["A_VAR_2"] = ConfigMapEnvVarReference(
            from_config_map={"name": "gitlabenv_wrong", "key": "GITLAB_TOKEN"}
        )
        with self.assertRaises(ApiException):
            self.app_hub_context.set_pod_env_vars()

        self.app_hub_context.env_vars.pop("A_VAR_2")

    def test_pod_env_vars_from_configmap_wrong_key(self):
        self.app_hub_context.env_vars["A_VAR_3"] = ConfigMapEnvVarReference(
            from_config_map={"name": "gitlabenv", "key": "GITLAB_TOKEN_WRONG"}
        )
        with self.assertRaises(KeyError):
            self.app_hub_context.set_pod_env_vars()

        self.app_hub_context.env_vars.pop("A_VAR_3")

    def test_role_and_role_binding_creation(self):

        pod_reader_role = Role(
            name="pod_reader_role",
            resources=["pods", "pods/log"],
            verbs=["get", "list", "watch", "create", "update", "patch", "delete"],
        )

        self.app_hub_context.create_role(
            name=pod_reader_role.name,
            resources=pod_reader_role.resources,
            verbs=pod_reader_role.verbs,
        )

        default_subject = Subject(name="default", kind=SubjectKind.service_account)

        self.app_hub_context.create_role_binding(
            name="pod_reader_role_binding",
            subjects=[default_subject],
            role=pod_reader_role,
        )

        rbac = self.app_hub_context.rbac_authorization_v1_api
        rbac.create_namespaced_role.assert_called_once()
        rbac.create_namespaced_role_binding.assert_called_once()
        namespace, role_body = rbac.create_namespaced_role.call_args.args
        self.assertEqual(namespace, "apphub-test")
        self.assertEqual(role_body.metadata.name, "pod_reader_role")
        self.assertEqual(role_body.rules[0].resources, ["pods", "pods/log"])
        namespace, binding_body = rbac.create_namespaced_role_binding.call_args.args
        self.assertEqual(namespace, "apphub-test")
        self.assertEqual(binding_body.role_ref.name, "pod_reader_role")
        self.assertEqual(binding_body.subjects[0]["name"], "default")
