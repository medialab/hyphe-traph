# =============================================================================
# LRU Trie Class
# =============================================================================
#
# Class representing the Trie indexing the LRUs.
#
import warnings
from traph.helpers import lru_iter
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

        # Reading headers
        self.header = LRUTrieHeader(storage)

    # =========================================================================
    # Debug
    # =========================================================================
    def representation(self):
        '''
        NOTE: deprecated, need to fix!
        '''

        string = ''

        for state in self.detailed_dfs_iter():
            if state.direction == 'down':
                node = state.node
                string += node.stem_as_str()

            if state.direction == 'right':
                string += '\n'
                string += (len(state.lru.decode(self.encoding, 'replace')) - 1) * '-' + state.lru[-1]

        return string

    # =========================================================================
    # Internal methods
    # =========================================================================

    # Method ensuring that a sibling with the desired char exists
    def __ensure_stem_from_siblings(self, node, stem):

        # If the node does not exist, we create it
        if not node.exists:
            node.set_stem(stem)
            node.write()
            return node

        # Else we follow the siblings until we find a relevant one
        while True:
            if node.stem() == stem:
                return node

            if node.has_next():
                node.read_next()
            else:
                break

        # We did not find a relevant sibling, let's add it
        sibling = self.node(stem=stem)

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
        # TODO: we should be able to use an iterator and not keep a list!
        stems = list(lru_iter(lru))
        l = len(stems)
        i = 0
        history = LRUTrieWalkHistory(lru)
        node = self.root()
        lru = ''

        # Descending the trie
        while i < l:
            stem = stems[i]
            lru += stem

            node = self.__ensure_stem_from_siblings(node, stem)

            # Tracking webentities
            if node.has_webentity():
                history.update_webentity(
                    node.webentity(),
                    lru,
                    len(lru)
                )

            # Tracking webentity creation rules
            if node.has_webentity_creation_rule():
                history.add_webentity_creation_rule(len(lru))

            i += 1

            if i < l and node.has_child():
                node.read_child()
            else:
                break

        # We went as far as possible, now we add the missing part
        while i < l:
            stem = stems[i]

            # Creating the child
            child = self.node(stem=stem)
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

        stems = list(lru_iter(lru))
        l = len(stems)

        for i in range(l):
            stem = stems[i]

            while node.stem() != stem:
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

        stems = list(lru_iter(lru))
        lru = ''
        l = len(stems)

        for i in range(l):
            stem = stems[i]
            lru += stem

            while node.stem() != stem:
                if not node.has_next():
                    return None, history
                node.read_next()

            if node.has_webentity():
                history.update_webentity(
                    node.webentity(),
                    lru,
                    len(lru)
                )

            if node.has_webentity_creation_rule():
                history.add_webentity_creation_rule(len(lru))

            if i < l - 1:
                if not node.has_child():
                    return None, history
                else:
                    node.read_child()

        return node, history

    def windup_lru(self, block):
        # TODO: check block
        node = self.node(block=block)

        lru = node.stem_as_str()

        for parent in self.node_parents_iter(node):
            lru = parent.stem_as_str() + lru

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
            lru = list(lru_iter(starting_lru))[:-1]
            # Note: unsure why we need to trim rule_prefix above, but it seems to work
        else:
            node = self.root()
            starting_block = None
            lru = []

        # If there is no root node, we can stop right there
        if not node.exists:
            return

        descending = True

        while True:

            # When descending, we yield
            if descending:
                yield node, ''.join(lru + [node.stem_as_str()])

            # If we have a child, we descend
            if descending and node.has_child():
                lru.append(node.stem_as_str())
                node.read_child()
                continue

            # Stopping the traversal when we have a starting block
            if node.block == starting_block:
                break

            # If we have no child, we follow the next sibling
            if node.has_next():
                descending = True
                node.read_next()
                continue

            # Stopping the traversal when performing a full DFS
            if not node.has_parent():
                break

            # Else we bubble up
            descending = False
            lru.pop()
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
        lru = list(lru_iter(starting_lru))[:-1]
        # Note: unsure why we need to trim rule_prefix above, but it seems to work

        # If there is no starting node, we can stop right there
        if not node.exists:
            return

        descending = True

        while True:

            # When descending, we yield
            if descending:
                yield node, ''.join(lru + [node.stem_as_str()])

            # If we have a VALID child, we descend
            if descending and node.has_child():
                child_node = node.child_node()

                if not child_node.has_webentity():
                    lru.append(node.stem_as_str())
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
            lru.pop()
            node.read_parent()

    def detailed_dfs_iter(self):
        node = self.root()
        state = LRUTrieDetailedDFSIterationState(node)

        # If there is no root node, we can stop right there
        if not node.exists:
            return

        descending = True

        while True:

            # When descending, we yield
            if descending:
                state.lru += node.stem_as_str()

                webentity = node.webentity()

                if webentity:
                    state.webentities.append(webentity)

                yield state
                # TODO: yield in next condition rather (also in DFS)
                state.lru = state.lru[:-1]

            # If we have a child, we descend
            if descending and node.has_child():
                state.lru += node.stem_as_str()
                state.last_block = node.block
                state.direction = 'down'

                node.read_child()
                continue

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

            # Do we need to stop?
            if not node.has_parent():
                break

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

            # If we have no child, we follow the next sibling
            if node.has_next():
                descending = True

                webentity = node.webentity()

                if webentity and webentity == state.current_webentity():
                    state.webentities.pop()

                node.read_next()

                continue

            # Do we need to stop?
            if not node.has_parent():
                break

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
