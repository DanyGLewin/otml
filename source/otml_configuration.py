import json
from io import StringIO
from typing import Any, Literal, Optional, Self

from pydantic import BaseModel, field_validator, create_model, model_validator, ConfigDict, NonNegativeInt
from pydantic_core import from_json

from source.errors import OtmlConfigurationError
from source.singelton import Singleton

INF = Literal[float("inf")]


class Model(BaseModel):
    model_config = ConfigDict(
        extra="forbid",  # disallow extra fields
        validate_assignment=True,  # run validations after every value assignment
    )

    def dict(self, *args, **kwargs) -> dict[str, Any]:
        return self.model_dump(*args, **kwargs)

    def items(self):
        return self.dict().items()

    def keys(self):
        return self.dict().keys()

    def values(self):
        return self.dict().values()

    def __repr__(self):
        buffer = StringIO()
        name = self.__class__.__name__
        buffer.write(f"{name}:\n")
        for key, val in self.items():
            buffer.write(f"\t{key}: {val}\n")
        return buffer.getvalue()


class Weights(Model):
    @property
    def sum(self) -> int:
        return sum(self.values())

    @field_validator("*")
    @classmethod
    def parse_int(cls, value):
        if type(value) == int:
            return value
        return int(value)


class LexiconMutationWeights(Weights):
    insert_segment: NonNegativeInt
    delete_segment: NonNegativeInt
    change_segment: NonNegativeInt


class ConstraintSetMutationWeights(Weights):
    insert_constraint: NonNegativeInt
    remove_constraint: NonNegativeInt
    demote_constraint: NonNegativeInt
    insert_feature_bundle_phonotactic_constraint: NonNegativeInt
    remove_feature_bundle_phonotactic_constraint: NonNegativeInt
    augment_feature_bundle: NonNegativeInt


class ConstraintInsertionWeights(Weights):
    dep: NonNegativeInt
    max: NonNegativeInt
    ident: NonNegativeInt
    phonotactic: NonNegativeInt


class OtmlConfiguration(Model, Singleton):
    source_file: str
    simulation_name: str

    constraint_set_file_name: str
    feature_table_file_name: str
    corpus_file_name: str

    log_file_name: str
    log_lexicon_words: bool

    corpus_duplication_factor: int

    allow_candidates_with_changed_segments: bool

    restriction_on_alphabet: bool

    max_constraints_in_constraint_set: float | int
    min_constraints_in_constraint_set: int
    max_feature_bundles_in_phonotactic_constraint: int
    min_feature_bundles_in_phonotactic_constraint: int
    max_features_in_bundle: float | int
    initial_number_of_features: int
    initial_number_of_bundles_in_phonotactic_constraint: int
    random_position_for_feature_bundle_insertion_in_phonotactic: bool
    random_position_for_feature_bundle_removal_in_phonotactic: bool

    lexicon_mutation_weights: LexiconMutationWeights
    constraint_set_mutation_weights: ConstraintSetMutationWeights
    constraint_insertion_weights: ConstraintInsertionWeights

    initial_temp: int
    threshold: float
    cooling_factor: float
    debug_logging_interval: int
    clear_modules_caching_interval: int
    steps_limitation: int | float

    random_seed: bool
    seed: int

    data_encoding_length_multiplier: int
    grammar_encoding_length_multiplier: int

    @field_validator("*", mode="before")
    @classmethod
    def _parse_json_field(cls, raw):
        if type(raw) != str:
            return raw
        try:
            if raw.casefold() == "inf":
                return float("inf")
            if "**" in raw:
                x, y = raw.split("**")
                return float(x) ** int(y)
        except ValueError:
            raise OtmlConfigurationError(f"Invalid integer value", {"value": raw})
        return raw

    @classmethod
    def from_json(cls, file_path: str) -> Self:
        with open(file_path, "r") as f:
            raw = json.load(f)

        raw["source_file"] = file_path
        obj = cls.model_validate(raw)
        return obj

    def reset(self) -> Self:
        """
        returns a copy of the configuration's original state
        """
        return from_json(self.source_file)

    def update(self, **updates) -> Self:
        """
        returns a copy of the configuration, updating the values per the given kwargs
        """
        return self.model_copy(update=updates, deep=True)

    @model_validator(mode="after")
    def _validate_weights(self):
        if self.lexicon_mutation_weights.sum + self.constraint_set_mutation_weights.sum == 0:
            raise OtmlConfigurationError("Sum of mutation weights is zero")

        if self.constraint_insertion_weights.sum == 0:
            raise OtmlConfigurationError("Sum of insertion weights is zero")
        return self

    @model_validator(mode="after")
    def _validate_not_implemented_features(self):
        for value in (
            self.constraint_set_mutation_weights.augment_feature_bundle,
            self.lexicon_mutation_weights.change_segment,
            self.allow_candidates_with_changed_segments,
        ):
            if value:
                raise NotImplementedError
        return self

    @model_validator(mode="after")
    def _validate_feature_number(self):
        if self.min_feature_bundles_in_phonotactic_constraint > self.initial_number_of_features:
            raise OtmlConfigurationError(
                "MIN_FEATURE_BUNDLES_IN_PHONOTACTIC_CONSTRAINT is bigger then INITIAL_NUMBER_OF_FEATURES",
            )
        return self

    @model_validator(mode="after")
    def _validate_change_segment_has_logical_weight(self):  # the logic for these isn't actually implemented yet
        if self.lexicon_mutation_weights.change_segment ^ self.allow_candidates_with_changed_segments:
            raise OtmlConfigurationError(
                "Either neither or both of `lexicon_mutation_weights.change_segment` and `allow_candidates_with_changed_segments` must be positive",
            )
        return self