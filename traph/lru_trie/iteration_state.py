# =============================================================================
# LRU Trie Iteration State Classes
# =============================================================================
#
# Gathering classes representing some complex iterations' state.
#


# The iteration state of a detailed DFS
class LRUTrieDetailedDFSIterationState(object):

    def __init__(self, node, lru=''):

        # Properties
        self.node = node
        self.last_block = None
        self.direction = 'down'
        self.lru = lru
        self.webentities = []

    def __repr__(self):
        class_name = self.__class__.__name__

        return (
            '<%(class_name)s level=%(level)s block=%(block)s'
            ' last_block=%(last_block)s lru="%(lru)s" direction=%(direction)s'
            ' webentities=%(webentities)s>'
        ) % {
            'class_name': class_name,
            'level': self.level(),
            'block': self.node.block,
            'last_block': self.last_block,
            'lru': self.lru,
            'direction': self.direction,
            'webentities': '/'.join(map(str, self.webentities)) if len(self.webentities) else None
        }

    def current_webentity(self):
        if len(self.webentities):
            return self.webentities[-1]

        return

    def level(self):
        return len(self.lru) - 1
