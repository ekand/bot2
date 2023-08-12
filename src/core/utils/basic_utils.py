import os
from configparser import ConfigParser
from pathlib import Path


def get_general_settings():
    return dict(load_config()["general"])


def get_feature_flags():
    return dict(load_config()["feature_flags"])


def get_dev_config():
    return dict(load_config()["dev"])


def load_config():
    """Returns a config object with the config settings values available"""
    this_file_path = os.path.dirname(__file__)
    repo_root_dir_path = str(Path(this_file_path).resolve().parents[2])
    config = ConfigParser()
    config_file_name = "config.ini"
    config_file_path = os.sep.join([repo_root_dir_path, config_file_name])
    config.read(config_file_path)
    return config


if __name__ == "__main__":
    print(feature_flags_dict)
