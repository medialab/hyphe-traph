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


# A class defining some custom assertions
class CustomAssertionsTestCase(unittest.TestCase):

    def assertIdenticalMultimaps(self, map1, map2):
        if len(map1) != len(map2):
            raise AssertionError('Maps have different lengths.')

        for source, targets1 in map1.items():
            if source not in map2:
                raise AssertionError('The %s key does not exist in the second map.' % source)

            targets2 = map2[source]

            if len(targets1) != len(targets2):
                raise AssertionError('The values for %s are not the same number.' % source)

            if set(targets1) != set(targets2):
                raise AssertionError('The values for %s are not identical.' % source)


# Class representing a Traph transaction to ease simple unit tests
class TraphTransaction(object):
    def __init__(self, traph):
        self.traph = traph

    def __enter__(self):
        return self.traph

    def __exit__(self, type, value, traceback):
        self.traph.close()


# A test case able to open and tear down a Traph when running tests
class TraphTestCase(CustomAssertionsTestCase):

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

    def open_traph(self, **kwargs):
        traph = self.get_traph(**kwargs)

        return TraphTransaction(traph)

    def tearDown(self):
        shutil.rmtree(self.folder, ignore_errors=True)
