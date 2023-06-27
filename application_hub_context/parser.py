import yaml

from application_hub_context.models import Config

undefined = object()


class ConfigParser:
    def __init__(self, config_data, user_groups):
        """returns a config parser"""
        self.config = Config(**config_data)
        self.user_groups = user_groups

    @classmethod
    def read_file(cls, config_path, user_groups):
        """reads a config file encoded in YAML"""
        with open(config_path, "r") as stream:
            try:
                config_data = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

        return cls(config_data=config_data, user_groups=user_groups)

    def get_profiles(self):
        """lists the profiles"""
        profiles = []
        for profile in self.config.profiles:
            if bool(set(profile.groups) & set(self.user_groups)):
                profiles.append(profile.definition.dict())

        return profiles
        # return [
        #     profile.definition
        #     for profile in self.config.profiles
        #     if bool(set(profile.groups) & set(self.user_groups))
        # ]

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
