import yaml
from jinja2 import Template
from application_hub_context.models import Config

undefined = object()


class ConfigParser:
    def __init__(self, config_data, user_groups):
        """returns a config parser"""
        self.config = Config(**config_data)
        self.user_groups = user_groups

    @classmethod
    def _render_templates(cls, obj, context):
        """Recursively render Jinja templates in strings only."""
        if isinstance(obj, str):
            if "{{" in obj:
                return Template(obj).render(**context)
            return obj

        if isinstance(obj, list):
            return [cls._render_templates(i, context) for i in obj]

        if isinstance(obj, dict):
            return {
                k: cls._render_templates(v, context)
                for k, v in obj.items()
            }

        return obj

    @classmethod
    def read_file(cls, config_path, user_groups, spawner, namespace):
        with open(config_path, "r") as stream:
            raw_content = stream.read()

        try:
            # Parse YAML first (SAFE)
            config_data = yaml.safe_load(raw_content)

            # Render templates selectively
            context = {
                "spawner": spawner,
                "namespace": namespace,
            }
            config_data = cls._render_templates(config_data, context)

        except yaml.YAMLError as exc:
            raise RuntimeError(f"Invalid YAML in {config_path}: {exc}") from exc
        except Exception as exc:
            raise RuntimeError(
                f"Error processing config file {config_path}: {exc}"
            ) from exc

        return cls(config_data=config_data, user_groups=user_groups)

    def get_profiles(self):
        """lists the profiles"""
        profiles = []
        for profile in self.config.profiles:
            if bool(set(profile.groups) & set(self.user_groups)):
                profiles.append(profile.definition.dict())

        if not profiles:
            profiles.append(
                {
                    "display_name": "Pending configuration",
                    "description": "Please contact your "
                    "administrator to configure your profile(s).",
                    "kubespawner_override": {},
                }
            )

        return profiles

    def get_profile_by_id(self, profile_id):
        """returns a profile using the id or None"""
        try:
            return [
                profile for profile in self.config.profiles if profile.id == profile_id
            ][0]
        except IndexError:
            pass

    def get_profile_volumes(self, profile_id):
        """returns the profile volumes"""
        try:
            return [
                volume
                for volume in self.get_profile_by_id(profile_id=profile_id).volumes
            ]
        except TypeError:
            return []

    def get_profile_by_slug(self, slug):
        try:
            return [
                profile
                for profile in self.config.profiles
                if profile.definition.slug == slug
            ][0]
        except IndexError:
            pass

    def get_profile_config_maps(self, profile_id):
        """returns the profile config maps"""
        try:
            return [
                config_map
                for config_map in self.get_profile_by_id(
                    profile_id=profile_id
                ).config_maps
            ]
        except TypeError:
            return []

    def get_profile_pod_env_vars(self, profile_id):
        """returns the profile config maps"""
        try:
            return self.get_profile_by_id(profile_id=profile_id).pod_env_vars
        except AttributeError:
            pass

    def get_profile_secret(self, profile_id):
        """returns the profile secret"""
        try:
            return self.get_profile_by_id(profile_id=profile_id).image_pull_secret
        except AttributeError:
            pass

    def get_profile_roles(self, profile_id):
        """returns the profile config maps"""
        try:
            return self.get_profile_by_id(profile_id=profile_id).roles
        except AttributeError:
            pass

    def get_profile_default_url(self, profile_id):
        """returns the profile default url"""
        try:
            return self.get_profile_by_id(profile_id=profile_id).default_url
        except AttributeError:
            pass

    def get_profile_role_bindings(self, profile_id):
        """returns the profile role bindings"""
        try:
            return self.get_profile_by_id(profile_id=profile_id).role_bindings
        except AttributeError:
            pass

    def get_profile_image_pull_secrets(self, profile_id):
        """returns the image pull secrets"""
        return self.get_profile_by_id(profile_id=profile_id).image_pull_secrets

    def get_profile_init_containers(self, profile_id):
        """returns the image pull secrets"""
        return self.get_profile_by_id(profile_id=profile_id).init_containers

    def get_profile_manifests(self, profile_id):
        """returns the profile manifests"""
        try:
            return self.get_profile_by_id(profile_id=profile_id).manifests
        except AttributeError:
            pass

    def get_profile_env_from_config_maps(self, profile_id):
        """returns the profile env from config maps"""
        try:
            return self.get_profile_by_id(profile_id=profile_id).env_from_config_maps
        except AttributeError:
            pass

    def get_profile_env_from_secrets(self, profile_id):
        """returns the profile env from secrets"""
        try:
            return self.get_profile_by_id(profile_id=profile_id).env_from_secrets
        except AttributeError:
            pass
        
    def get_profile_secret_mounts(self, profile_id):
        """returns the profile secret mounts"""
        try:
            return self.get_profile_by_id(profile_id=profile_id).secret_mounts
        except AttributeError:
            pass