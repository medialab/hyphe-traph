# =============================================================================
# LRU Trie Class
# =============================================================================
#
# Class representing the Trie indexing the LRUs.
#
import warnings
from collections import Counter
from traph.helpers import lru_iter, lru_dirname
from traph.lru_trie.node import LRUTrieNode, LRU_TRIE_FIRST_DATA_BLOCK, LRU_TRIE_STEM_SIZE
from traph.lru_trie.header import LRUTrieHeader
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
            current_stem = node.stem()

            if current_stem == stem:
                return node

            # Searching the BST
            if stem < current_stem:
                if node.has_left():
                    node.read_left()
                else:
                    break
            else:
                if node.has_right():
                    node.read_right()
                else:
                    break

        # We did not find a relevant sibling, let's add it
        sibling = self.node(stem=stem)

        # The new sibling's parent is the same, obviously
        sibling.set_parent(node.parent())
        sibling.write()

        if stem < node.stem():
            node.set_left(sibling.block)
        else:
            node.set_right(sibling.block)

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
    def add_page(self, lru, crawled=False):
        node, history = self.add_lru(lru)

        # Flagging the node as a page
        if not node.is_page():
            node.flag_as_page()

            if crawled:
                node.flag_as_crawled()

            node.write()
            history.page_was_created = True

        elif crawled and not node.is_crawled():
            node.flag_as_crawled()

            node.write()

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

            while True:
                current_stem = node.stem()

                if current_stem == stem:
                    break

                if stem < current_stem:
                    if node.has_left():
                        node.read_left()
                    else:
                        return
                else:
                    if node.has_right():
                        node.read_right()
                    else:
                        return

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

            while True:
                current_stem = node.stem()

                if current_stem == stem:
                    break

                if stem < current_stem:
                    if node.has_left():
                        node.read_left()
                    else:
                        return None, history
                else:
                    if node.has_right():
                        node.read_right()
                    else:
                        return None, history

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

        lru = node.stem()

        for parent in self.node_parents_iter(node):
            lru = parent.stem() + lru

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
        if not node.has_parent():
            return

        parent = node.parent_node()

        yield parent

        while parent.has_parent():
            parent.read_parent()
            yield parent

    def dfs_iter(self, starting_node=None, starting_lru=''):
        starting_from_root = not starting_node

        if starting_node:
            starting_block = starting_node.block
            starting_lru = lru_dirname(starting_lru)
        else:
            starting_node = self.root()
            starting_block = self.root().block

        # If there is no starting node, there is no point in doing a DFS
        if not starting_node.exists:
            return

        stack = [(starting_block, starting_lru)]
        node = self.node()

        while len(stack):
            block, lru = stack.pop()
            node.read(block)

            current_lru = lru + node.stem()

            yield node, current_lru

            if starting_from_root or block != starting_block:
                if node.has_right():
                    stack.append((node.right(), lru))

                if node.has_left():
                    stack.append((node.left(), lru))

            if node.has_child():
                stack.append((node.child(), current_lru))

    def webentity_dfs_iter(self, starting_node, starting_lru, max_depth=None):
        '''
        Note that this algorithm will peruse the webentity nodes only for the
        given prefix. We would need a refined algorithm for the cases when
        then prefixes are not given and we need to peruse the webentity's
        whole realm.
        '''
        starting_block = starting_node.block
        starting_lru = lru_dirname(starting_lru)

        # If there is no starting node, there is no point in doing a DFS
        if not starting_node.exists:
            return

        stack = [(starting_block, starting_lru, 0)]
        node = self.node()

        while len(stack):
            block, lru, level = stack.pop()
            node.read(block)

            relevant_node = block == starting_block or not node.has_webentity()
            current_lru = lru + node.stem()

            if relevant_node:
                yield node, current_lru

            # Following siblings
            if block != starting_block:
                if node.has_right():
                    stack.append((node.right(), lru, level))

                if node.has_left():
                    stack.append((node.left(), lru, level))

            # Following child
            if relevant_node and node.has_child():
                if max_depth is not None and level >= max_depth:
                    continue

                stack.append((node.child(), current_lru, level + 1))

    def webentity_inorder_iter(self, starting_node, starting_lru,
                               pagination_node=None, pagination_path=None):

        starting_lru = lru_dirname(starting_lru)
        pagination_stack = []

        if pagination_node is not None:
            assert pagination_path is not None

            # Here we need to build back a stack of ids and lrus
            node = starting_node

            for op in pagination_path:
                if op == 'l':
                    node = node.left_node()
                elif op == 'r':
                    node = node.right_node()
                else:
                    node = node.child_node()

                # TODO: can do better than windup here...
                pagination_stack.append((node, lru_dirname(self.windup_lru(node.block)), op))

        def inorder_traversal(node, lru, path='', last_op=None):

            if node.block != starting_node.block:
                if last_op != 'l' and node.has_left():
                    for item in inorder_traversal(node.left_node(), lru, path + 'l'):
                        yield item

            current_lru = lru + node.stem()
            relevant_node = node.block == starting_node.block or not node.has_webentity()

            if relevant_node:
                if pagination_node is None or node.block != pagination_node.block:
                    yield node, current_lru

                if last_op != 'c' and node.has_child():
                    for item in inorder_traversal(node.child_node(), current_lru, path + 'c'):
                        yield item

            if node.block != starting_node.block:
                if last_op is None and node.has_right():
                    for item in inorder_traversal(node.right_node(), lru, path + 'r'):
                        yield item

            if len(pagination_stack) != 0:
                last_node, last_lru, last_op = pagination_stack.pop()

                for item in inorder_traversal(last_node, last_lru, path[:-1], last_op):
                    yield item

        if pagination_node is not None:
            generator = inorder_traversal(
                pagination_node,
                pagination_stack[-1][1],
                pagination_path
            )
        else:
            generator = inorder_traversal(
                starting_node,
                starting_lru
            )

        for item in generator:
            yield item

    def dfs_with_webentity_iter(self):
        starting_node = self.root()
        starting_block = self.root().block

        # If there is no starting node, there is no point in doing a DFS
        if not starting_node.exists:
            return

        stack = [(starting_block, None)]
        node = self.node()

        while len(stack):
            block, webentity = stack.pop()
            node.read(block)

            current_webentity = webentity

            if node.has_webentity():
                current_webentity = node.webentity()

            yield node, current_webentity

            if node.has_right():
                stack.append((node.right(), webentity))

            if node.has_left():
                stack.append((node.left(), webentity))

            if node.has_child():
                stack.append((node.child(), current_webentity))

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

    def count_crawled_pages(self):
        nb = 0

        # Here we don't need a DFS so we can plainly iterate over the nodes
        for node in self.nodes_iter():
            if node.is_page() and node.is_crawled():
                nb += 1

        return nb

    def metrics(self):
        stats = {
            'nb_nodes': 0,
            'nb_pages': 0,
            'nb_crawled_pages': 0,
            'nb_tail_nodes': 0,
            'nb_fragmented_nodes': 0,
            'nb_stems': 0,
            'avg_stem_filling': 0,
            'max_tail': 0,
            'avg_tail': 0
        }

        current_tail_size = 0
        last_tail_size = 0

        for node in self.nodes_iter():
            stats['nb_nodes'] += 1

            if node.is_page():
                stats['nb_pages'] += 1

                if node.is_crawled():
                    stats['nb_crawled_pages'] += 1

            if node.has_tail():
                stats['nb_fragmented_nodes'] += 1

            if node.is_tail():
                stats['nb_tail_nodes'] += 1
                current_tail_size += 1

                if current_tail_size > stats['max_tail']:
                    stats['max_tail'] = current_tail_size

                last_tail_size = current_tail_size
            else:
                current_tail_size = 0
                filling = len(node.stem()) / float(LRU_TRIE_STEM_SIZE)

                stats['nb_stems'] += 1
                stats['avg_stem_filling'] = (
                    stats['avg_stem_filling'] +
                    (
                        (filling - stats['avg_stem_filling']) /
                        float(stats['nb_stems'])
                    )
                )

                if last_tail_size:
                    stats['avg_tail'] = (
                        stats['avg_tail'] + (
                            (last_tail_size - stats['avg_tail']) /
                            float(stats['nb_fragmented_nodes'])
                        )
                    )

                    last_tail_size = 0

        stats['prop_fragmented_stems'] = (
            stats['nb_fragmented_nodes'] / float(stats['nb_stems'])
        )

        return stats

    def bst_stats(self):
        stems_index = {}
        bst_index = Counter()

        for node in self.nodes_iter():
            parent_block = node.parent()
            parent_stem = stems_index.get(parent_block, '')

            stems_index[node.block] = parent_stem + node.stem()
            bst_index[parent_block] += 1

        return stems_index, bst_index
