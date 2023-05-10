from application_hub_context.parser import ConfigParser

ws_config_parser = ConfigParser.read_file(
    config_path="jupyterhub/files/hub/config.yml", user_groups=["group-2"]
)

print(ws_config_parser.get_profile_by_slug(slug="ellip_studio_labs").dict())

print(ws_config_parser.get_profile_config_maps(profile_id="profile_studio_labs"))
