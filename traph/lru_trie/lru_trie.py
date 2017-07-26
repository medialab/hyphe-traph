# =============================================================================
# LRU Trie Class
# =============================================================================
#
# Class representing the Trie indexing the LRUs.
#
import warnings
from traph.lru_trie.node import LRUTrieNode, LRU_TRIE_FIRST_DATA_BLOCK
from traph.lru_trie.header import LRUTrieHeader
from traph.lru_trie.iteration_state import LRUTrieDetailedDFSIterationState
from traph.lru_trie.walk_history import LRUTrieWalkHistory


# Main class
class LRUTrie(object):

    # =========================================================================
    # Constructor
    # =========================================================================
    def __init__(self, storage, encoding='utf-8'):

        # Properties
        self.storage = storage
        self.encoding = encoding

        # Readin headers
        self.header = LRUTrieHeader(storage)

    # =========================================================================
    # Debug
    # =========================================================================
    def representation(self):

        string = ''

        for state in self.detailed_dfs_iter():
            if state.direction == 'down':
                node = state.node
                string += node.char_as_str()

            if state.direction == 'right':
                string += '\n'
                string += (len(state.lru.decode(self.encoding, 'replace')) - 1) * '-' + state.lru[-1]

        return string

    # =========================================================================
    # Internal methods
    # =========================================================================

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
        sibling = self.node(char=char)

        # The new sibling's parent is the same, obviously
        sibling.set_parent(node.parent())
        sibling.write()

        node.set_next(sibling.block)
        node.write()

        return sibling

    # =========================================================================
    # Mutation methods
    # =========================================================================

    # Method adding a lru to the trie
    def add_lru(self, lru):

        # Iteration state
        l = len(lru)
        i = 0
        history = LRUTrieWalkHistory(lru)
        node = self.root()

        # Descending the trie
        while i < l:
            char = ord(lru[i])

            node = self.__ensure_char_from_siblings(node, char)

            # Tracking webentities
            if node.has_webentity():
                history.update_webentity(
                    node.webentity(),
                    lru[:i],
                    i
                )

            # Tracking webentity creation rules
            if node.has_webentity_creation_rule():
                history.add_webentity_creation_rule(i)

            i += 1

            if i < l and node.has_child():
                node.read_child()
            else:
                break

        # We went as far as possible, now we add the missing part
        while i < l:
            char = ord(lru[i])

            # Creating the child
            child = self.node(char=char)
            child.set_parent(node.block)
            child.write()

            # Linking the child to its parent
            node.set_child(child.block)
            node.write()

            node = child
            i += 1

        return node, history

    # Method adding a page to the trie
    def add_page(self, lru):
        node, history = self.add_lru(lru)

        # Flagging the node as a page
        if not node.is_page():
            node.flag_as_page()
            node.write()
            history.page_was_created = True

        return node, history

    # =========================================================================
    # Read methods
    # =========================================================================

    # Method returning a node
    def node(self, **kwargs):
        return LRUTrieNode(self.storage, **kwargs)

    # Method returning root node
    def root(self):
        return self.node(block=LRU_TRIE_FIRST_DATA_BLOCK)

    def lru_node(self, lru):
        node = self.root()

        l = len(lru)

        for i in range(l):
            char = ord(lru[i])

            while node.char() != char:
                if not node.has_next():
                    return
                node.read_next()

            if i < l - 1:
                if not node.has_child():
                    return
                else:
                    node.read_child()

        return node

    def follow_lru(self, lru):
        # Does almost the same thing as lru_node but with a history,
        # and thus less efficient.
        # Very similar to add_lru too, but returns False if lru not in Trie

        node = self.root()
        history = LRUTrieWalkHistory(lru)

        l = len(lru)

        for i in range(l):
            char = ord(lru[i])

            while node.char() != char:
                if not node.has_next():
                    return None, history
                node.read_next()

            if node.has_webentity():
                history.update_webentity(
                    node.webentity(),

                    # TODO: this should become useless with a getter method
                    lru[:i + 1],
                    i
                )

            if node.has_webentity_creation_rule():
                history.add_webentity_creation_rule(i)

            if i < l - 1:
                if not node.has_child():
                    return None, history
                else:
                    node.read_child()

        return node, history

    def windup_lru(self, block):
        # TODO: check block
        node = self.node(block=block)

        lru = node.char_as_str()

        for parent in self.node_parents_iter(node):
            lru = parent.char_as_str() + lru

        return lru

    def windup_lru_for_webentity(self, node):
        if node.has_webentity():
            return node.webentity()

        for parent in self.node_parents_iter(node):
            if parent.has_webentity():
                return parent.webentity()

        # We could not find a webentity for the given node, we should warn
        warnings.warn(
            'Could not find a webentity for the given node %s!' % node.__repr__(),
            RuntimeWarning
        )

        return None

    # =========================================================================
    # Iteration methods
    # =========================================================================
    def nodes_iter(self):
        node = self.root()

        while node.exists:
            yield node
            node.read(node.block + self.storage.block_size)

    def node_parents_iter(self, node):

        # TODO: block
        if node.is_root():
            return

        parent = node.parent_node()

        yield parent

        while not parent.is_root():
            parent.read_parent()
            yield parent

    def node_siblings_iter(self, node):

        # TODO: block
        if not node.has_next():
            return

        sibling = node.next_node()

        yield sibling

        while sibling.has_next():
            sibling.read_next()
            yield sibling

    def dfs_iter(self, starting_node=False, starting_lru=False):
        # Note: if starting_node is set, starting_lru must be too
        if starting_node:
            node = starting_node
            starting_block = starting_node.block
            lru = starting_lru[:-1]
            # Note: unsure why we need to trim rule_prefix above, but it seems to work
        else:
            node = self.root()
            starting_block = node.block
            lru = ''

        # If there is no root node, we can stop right there
        if not node.exists:
            return

        descending = True

        while True:

            # When descending, we yield
            if descending:
                yield node, lru + node.char_as_str()

            # If we have a child, we descend
            if descending and node.has_child():
                lru = lru + node.char_as_str()
                node.read_child()
                continue

            # Do we need to stop?
            if node.block == starting_block:
                break

            # If we have no child, we follow the next sibling
            if node.has_next():
                descending = True
                node.read_next()
                continue

            # Else we bubble up
            descending = False
            lru = lru[:-1]
            node.read_parent()

    def webentity_dfs_iter(self, weid, starting_node, starting_lru):
        '''
        Note that this algorithm will peruse the webentity nodes only for the
        given prefix. We would need a refined algorithm for the cases when
        then prefixes are not given and we need to peruse the webentity's
        whole realm.
        '''
        node = starting_node
        starting_block = starting_node.block
        lru = starting_lru[:-1]
        # Note: unsure why we need to trim rule_prefix above, but it seems to work

        # If there is no starting node, we can stop right there
        if not node.exists:
            return

        descending = True

        while True:

            # When descending, we yield
            if descending:
                yield node, lru + node.char_as_str()

            # If we have a VALID child, we descend
            if descending and node.has_child():
                child_node = node.child_node()

                if not child_node.has_webentity():
                    lru = lru + node.char_as_str()
                    node = child_node
                    continue

            # Do we need to stop?
            if node.block == starting_block:
                break

            # If we have no child, we follow the next VALID sibling
            valid_next = False
            while node.has_next() and not valid_next:
                node.read_next()
                if node.has_webentity():
                    continue
                else:
                    valid_next = True

            if valid_next:
                descending = True
                continue

            # Else we bubble up
            descending = False
            lru = lru[:-1]
            node.read_parent()

    def detailed_dfs_iter(self):
        node = self.root()
        state = LRUTrieDetailedDFSIterationState(node)

        starting_block = node.block

        # If there is no root node, we can stop right there
        if not node.exists:
            return

        descending = True

        while True:

            # When descending, we yield
            if descending:
                state.lru += node.char_as_str()

                webentity = node.webentity()

                if webentity:
                    state.webentities.append(webentity)

                yield state
                # TODO: yield in next condition rather (also in DFS)
                state.lru = state.lru[:-1]

            # If we have a child, we descend
            if descending and node.has_child():
                state.lru += node.char_as_str()
                state.last_block = node.block
                state.direction = 'down'

                node.read_child()
                continue

            # Do we need to stop?
            if node.block == starting_block:
                break

            # If we have no child, we follow the next sibling
            if node.has_next():
                descending = True
                state.last_block = node.block
                state.direction = 'right'

                webentity = node.webentity()

                if webentity and webentity == state.current_webentity():
                    state.webentities.pop()

                node.read_next()

                continue

            # Else we bubble up
            state.lru = state.lru[:-1]
            descending = False
            state.last_block = node.block

            webentity = node.webentity()

            if webentity and webentity == state.current_webentity():
                state.webentities.pop()

            node.read_parent()

    def lean_detailed_dfs_iter(self):
        node = self.root()

        # TODO: use a degraded version of the iteration state
        state = LRUTrieDetailedDFSIterationState(node)

        starting_block = node.block

        # If there is no root node, we can stop right there
        if not node.exists:
            return

        descending = True

        while True:

            # When descending, we yield
            if descending:
                webentity = node.webentity()

                if webentity:
                    state.webentities.append(webentity)

                yield state

            # If we have a child, we descend
            if descending and node.has_child():
                node.read_child()
                continue

            # Do we need to stop?
            if node.block == starting_block:
                break

            # If we have no child, we follow the next sibling
            if node.has_next():
                descending = True

                webentity = node.webentity()

                if webentity and webentity == state.current_webentity():
                    state.webentities.pop()

                node.read_next()

                continue

            # Else we bubble up
            descending = False
            webentity = node.webentity()

            if webentity and webentity == state.current_webentity():
                state.webentities.pop()

            node.read_parent()

    def pages_iter(self):
        for node, lru in self.dfs_iter():
            if node.is_page():
                yield node, lru

    def webentity_prefix_iter(self):
        for node, lru in self.dfs_iter():
            if node.has_webentity():
                yield node, lru

    # =========================================================================
    # Counting methods
    # =========================================================================
    def count_pages(self):
        nb = 0

        # Here we don't need a DFS so we can plainly iterate over the nodes
        for node in self.nodes_iter():
            if node.is_page():
                nb += 1

        return nb
