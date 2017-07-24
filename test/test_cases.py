# =============================================================================
# Traph Test Case
# =============================================================================
#
# A special test case embarking fixtures ensuring everything runs cleanly.
#
from os import path
import unittest
import shutil
from traph import Traph
from test.config import DEFAULT_WEBENTITY_CREATION_RULE, WEBENTITY_CREATION_RULES

FOLDER = path.join(path.realpath(path.dirname(__file__)), 'temp')


class TraphTransaction(object):
    def __init__(self, traph):
        self.traph = traph

    def __enter__(self):
        return self.traph

    def __exit__(self, type, value, traceback):
        self.traph.close()


class TraphTestCase(unittest.TestCase):

    folder = FOLDER

    def get_traph(self, **kwargs):
        options = {
            'overwrite': False,
            'default_webentity_creation_rule': DEFAULT_WEBENTITY_CREATION_RULE,
            'webentity_creation_rules': WEBENTITY_CREATION_RULES,
            'folder': self.folder
        }

        options.update(kwargs)

        return Traph(**options)

    def traph_transaction(self, **kwargs):
        traph = self.get_traph(**kwargs)

        return TraphTransaction(traph)

    def tearDown(self):
        shutil.rmtree(self.folder, ignore_errors=True)
