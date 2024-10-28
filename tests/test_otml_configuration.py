import os
import unittest

from src.exceptions import OtmlConfigurationError
from src.otml_configuration import OtmlConfiguration, ConstraintInsertionWeights


class TestOtmlConfigurationManager(unittest.TestCase):
    def setUp(self):
        dirname, filename = os.path.split(os.path.abspath(__file__))

        config_path = os.path.join(dirname, "fixtures/french_deletion")
        self.config = OtmlConfiguration.load(config_path)

    def test_loading_given_inf_string_should_convert_to_infinity(self):
        self.assertEqual(self.config.max_features_in_bundle, float("inf"))

    def test_loading_given_exponents_should_calculate_value(self):
        self.assertEqual(self.config.threshold, 10 ** -2)

    def test_update_should_update_config_values(self):
        self.config.update(min_constraints_in_constraint_set=2)
        self.assertEqual(self.config.min_constraints_in_constraint_set, 2)

    def test_reset_should_reset_config_values(self):
        self.config.update(min_constraints_in_constraint_set=2)
        self.config.reset()
        self.assertEqual(self.config.min_constraints_in_constraint_set, 1)

    def test_insertion_weights_given_sum_zero_should_raise_error(self):
        with self.assertRaises(OtmlConfigurationError):
            self.config.constraint_insertion_weights = ConstraintInsertionWeights(
                dep=0,
                max=0,
                ident=0,
                phonotactic=0,
            )

    def tearDown(self):
        self.config.reset()
