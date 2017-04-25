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
from link_store import LinkStore
from link_store_node import LINK_STORE_NODE_BLOCK_SIZE



class Traph(object):

    # =========================================================================
    # Constructor
    # =========================================================================
    def __init__(self, lru_trie_file=None, links_store_file=None):

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
        if links_store_file:
            self.links_store_storage = FileStorage(
                LINK_STORE_NODE_BLOCK_SIZE,
                links_store_file
            )
        else:
            self.links_store_storage = MemoryStorage(LINK_STORE_NODE_BLOCK_SIZE)

    # =========================================================================
    # Public interface
    # =========================================================================
    def add_page(self, lru):
        self.lru_trie.add_page(lru)
