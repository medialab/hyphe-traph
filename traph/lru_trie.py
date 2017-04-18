# =============================================================================
# LRU Trie Class
# =============================================================================
#
# Class representing the Trie indexing the LRUs.
#
# Note that we only process raw ascii bytes as string for the moment and not
# UTF-16 characters.
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

    # Method returning a node
    def __node(self, **kwargs):
        return LRUTrieNode(self.storage, **kwargs)

    # Method returning root node
    def __root(self):
        return self.__node(block=0)

    # Method ensuring that a sibling with the desired char exists
    def __require_char_from_siblings(self, node, char):

        # If the node does not exist, we create it
        if not node.exists:
            node.set_char(char)
            node.write()
            return node

        # Else we follow the siblings until we find a relevant one
        while True:
            if node.char() == char:
                return node

            if node.has_next():
                node.read_next()
            else:
                break

        # We did not find a relevant sibling, let's add it
        sibling = self.__node(char=char)
        sibling.write()

        node.set_next(sibling.block)
        node.write()

        return sibling

    # =========================================================================
    # Mutation methods
    # =========================================================================

    # Method adding a page to the trie
    def add_page(self, lru):

        l = len(lru)

        node = self.__root()
        parent_node = None

        # Iterating over the lru's characters
        for i in range(l):
            char = ord(lru[i])

            node = self.__require_char_from_siblings(node, char)

            # Need to link a created child to the parent?
            # TODO: this part can probably be rewritten to better write data
            if parent_node:
                node.set_parent(parent_node.block)
                node.write()
                parent_node.set_child(node.block)
                parent_node.write()

            # Following up through the child
            if i < l - 1:
                if node.has_child():
                    parent_node = None
                    node.read_child()
                else:
                    parent_node = node
                    node = self.__node()

        # Flagging the node as a page
        node.flag_as_page()
        node.write()

    # =========================================================================
    # Iteration methods
    # =========================================================================
    def nodes_iter(self):
        node = self.__root()

        while node.exists:
            yield node
            node.read(block=node.block + 1)

    def dfs_iter(self):
        node = self.__root()

        if not node.exists:
            return

        descending = True
        lru = ''

        while True:

            # When descending, we yield the node
            if descending:
                yield node, lru + node.char_as_str()

            # Descending to the child
            if descending and node.has_child():
                descending = True
                lru = lru + node.char_as_str()
                node.read_child()
                continue

            # Following next sibling
            if node.has_next():
                descending = True
                node.read_next()
                continue

            # Ascending to the parent again
            if not node.is_root():
                descending = False
                lru = lru[:-1]
                node.read_parent()
                continue

            return

    def pages_iter(self):
        for node, lru in self.dfs_iter():
            if node.is_page():
                yield lru
