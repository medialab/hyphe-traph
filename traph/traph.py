# =============================================================================
# Traph Class
# =============================================================================
#
# Main class representing the Traph data structure.
#
from traph_batch import TraphBatch
from file_storage import FileStorage
from memory_storage import MemoryStorage
from lru_trie import LRUTrie
from lru_trie_walk_history import LRUTrieWalkHistory
from lru_trie_node import LRU_TRIE_NODE_BLOCK_SIZE
from link_store import LinkStore
from link_store_node import LINK_STORE_NODE_BLOCK_SIZE


# Main class
class Traph(object):

    # =========================================================================
    # Constructor
    # =========================================================================
    def __init__(self, lru_trie_file=None, link_store_file=None,
                 webentity_default_creation_rule=None,
                 webentity_creation_rules=None):

        # Web entity creation rules are stored in RAM
        self.webentity_default_creation_rule = webentity_default_creation_rule
        self.webentity_creation_rules = webentity_creation_rules

        # LRU Trie initialization
        if lru_trie_file:
            self.lru_trie_storage = FileStorage(
                LRU_TRIE_NODE_BLOCK_SIZE,
                lru_trie_file
            )
        else:
            self.lru_trie_storage = MemoryStorage(LRU_TRIE_NODE_BLOCK_SIZE)

        self.lru_trie = LRUTrie(self.lru_trie_storage)

        # Link Store initialization
        if link_store_file:
            self.links_store_storage = FileStorage(
                LINK_STORE_NODE_BLOCK_SIZE,
                link_store_file
            )
        else:
            self.links_store_storage = MemoryStorage(
                LINK_STORE_NODE_BLOCK_SIZE)

        self.link_store = LinkStore(self.links_store_storage)

    def __apply_webentity_creation_rule(self, prefix, lru):
        pass  # TODO

    def __apply_webentity_default_creation_rule(self, lru):
        pass  # TODO

    # =========================================================================
    # Public interface
    # =========================================================================
    def batch(self):
        return TraphBatch(self)

    def add_page(self, lru):
        node, history = self.lru_trie.add_page(lru)

        # Here we need to deal with webentity creation rules
        for prefix in history.rules_to_apply():
            regexp = self.webentity_creation_rules[prefix]
            self.__apply_webentity_creation_rule(prefix, lru)
            return node

        self.__apply_webentity_default_creation_rule(lru)
        return node
