from os import environ

import yaml


class YamlParser:
    def __init__(self, _config):
        self._config = _config

    def get(self, path: str):
        if path == "":
            return self._config

        keys = path.split(".")
        _config = self._config
        for key in keys:
            _config = _config.get(key, {})

        if _config is None:
            raise KeyError(f"Key '{path}' not found")

        return _config

    def get_by_key(self, key, default=None):
        _config = self._config.get(key, default)
        return YamlParser(_config) if isinstance(_config, dict) else _config


try:
    env_name = environ.get("API_ENV", "")

    if env_name == "":
        conf_file_name = "./env/config.yaml"
    else:
        conf_file_name = f"./env/config.{env_name}.yaml"

    with open(conf_file_name) as file:
        config_dict = yaml.load(file, Loader=yaml.FullLoader)

        if len(config_dict.get("include", {}).get("optional", [])) > 0:
            for include_file in config_dict.get("include", {}).get("optional", []):
                try:
                    with open(f"./env/{include_file}") as include:
                        config_dict.update(yaml.load(include, Loader=yaml.FullLoader))
                except FileNotFoundError:
                    ...
except FileNotFoundError as e:
    raise FileNotFoundError("Please check config file by environment") from e

config = YamlParser(config_dict)
