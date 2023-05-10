# Application-Hub


## Read the configuration

```python
config_path="/usr/local/etc/jupyterhub/config.yml"
```

## Profile list

```python
from application_hub_context.app_hub_context import DefaultApplicationHubContext

namespace_prefix = "jupyter"

def custom_options_form(spawner):

    spawner.log.info("Configure profile list")

    namespace = f"{namespace_prefix}-{spawner.user.name}"

    workspace = DefaultApplicationHubContext(
        namespace=namespace,
        spawner=spawner,
        config_path=config_path,
    )

    spawner.profile_list = workspace.get_profile_list()

    return spawner._options_form_default()
```

## Pre-spawn hook

```python
def pre_spawn_hook(spawner):

    spawner.http_timeout = 600

    profile_slug = spawner.user_options.get("profile", None)

    env = os.environ["JUPYTERHUB_ENV"].lower()

    spawner.environment["CALRISSIAN_POD_NAME"] = f"jupyter-{spawner.user.name}-{env}"

    spawner.log.info(f"Using profile slug {profile_slug}")

    namespace = f"{namespace_prefix}-{spawner.user.name}"

    workspace = DefaultApplicationHubContext(
        namespace=namespace,
        spawner=spawner,
        config_path=config_path
    )

    workspace.initialise()

    profile_id = workspace.config_parser.get_profile_by_slug(slug=profile_slug).id

    default_url = workspace.config_parser.get_profile_default_url(profile_id=profile_id)

    if default_url:
        spawner.log.info(f"Setting default url to {default_url}")
        spawner.default_url = default_url
```

## Post-stop hook

```python
def post_stop_hook(spawner):

    namespace = f"jupyter-{spawner.user.name}"

    workspace = DefaultApplicationHubContext(
        namespace=namespace,
        spawner=spawner,
        config_path=config_path
    )
    spawner.log.info("Dispose in post stop hook")
    workspace.dispose()
```
