from __future__ import absolute_import, division, print_function, unicode_literals

import pickle
import unittest

from src.grammar.constraint import MaxConstraint, PhonotacticConstraint
from src.grammar.constraint_set import ConstraintSet
from src.grammar.feature_table import FeatureTable
from src.grammar.grammar import Grammar
from src.grammar.lexicon import Lexicon
from src.grammar.lexicon import Word
from src.misc.debug_tools import timeit
from src.models.corpus import Corpus
from tests.otml_configuration_for_testing import configurations
from tests.persistence_tools import get_constraint_set_fixture, get_feature_table_fixture, get_corpus_fixture


class TestObjectCaching(unittest.TestCase):

    def setUp(self):
        self.feature_table = FeatureTable.load(get_feature_table_fixture("a_b_and_son_feature_table.json"))
        self.constraint_set_filename = get_constraint_set_fixture("no_bb_Max_Dep_constraint_set.json")
        self.corpus = Corpus.load(get_corpus_fixture("small_ab_corpus.txt"))
        self.word = Word("abababa", self.feature_table)
        self.constraint = PhonotacticConstraint([{'son': '+'}, {'son': '+'}], self.feature_table)
        self.constraint_set = ConstraintSet.load(self.constraint_set_filename, self.feature_table)
        self.lexicon = Lexicon(self.corpus.get_words(), self.feature_table)
        self.grammar = Grammar(self.feature_table, self.constraint_set, self.lexicon)

    def test_constraint_transducer_caching(self):
        max_constraint = MaxConstraint([{'son': '+'}], self.feature_table)
        # deepcopy(max_constraint)
        orig_transducer = max_constraint.get_transducer()
        max_constraint.augment_feature_bundle()
        new_transducer = max_constraint.get_transducer()
        self.assertEqual(id(orig_transducer), id(new_transducer))

    # def test_word_caching(self):
    #    get_transducer(self.word)
    #    get_transducer(self.word)
    #    get_transducer(self.word)
    #
    # def test_constraint_caching(self):
    #    get_transducer(self.constraint)
    #    get_transducer(self.constraint)
    #    get_transducer(self.constraint)
    #
    #
    # def test_constraint_set_caching(self):
    #    get_transducer(self.constraint_set)
    #    get_transducer(self.constraint_set)
    #    get_transducer(self.constraint_set)
    #
    # def test_grammar_caching(self):
    #    get_transducer(self.grammar)
    #    get_transducer(self.grammar)
    #    get_transducer(self.grammar)

    def test_generate_caching(self):
        word = Word("bbb", self.feature_table)
        word_outputs = self.grammar.generate(word)
        from src.grammar.grammar import outputs_by_constraint_set_and_word

        constraint_set_and_word_key = str(self.grammar.constraint_set) + str(word)

        self.assertEqual(set(outputs_by_constraint_set_and_word[constraint_set_and_word_key]),
                         set(word_outputs))

    def test_parse_data_caching(self):
        pass

    def test_start_from_middle(self):
        print()
        print(pickle.dumps(configurations))


@timeit
def get_transducer(o):
    return o.get_transducer()
