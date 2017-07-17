# =============================================================================
# Webentity Creation Rule Store
# =============================================================================
#
# Class storing reading & writing a set of webentity creation rules to a JSON
# format to mock data that would be provided by Hyphe's core.
#
import json


class WebEntityCreationRuleStore(object):

    def __init__(self, path):

        # Properties
        self.path = path
        self.data = {}

        # Initializing
        self.read()

    def read(self):
        try:
            with open(self.path, 'r') as f:
                self.data = json.load(f)
        except IOError:
            self.write()

    def write(self):
        with open(self.path, 'w') as f:
            json.dump(self.data, f)
