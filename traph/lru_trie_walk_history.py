# =============================================================================
# LRU Trie Walk History Class
# =============================================================================
#
# Class tracking some information about a given walk in the LRU Trie.
#


# Main class
class LRUTrieWalkHistory(object):

    APPLY_DEFAULT_RULE = 'APPLY_DEFAULT_RULE'
    SKIP_RULE = 'SKIP_RULE'

    def __init__(self):

        # Properties
        self.webentity = None
        self.webentity_prefix = ''
        self.webentity_position = -1
        self.webentity_creation_rule = None
        self.webentity_creation_rule_position = -1
        self.page_was_created = False

    def __repr__(self):
        class_name = self.__class__.__name__

        return (
            '<%(class_name)s prefix="%(prefix)s"'
            ' weid=%(weid)s wecrid=%(wecrid)s>'
        ) % {
            'class_name': class_name,
            'prefix': self.webentity_prefix,
            'weid': self.webentity,
            'wecrid': self.webentity_creation_rule
        }

    def update_webentity(weid, prefix, position):
        self.webentity = weid
        self.webentity_prefix = prefix
        self.webentity_position = position

    def update_webentity_creation_rule(wecrid, position):
        self.webentity_creation_rule = wecrid
        self.webentity_creation_rule_position = position

    def rule_to_apply(self):
        if self.webentity_creation_rule_position >= 0 and \
           self.webentity_creation_rule_position >= self.webentity_position:

            # Note that it remains to the user to apply default rule if
            # the given rule would happen to fail
            return self.webentity_creation_rule

        elif self.webentity is None:
            return self.APPLY_DEFAULT_RULE

        return self.SKIP_RULE
