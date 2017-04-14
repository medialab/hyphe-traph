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
from lru_trie_node import LRU_TRIE_NODE_BLOCK_SIZE


class Traph(object):

    # =========================================================================
    # Constructor
    # =========================================================================
    def __init__(self, lru_trie_file=None, links_file=None):

        # Properties
        if lru_trie_file:
            self.lru_trie_storage = FileStorage(
                LRU_TRIE_NODE_BLOCK_SIZE,
                lru_trie_file
            )
        else:
            self.lru_trie_storage = MemoryStorage(LRU_TRIE_NODE_BLOCK_SIZE)

        self.lru_trie = LRUTrie(self.lru_trie_storage)

    # =========================================================================
    # Internal methods
    # =========================================================================

    # =========================================================================
    # Public interface
    # =========================================================================
    def add_page(self, lru):
        self.lru_trie.add_page(lru)
