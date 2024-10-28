"""
This is the entry point of the otml project
The working directory for activating this file should be "otml"
"""

import os
import platform
from base64 import urlsafe_b64encode
from uuid import uuid4

import click

from src.grammar.constraint_set import ConstraintSet
from src.grammar.feature_table import FeatureTable
from src.grammar.grammar import Grammar
from src.grammar.lexicon import Lexicon
from src.misc.logger import setup_logger
from src.models.corpus import Corpus
from src.models.traversable_grammar_hypothesis import TraversableGrammarHypothesis
from src.otml_configuration import OtmlConfiguration, settings
from src.simulated_annealing import SimulatedAnnealing



@click.command()
@click.option(
    "-c", "--configuration", "config_folder_path", required=True, help="Relative path to the configuration folder"
)
@click.option("-v", "--verbose", "verbose", is_flag=True, default=False, help="Set log level to info")
@click.option("-vv", "--very-verbose", "very_verbose", is_flag=True, default=False, help="Set log level to debug")
def main(config_folder_path, verbose, very_verbose):
    # load configurations
    OtmlConfiguration.load(config_folder_path)
    setup_logger(verbose, very_verbose)

    # load grammar and data
    feature_table = FeatureTable.load(settings.features_file)
    corpus = Corpus.load(settings.corpus_file)
    constraint_set = ConstraintSet.load(settings.constraints_file, feature_table)
    lexicon = Lexicon(corpus.get_words(), feature_table)
    grammar = Grammar(feature_table, constraint_set, lexicon)
    data = corpus.get_words()

    # prepare data for optimization
    traversable_hypothesis = TraversableGrammarHypothesis(grammar, data)
    simulated_annealing = SimulatedAnnealing(traversable_hypothesis)

    # run simulated annealing
    print("Starting optimization")
    simulated_annealing.run()
    print("Done")


def get_log_name():
    short_random_identifier = urlsafe_b64encode(uuid4().bytes)[:4].decode("utf-8")  # length 4 of base64
    # is more than 16M possibilities
    log_name = "_".join()


def create_simulation_directory(simulation_name, sub_name):
    computer_name = platform.node()
    # logging


if __name__ == "__main__":
    main()
    # get_log_name()
