from __future__ import absolute_import, division, print_function, unicode_literals

import os
import codecs

from source.otml_configuration import OtmlConfiguration, settings

dirname, filename = os.path.split(os.path.abspath(__file__))

json_str = codecs.open(os.path.join(dirname, "fixtures/configuration/otml_configuration.json"), 'r').read()
otml_configuration_manager = OtmlConfigurationManager(json_str)

configurations: OtmlConfiguration = settings