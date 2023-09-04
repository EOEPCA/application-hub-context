import unittest

from addict import Dict
from kubernetes.client.rest import ApiException

from application_hub_context.app_hub_context import DefaultApplicationHubContext
from application_hub_context.models import ConfigMapEnvVarReference

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
    @classmethod
    def setUpClass(cls):

        cls.app_hub_context = DefaultApplicationHubContext(
            namespace="apphub-test",
            spawner=spawner,
            config_path="tests/data/config.yml",
            a=1,
            b=2,
        )

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

    def test_pod_env_vars_from_configmap_wrong_key(self):
        self.app_hub_context.env_vars["A_VAR_3"] = ConfigMapEnvVarReference(
            from_config_map={"name": "gitlabenv", "key": "GITLAB_TOKEN_WRONG"}
        )
        with self.assertRaises(KeyError):
            self.app_hub_context.set_pod_env_vars()
