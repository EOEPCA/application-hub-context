import unittest
from unittest.mock import patch

from addict import Dict
from kubernetes import client

from application_hub_context.app_hub_context import DefaultApplicationHubContext

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


class TestK8s(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        api_client = client.ApiClient(client.Configuration(host="https://kubernetes.invalid"))
        cls.addClassCleanup(api_client.close)
        patcher = patch(
            "application_hub_context.app_hub_context.ApplicationHubContext._get_api_client",
            return_value=api_client,
        )
        patcher.start()
        cls.addClassCleanup(patcher.stop)

        cls.app_hub_context = DefaultApplicationHubContext(
            namespace="a_namespace",
            spawner=spawner,
            config_path="tests/data/config.yml",
            a=1,
            b=2,
        )

    def test_obj(self):
        self.assertIs(type(self.app_hub_context), DefaultApplicationHubContext)

    def test_client(self):
        self.assertIsInstance(self.app_hub_context._get_core_v1_api(), client.CoreV1Api)

    def test_batch(self):
        self.assertIsInstance(
            self.app_hub_context._get_batch_v1_api(), client.BatchV1Api
        )

    def test_rbac(self):
        self.assertIsInstance(
            self.app_hub_context._get_rbac_authorization_v1_api(),
            client.RbacAuthorizationV1Api,
        )
