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

    def tearDown(self):
        shutil.rmtree(self.folder)
