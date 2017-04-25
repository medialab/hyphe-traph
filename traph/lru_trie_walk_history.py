# =============================================================================
# LRU Trie Walk History Class
# =============================================================================
#
# Class tracking some information about a given walk in the LRU Trie.
#


class LRUTrieWalkHistory(object):

    def __init__(self):

        # Properties
        self.webentity = None
        self.webentity_prefix = ''
        self.webentity_position = 0
        self.webentity_creation_rule = None
        self.webentity_creation_rule_position = 0

    def __repr__(self):
        class_name = self.__class__.__name__

        return (
            '<%(class_name)s we_prefix="%(prefix)s">'
        ) % {
            'class_name': class_name,
            'prefix': self.webentity_prefix
        }

    def update_webentity(weid, prefix, position):
        self.webentity = weid
        self.webentity_prefix = prefix
        self.webentity_position = position

    def update_webentity_creation_rule(wecrid, position):
        self.webentity_creation_rule = wecrid
        self.webentity_creation_rule_position = position
