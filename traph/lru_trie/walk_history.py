# =============================================================================
# LRU Trie Walk History Class
# =============================================================================
#
# Class tracking some information about a given walk in the LRU Trie.
#


# Class representing the history of a simple walk into the Trie
class LRUTrieWalkHistory(object):

    def __init__(self, lru):

        # Properties

        # TODO: this should become a list
        self.lru = lru
        self.webentity = None
        self.webentity_prefix = ''
        self.webentity_position = -1
        self.webentity_creation_rules = []
        self.page_was_created = False

    def __repr__(self):
        class_name = self.__class__.__name__

        return (
            '<%(class_name)s prefix="%(prefix)s"'
            ' weid=%(weid)s position=%(position)s wecr=%(wecr)s>'
        ) % {
            'class_name': class_name,
            'prefix': self.webentity_prefix,
            'weid': self.webentity,
            'position': self.webentity_position,
            'wecr': '/'.join(str(wecr) for wecr in self.webentity_creation_rules) if self.webentity_creation_rules else None
        }

    def update_webentity(self, weid, prefix, position):
        self.webentity = weid
        self.webentity_prefix = prefix
        self.webentity_position = position

    def add_webentity_creation_rule(self, position):
        self.webentity_creation_rules.append(position)

    def rules_to_apply(self):
        for position in reversed(self.webentity_creation_rules):
            if position >= 0:

                prefix = self.lru[0:position]

                # Note that it remains to the user to apply default rule if
                # none of the given rules would happen to succeed
                yield prefix
