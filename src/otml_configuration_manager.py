# Python2 and Python 3 compatibility:
from __future__ import absolute_import, division, print_function, unicode_literals

from copy import deepcopy

from configuration_manager import ConfigurationManager
from src.otml_configuration import OtmlConfiguration
from unicode_mixin import UnicodeMixin


class OtmlConfigurationManager(ConfigurationManager, UnicodeMixin):
    configurations: OtmlConfiguration

    def __init__(self, config_path):
        ConfigurationManager.__init__(
            self,
            config_type=OtmlConfiguration,
            config_loader=OtmlConfiguration.from_json,
            config_path=config_path,
        )
        self.initial_configurations = deepcopy(self.configurations)

    def __unicode__(self):
        return repr(self.configurations)
