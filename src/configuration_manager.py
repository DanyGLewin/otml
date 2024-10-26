import json

from six import with_metaclass, PY3

from singelton import Singleton
from src.errors import ConfigurationManagerError

if PY3:
    UNICODE_TYPE = str
else:
    UNICODE_TYPE = unicode


class ConfigurationManager(with_metaclass(Singleton)):
    def __init__(self, config_type, config_loader, config_path):
        self.config_loader = config_loader  # see OtmlConfiguration.from_json
        self.configurations = config_loader(config_path)

        self.validate_configurations()
        self.derive_configurations()

    def update_configurations(self, other_json):
        other = json.loads(other_json)
        return self.configurations.update(other)

    def validate_configurations(self):
        pass

    def derive_configurations(self):
        pass

    @classmethod
    def get_config(cls):
        return cls.get_instance().configurations

    def __getitem__(self, key):
        if key in self.configurations.keys():
            return getattr(self.configurations, key)
        else:
            raise ConfigurationManagerError("Key not found", {"key": key})

    def __setitem__(self, key, value):
        if key in self.configurations.keys():
            setattr(self.configurations, key, value)
        else:
            raise ConfigurationManagerError("Key not found", {"key": key})
