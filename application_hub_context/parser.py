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
    def read_file(cls, config_path, user_groups, spawner):
        """reads a config file encoded in YAML"""
        with open(config_path, "r") as stream:
            try:
                # Read the file as a raw string
                raw_content = stream.read()
                
                # Render the content as a Jinja2 template
                template = Template(raw_content)
                rendered_content = template.render(spawner=spawner)
                
                # Parse the rendered content as YAML
                config_data = yaml.safe_load(rendered_content)
    
            except yaml.YAMLError as exc:
                print(f"YAML Error: {exc}")
            except Exception as e:
                print(f"Error: {e}")

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