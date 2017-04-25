# =============================================================================
# LRU Trie Class
# =============================================================================
#
# Class representing the Trie indexing the LRUs.
#
# Note that we only process raw ascii bytes as string for the moment and not
# UTF-16 characters.
#
from lru_trie_node import LRUTrieNode, LRU_TRIE_NODE_HEADER_BLOCKS


class LRUTrie(object):

    # =========================================================================
    # Constructor
    # =========================================================================
    def __init__(self, storage):

        # Properties
        self.storage = storage

        # Ensuring headers are written
        self.__ensure_headers()

    # =========================================================================
    # Internal methods
    # =========================================================================

    # Method returning a node
    def __node(self, **kwargs):
        return LRUTrieNode(self.storage, **kwargs)

    # Method returning root node
    def __root(self):
        return self.__node(block=LRU_TRIE_NODE_HEADER_BLOCKS)

    # Method ensuring we wrote the headers
    def __ensure_headers(self):
        header_block = 0

        while header_block < LRU_TRIE_NODE_HEADER_BLOCKS:
            header_node = self.__node(block=header_block)

            if not header_node.exists:
                header_node.write()

            header_block += 1


    # Method ensuring that a sibling with the desired char exists
    def __ensure_char_from_siblings(self, node, char):

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

        # The new sibling's parent is the same, obviously
        sibling.set_parent(node.parent())
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

        # Iterating over the lru's characters
        for i in range(l):
            char = ord(lru[i])

            node = self.__ensure_char_from_siblings(node, char)

            # Following up through the child
            if i < l - 1:
                if node.has_child():
                    node.read_child()
                else:
                    parent_node = node
                    node = self.__node(char=ord(lru[i + 1]))
                    node.set_parent(parent_node.block)
                    node.write()
                    parent_node.set_child(node.block)
                    parent_node.write()

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
            node.read(node.block + 1)

    def node_siblings_iter(self, node):
        if not node.has_next():
            return

        sibling = node.next_node()

        yield sibling

        while sibling.has_next():
            sibling.read_next()
            yield sibling

    def dfs_iter(self):
        node = self.__root()

        # If there is no root node, we can stop right there
        if not node.exists:
            return

        descending = True
        lru = ''

        while True:

            # When descending, we yield
            if descending:
                yield node, lru + node.char_as_str()

            # If we have a child, we descend
            if descending and node.has_child():
                descending = True
                lru = lru + node.char_as_str()
                node.read_child()
                continue

            # If we have no child, we follow the next sibling
            if node.has_next():
                descending = True
                node.read_next()
                continue

            # Else we bubble up
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
