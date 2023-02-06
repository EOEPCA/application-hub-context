from abc import ABC


class ApplicationHubContext(ABC):
    def __init__(self, namespace, spawner, **kwargs):

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

    def dispose(self):
        return True

    def _set_pod_env_vars(self):

        for key, value in self.env_vars.items():
            self.spawner.environment[key] = value
