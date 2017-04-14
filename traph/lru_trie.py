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
            if parent_node:
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
    def pages_iter(self):
        stack = [(self.__root(), '')]

        while len(stack):
            node, lru = stack.pop()

            if node.is_page():
                yield lru + node.char_as_str()

            if node.has_child():
                stack.append((node.child_node(), lru + node.char_as_str()))

            if node.has_next():
                stack.append((node.next_node(), lru + node.char_as_str()))

    # =========================================================================
    # Debug methods
    # =========================================================================
    def log(self):

        stack = [(self.__root(), 0)]

        while len(stack):
            node, level = stack.pop()
            print '-' * level, node.char_as_str()

            if node.has_next():
                stack.append((node.next_node(), level))

            if node.has_child():
                stack.append((node.child_node(), level + 1))
