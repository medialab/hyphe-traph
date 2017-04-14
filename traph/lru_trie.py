# =============================================================================
# LRU Trie Class
# =============================================================================
#
# Class representing the Trie indexing the LRUs.
#
from lru_trie_node import LRUTrieNode


class LRUTrie(object):

    # =========================================================================
    # Constructor
    # =========================================================================
    def __init__(self, storage):

        # Properties
        self.storage = storage

    # =========================================================================
    # Internal methods
    # =========================================================================

    # Method ensuring that a sibling with the desired char exists
    def __require_char_from_siblings(self, node, char):

        # If the node does not exist, we create it
        if not node.exists:
            node.set_char(char)
            node.write()
            return node

    # =========================================================================
    # Mutation methods
    # =========================================================================

    # Method adding a page to the trie
    # Note: passing unicode strings or raw strings will alter the structure
    def add_page(self, lru):

        node = LRUTrieNode(self.storage, block=0)

        # Iterating over the lru's characters
        for char in lru:
            char = ord(char)

            node = self.__require_char_from_siblings(node, char)
