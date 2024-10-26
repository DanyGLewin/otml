import os

from corpus import Corpus
from grammar.constraint_set import ConstraintSet
from grammar.feature_table import FeatureTable
from grammar.grammar import Grammar
from grammar.lexicon import Lexicon
from simulated_annealing import SimulatedAnnealing
from src.otml_configuration import OtmlConfiguration, settings
from traversable_grammar_hypothesis import TraversableGrammarHypothesis

CURRENT_PATH = os.path.split(os.path.abspath(__file__))[0]
FIXTURES_PATH = os.path.join(CURRENT_PATH, "tests/fixtures")
SIMULATION_NAME = "french_deletion"

configuration_folder = f"{FIXTURES_PATH}/{SIMULATION_NAME}"

OtmlConfiguration.load(configuration_folder)

feature_table = FeatureTable.load(settings.features_file)
corpus = Corpus.load(settings.corpus_file)
constraint_set = ConstraintSet.load(settings.constraints_file, feature_table)
lexicon = Lexicon(corpus.get_words(), feature_table)
grammar = Grammar(feature_table, constraint_set, lexicon)
data = corpus.get_words()
traversable_hypothesis = TraversableGrammarHypothesis(grammar, data)
simulated_annealing = SimulatedAnnealing(traversable_hypothesis)
simulated_annealing.run()

print("🥳️")
