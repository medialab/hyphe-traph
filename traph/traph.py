# =============================================================================
# Traph Class
# =============================================================================
#
# Main class representing the Traph data structure.
#
from walk_history import WalkHistory


class Traph(object):

    def __init__(self, storage):

        # Properties
        self.storage = storage

    # Method used to ensure a char is set within the siblings of the
    # current node
    def __require_char_from_siblings(self, block, char):

        # Reading the block
        node = self.storage.read_lru_trie_node(block)

        # If the node does not exist, just create it
        if not node:
            node = self.storage.create_lru_trie_node(char)
            self.storage.write_lru_trie_node(node)
            return node

        # Else we follow the linked list to see if we can find the
        # relevant sibling
        if node.char() == char:
            return node

        while node.hasNext():
            node = self.storage.read_lru_trie_node(node.next())

            if node.char() == char:
                return node

        # A relevant node was not found, let's append a sibling to the list
        sibling = self.storage.create_lru_trie_node(char)
        block = self.storage.write_lru_trie_node(sibling)

        # Updating the pointer of the last node
        # TODO: find a way to anticipate move to update the node before we
        # create the other one, this would be better for the cursor
        node.setNext(block)
        self.storage.write_lru_trie_node(node)

        return sibling


    # Method used to add a single page to the Traph
    def add_page(self, lru):
        walk_history = WalkHistory()

        block = 0

        for char in lru:
            char = ord(char)
            node = self.__require_char_from_siblings(block, char)

