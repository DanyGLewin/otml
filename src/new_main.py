import os

from src.grammar.constraint_set import ConstraintSet
from src.grammar.feature_table import FeatureTable
from src.grammar.grammar import Grammar
from src.grammar.lexicon import Lexicon
from src.models.corpus import Corpus
from src.models.traversable_grammar_hypothesis import TraversableGrammarHypothesis
from src.otml_configuration import OtmlConfiguration, settings
from src.simulated_annealing import SimulatedAnnealing

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
