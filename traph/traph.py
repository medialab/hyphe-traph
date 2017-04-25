# =============================================================================
# Traph Class
# =============================================================================
#
# Main class representing the Traph data structure.
#
from walk_history import WalkHistory
from file_storage import FileStorage
from memory_storage import MemoryStorage
from lru_trie import LRUTrie
from lru_trie_walk_history import LRUTrieWalkHistory
from lru_trie_node import LRU_TRIE_NODE_BLOCK_SIZE
from link_store import LinkStore
from link_store_node import LINK_STORE_NODE_BLOCK_SIZE


class Traph(object):

    # =========================================================================
    # Constructor
    # =========================================================================
    def __init__(self, lru_trie_file=None, link_store_file=None):

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

    # =========================================================================
    # Public interface
    # =========================================================================
    def add_page(self, lru):
        node, history = self.lru_trie.add_page(lru)

        # Here we need to deal with webentity creation rules
        rule = history.rule_to_apply()

        # Either we apply the default rule
        if rule == LRUTrieWalkHistory.APPLY_DEFAULT_RULE:
            pass

        # Either we attempt to apply the matched creation rule
        if rule != LRUTrieWalkHistory.SKIP_RULE:

            # If we fail to match the pattern of the creation rule,
            # we fallback on the default one
            pass
