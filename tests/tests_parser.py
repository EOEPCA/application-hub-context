import unittest

from application_hub_context.models import ConfigMap, Profile
from application_hub_context.parser import ConfigParser


class TestConfigParser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ws_config_parser = ConfigParser.read_file(
            config_path="tests/data/config.yml", user_groups=["group-2"]
        )
        cls.groups = ["group-2"]

    def test_obj(self):
        self.assertIs(type(self.ws_config_parser), ConfigParser)

    def test_profile(self):
        expected = {
            "id": "profile_1",
            "slug": "profile_1_slug",
            "groups": ["group-1"],
            "definition": {
                "display_name": "Profile 1",
                "slug": "profile_1_slug",
                "default": False,
                "kubespawner_override": {
                    "cpu_limit": 4,
                    "mem_limit": "8G",
                    "image": "eoepca/iat-jupyterlab:main",
                },
            },
            "default_url": "lab",
            "pod_env_vars": {"A": 10, "B": 20},
            "node_selector": {"k8s.acme.com/pool-name": "processing-node-pool"},
        }

        self.assertEqual(self.ws_config_parser.config.profiles[0], Profile(**expected))

    def test_get_profiles(self):
        self.assertEqual(len(self.ws_config_parser.get_profiles()), 1)

    def test_get_all_profiles(self):
        ws_config_parser = ConfigParser.read_file(
            config_path="tests/data/config.yml",
            user_groups=["group-1", "group-2"],
        )
        self.assertEqual(len(ws_config_parser.get_profiles()), 2)

    def test_get_no_profiles(self):
        ws_config_parser = ConfigParser.read_file(
            config_path="tests/data/config.yml",
            user_groups=["group-a", "group-b"],
        )
        self.assertFalse(ws_config_parser.get_profiles())

    def test_get_profile_by_id(self):
        profile = self.ws_config_parser.get_profile_by_id(profile_id="profile_1")

        self.assertEqual(profile.id, "profile_1")

    def test_get_profile_by_slug(self):
        self.assertEqual(
            self.ws_config_parser.get_profile_by_slug(slug="profile_1_slug").id,
            "profile_1",
        )

    def test_get_profile_volumes(self):
        print(self.ws_config_parser.get_profile_volumes(profile_id="profile_1"))

    def test_get_profile_config_maps(self):
        self.assertIsNotNone(
            self.ws_config_parser.get_profile_config_maps(profile_id="profile_2")
        )

    def test_get_profile_env_vars(self):
        expected = {"A": 10, "B": 20}
        self.assertDictEqual(
            self.ws_config_parser.get_profile_pod_env_vars(profile_id="profile_1"),
            expected,
        )

    def test_get_profile_volume(self):
        volumes = self.ws_config_parser.get_profile_volumes(profile_id="profile_2")
        volume = volumes[0]

        self.assertEqual(volume.volume_mount.name, "volume-workspace")

    def test_get_profile_secret(self):
        print(self.ws_config_parser.get_profile_secret(profile_id="profile_1"))

    def test_get_profile_roles(self):
        print(
            self.ws_config_parser.get_profile_roles(profile_id="profile_studio_coder")
        )

    def test_get_profile_default_url(self):
        self.assertEqual(
            self.ws_config_parser.get_profile_default_url(profile_id="profile_1"),
            "lab",
        )

    def test_get_profile_default_url_empty(self):
        self.assertEqual(
            self.ws_config_parser.get_profile_default_url(profile_id="profile_2"),
            None,
        )

    def test_get_config_maps(self):
        config_maps = self.ws_config_parser.get_profile_config_maps(
            profile_id="profile_2"
        )

        self.assertIsNotNone(config_maps)

    def test_get_config_maps_type(self):
        config_maps = self.ws_config_parser.get_profile_config_maps(
            profile_id="profile_2"
        )

        self.assertEqual(type(config_maps[0]), ConfigMap)

    def test_get_config_maps_name(self):
        config_maps = self.ws_config_parser.get_profile_config_maps(
            profile_id="profile_2"
        )

        self.assertEqual(config_maps[0].name, "aws-credentials")

    def test_get_empty_config_maps(self):
        config_maps = self.ws_config_parser.get_profile_config_maps(
            profile_id="profile_4"
        )

        self.assertIsNotNone(config_maps)
