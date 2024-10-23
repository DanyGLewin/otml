import csv
import json
import logging
from copy import deepcopy
from random import choice

from pydantic import BaseModel, model_validator
from six import string_types, integer_types, StringIO, iterkeys

from source.errors import FeatureParseError
from source.grammar.base_segment import BaseSegment
from source.otml_configuration import settings
from source.unicode_mixin import UnicodeMixin

logger = logging.getLogger(__name__)


class Feature(BaseModel):
    label: str
    values: list[str]

    def __repr__(self):
        return f"{self.label}: {self.values}"


class FeatureList(BaseModel):
    features: list[Feature]

    @property
    def labels(self):
        return {f.label for f in self.features}

    def __getitem__(self, key: int | str):
        if type(key) == str:
            if key in self.labels:
                return [f.values for f in self.features if f.label == key][0]
            else:
                raise KeyError(key)
        if type(key) == int:
            return self.features[key]

    def __len__(self):
        return len(self.features)

    def __iter__(self):
        return iter(self.features)

    def __contains__(self, key: str | Feature):
        if type(key) == str:
            return key in self.labels
        return key in self.features

    @model_validator(mode="after")
    def _validate_distinct(self):
        for label in self.labels:
            features = [f for f in self.features if f.label == label]
            if len(features) > 1:
                raise FeatureParseError("Feature was defined more than once", {"label": label, "definitions": features})
        return self


class FeatureTable(UnicodeMixin, object):
    def __init__(self, segments: list[BaseSegment]):
        self.feature_table_dict = dict()
        self.features_list = FeatureList.model_validate(dict(features=segments["feature"]))
        self.segments_list = list()

        self.feature_order_dict = dict()
        for i, feature in enumerate(self.features_list):
            self.feature_order_dict[i] = feature

        for symbol in segments["feature_table"].keys():
            feature_values = segments["feature_table"][symbol]
            if len(feature_values) != len(self.features_list):
                raise FeatureParseError("Mismatch in number of features for segment {0}".format(symbol))
            symbol_feature_dict = dict()
            for i, feature_value in enumerate(feature_values):
                feature = self.features_list[i]
                if not feature_value in feature.values:
                    raise FeatureParseError("Illegal feature was found for segment {0}".format(symbol))
                symbol_feature_dict[feature.label] = feature_value
            self.feature_table_dict[symbol] = symbol_feature_dict

        for symbol in self.get_alphabet():
            self.segments_list.append(Segment_(symbol, self))

    @classmethod
    def loads(cls, feature_table_str):
        feature_table_dict = json.loads(feature_table_str)
        return cls(feature_table_dict)

    @classmethod
    def load(cls):
        with open(settings.features_file, "r") as f:
            reader = csv.DictReader(f)
            segments_list = [settings.Segment.model_validate(row) for row in reader]

        return cls(segments_list)


    def get_number_of_features(self):
        return len(self.features_list)

    def get_features(self):
        return self.features_list.labels

    def get_random_value(self, feature):
        return choice(self.features_list[feature])

    def get_alphabet(self):
        return list(iterkeys(self.feature_table_dict))

    def get_segments(self):
        return deepcopy(self.segments_list)

    def get_random_segment(self):
        return choice(self.get_alphabet())

    def get_ordered_feature_vector(self, char):
        return [self[char][self.feature_order_dict[i]] for i in range(self.get_number_of_features())]

    def is_valid_feature(self, feature_label):
        return feature_label in self.features_list

    def is_valid_symbol(self, symbol):
        return symbol in self.feature_table_dict

    def __unicode__(self):
        values_str_io = StringIO()
        print(
            "Feature Table with {0} features and {1} segments:".format(
                self.get_number_of_features(), len(self.get_alphabet())
            ),
            end="\n",
            file=values_str_io,
        )

        print("{:20s}".format("Segment/Feature"), end="", file=values_str_io)
        for i in list(range(len(self.feature_order_dict))):
            print("{:10s}".format(self.feature_order_dict[i]), end="", file=values_str_io)
        print("", file=values_str_io)  # new line
        for segment in sorted(iterkeys(self.feature_table_dict)):
            print("{:20s}".format(segment), end="", file=values_str_io)
            for i in list(range(len(self.feature_order_dict))):
                feature = self.feature_order_dict[i]
                print("{:10s}".format(self.feature_table_dict[segment][feature]), end="", file=values_str_io)
            print("", file=values_str_io)

        return values_str_io.getvalue()

    def __getitem__(self, item):
        if isinstance(item, string_types):
            return self.feature_table_dict[item]
        if isinstance(item, integer_types):  # TODO this should support an ordered access to the feature table.
            #  is this a good implementation?
            return self.feature_table_dict[self.feature_order_dict[item]]
        else:
            segment, feature = item
            return self.feature_table_dict[segment][feature]


class Segment_(UnicodeMixin, object):
    def __init__(self, symbol, feature_table=None):
        self.symbol = symbol  # JOKER and NULL segments need feature_table=None
        if feature_table:
            self.feature_table = feature_table
            self.feature_dict = feature_table[symbol]

        self.hash = hash(self.symbol)

    def get_encoding_length(self):
        return len(self.feature_dict)

    def has_feature_bundle(self, feature_bundle):
        return all(item in self.feature_dict.items() for item in feature_bundle.get_feature_dict().items())

    def get_symbol(self):
        return self.symbol

    @staticmethod
    def intersect(x, y):
        """Intersect two segments, a segment and a set, or two sets.

        :type x: Segment_ or set
        :type y: Segment_ or set
        """
        if isinstance(x, set):
            x, y = y, x  # if x is a set then maybe y is a segment, switch between them so that
            # Segment.__and__ will take affect
        return x & y

    def __and__(self, other):
        """Based on ```(17) symbol unification```(Riggle, 2004)

        :type other: Segment_ or set
        """
        if self == JOKER_SEGMENT:
            return other
        elif isinstance(other, set):
            if self.symbol in other:
                return self
        else:
            if self == other:
                return self
            elif other == JOKER_SEGMENT:
                return self
        return None

    def __eq__(self, other):
        if other is None:
            return False
        return self.symbol == other.symbol

    def __hash__(self):
        return self.hash

    def __unicode__(self):
        if hasattr(self, "feature_table"):
            values_str_io = StringIO()
            ordered_feature_vector = self.feature_table.get_ordered_feature_vector(self.symbol)

            for value in ordered_feature_vector:
                print(value, end=", ", file=values_str_io)
            return "Segment {0}[{1}]".format(self.symbol, values_str_io.getvalue()[:-2])
        else:
            return self.symbol

    def __getitem__(self, item):
        return self.feature_dict[item]


# ----------------------
# Special segments - required for transducer construction
NULL_SEGMENT = Segment_("-")
JOKER_SEGMENT = Segment_("*")


# ----------------------


class FeatureType(UnicodeMixin, object):
    def __init__(self, label, values):
        self.label = label
        self.values = values

    def get_random_value(self):
        return choice(self.values)

    def __unicode__(self):
        values_str_io = StringIO()
        for value in self.values:
            print(value, end=", ", file=values_str_io)
        return "FeatureType {0} with possible values: [{1}]".format(self.label, values_str_io.getvalue()[:-2])

    def __contains__(self, item):
        return item in self.values
